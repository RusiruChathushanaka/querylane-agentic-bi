import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import vm from "node:vm";
import ts from "typescript";

function voiceHarness(options, behavior = {}) {
  const track = { enabled: true, stop() { effects.tracksStopped++; } };
  const effects = {
    buffers: 0,
    tracksStopped: 0,
    contextsClosed: 0,
    microphoneRequests: 0,
    frames: [],
    closed: 0,
    events: [],
    mutedAtConnect: null,
    socket: null,
  };
  class AudioContext {
    currentTime = 0;
    destination = {};
    async resume() {}
    async close() { effects.contextsClosed++; }
    createBuffer() {
      effects.buffers++;
      return { getChannelData: () => new Float32Array(1), duration: 1 / 24000 };
    }
    createBufferSource() {
      return { connect() {}, start() {}, stop() {} };
    }
  }
  class Socket {
    static OPEN = 1;
    readyState = 1;
    constructor(url) {
      effects.url = url.href;
      effects.mutedAtConnect = !track.enabled;
      effects.socket = this;
    }
    send(data) { effects.frames.push(JSON.parse(data)); }
    close() { effects.closed++; }
  }
  const compiledModule = { exports: {} };
  const context = {
    module: compiledModule,
    exports: compiledModule.exports,
    require: () => ({
      backendUrl: async () => "http://localhost:8000",
      guestToken: async () => "test-guest",
    }),
    navigator: {
      mediaDevices: {
        getUserMedia: async () => {
          effects.microphoneRequests++;
          if (behavior.denyMicrophone) throw new Error("Microphone permission denied");
          if (behavior.waitForPermission) await behavior.waitForPermission;
          return { getTracks: () => [track], getAudioTracks: () => [track] };
        },
      },
    },
    window: { AudioWorkletNode: class {} },
    AudioContext,
    WebSocket: Socket,
    URL,
    atob,
    setTimeout,
    clearTimeout,
  };
  const source = readFileSync(
    resolve(import.meta.dirname, "../src/lib/voice.ts"),
    "utf8",
  );
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2022,
    },
  });
  vm.runInNewContext(outputText, context);
  const voice = new compiledModule.exports.LiveVoice(
    (event) => effects.events.push(event),
    () => {},
    options,
  );
  return { voice, effects, track };
}

test("start-muted disables microphone tracks before connecting and still permits manual unmute", async () => {
  const { voice, effects, track } = voiceHarness({ startMuted: true });
  await voice.start("test-conversation");
  assert.equal(effects.mutedAtConnect, true);
  assert.equal(track.enabled, false);
  assert.equal(voice.toggleMute(), false);
  assert.equal(track.enabled, true);
  voice.stop();
});

test("silent responses skip speaker playback but preserve incoming transcripts", async () => {
  const { voice, effects } = voiceHarness({ spokenResponses: false });
  await voice.start("test-conversation");
  await effects.socket.onmessage({
    data: JSON.stringify({ type: "audio", data: "AAAA" }),
  });
  await effects.socket.onmessage({
    data: JSON.stringify({ type: "transcript", text: "Revenue increased." }),
  });
  assert.equal(effects.buffers, 0);
  assert.ok(
    effects.events.some(
      (event) =>
        event.type === "transcript" && event.text === "Revenue increased.",
    ),
  );
  voice.stop();
});

test("default voice preferences preserve audible responses and an enabled microphone", async () => {
  const { voice, effects, track } = voiceHarness();
  await voice.start("test-conversation");
  assert.equal(track.enabled, true);
  await effects.socket.onmessage({
    data: JSON.stringify({ type: "audio", data: "AAAA" }),
  });
  assert.equal(effects.buffers, 1);
  voice.stop();
});

test("typing interview uses author endpoint and text frames without requesting microphone access", async () => {
  const { voice, effects } = voiceHarness({ textOnly: true, endpoint: "/api/v1/skills/author-sessions/example/voice" });
  await voice.start("example");
  assert.equal(effects.microphoneRequests, 0);
  assert.equal(effects.url, "ws://localhost:8000/api/v1/skills/author-sessions/example/voice");
  assert.equal(voice.sendText("Revenue"), false);
  await effects.socket.onmessage({ data: JSON.stringify({ type: "ready" }) });
  assert.equal(voice.sendText("Revenue"), true);
  assert.deepEqual(effects.frames.at(-1), { type: "text", text: "Revenue" });
  voice.stop();
});

test("microphone denial closes the playback context before surfacing the error", async () => {
  const { voice, effects } = voiceHarness({}, { denyMicrophone: true });
  await assert.rejects(voice.start("example"), /permission denied/);
  assert.equal(effects.contextsClosed, 1);
  assert.equal(effects.socket, null);
});

test("closing while permission is pending stops late microphone tracks and never connects", async () => {
  let allow;
  const permission = new Promise((resolve) => { allow = resolve; });
  const { voice, effects } = voiceHarness({}, { waitForPermission: permission });
  const start = voice.start("example");
  await Promise.resolve();
  voice.stop(); allow(); await start;
  assert.equal(effects.tracksStopped, 1);
  assert.equal(effects.contextsClosed, 1);
  assert.equal(effects.socket, null);
});

test("graceful pause accepts the final server draft while releasing audio immediately", async () => {
  const { voice, effects } = voiceHarness({ textOnly: true });
  await voice.start("example");
  await effects.socket.onmessage({ data: JSON.stringify({ type: "ready" }) });
  voice.stop(true);
  assert.equal(effects.contextsClosed, 1);
  assert.equal(effects.closed, 0);
  assert.equal(effects.frames.at(-1).type, "stop");
  await effects.socket.onmessage({ data: JSON.stringify({ type: "stopped", session: { revision: 3 } }) });
  effects.socket.onclose();
  assert.equal(effects.events.find((event) => event.session)?.session.revision, 3);
  voice.stop();
  assert.equal(effects.contextsClosed, 1);
});

test("interruption clears queued spoken audio without ending the interview", async () => {
  const { voice, effects } = voiceHarness({ textOnly: true });
  await voice.start("example");
  await effects.socket.onmessage({ data: JSON.stringify({ type: "ready" }) });
  await effects.socket.onmessage({ data: JSON.stringify({ type: "audio", data: "AAAA" }) });
  await effects.socket.onmessage({ data: JSON.stringify({ type: "interrupted" }) });
  assert.equal(effects.buffers, 1);
  assert.equal(effects.closed, 0);
  assert.equal(voice.sendText("Please correct the definition"), true);
  voice.stop();
});

test("analysis model is included in the analyst voice handshake", async () => {
  const harness = voiceHarness({ textOnly: true, analysisModel: "gemini-3.5-flash-lite" });
  await harness.voice.start("chat");
  harness.effects.socket.onopen();
  assert.equal(harness.effects.frames[0].model, "gemini-3.5-flash-lite");
  harness.voice.stop();
});

test('malformed server frames fail safely and release audio rather than rejecting the handler', async () => {
  const {voice,effects}=voiceHarness({textOnly:true});
  await voice.start('chat');
  await effects.socket.onmessage({data:'{broken'});
  assert.equal(effects.closed,1);
  assert.ok(effects.events.some(e=>e.type==='error'));
});

test('late ready after stop cannot reactivate a closed voice UI', async () => {
  const {voice,effects}=voiceHarness({textOnly:true});
  await voice.start('chat');voice.stop();
  await effects.socket.onmessage({data:JSON.stringify({type:'ready'})});
  assert.ok(!effects.events.some(e=>e.type==='ready'));
});
