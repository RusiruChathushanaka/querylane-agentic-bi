import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import vm from "node:vm";
import ts from "typescript";

function voiceHarness(options) {
  const track = { enabled: true, stop() {} };
  const effects = {
    buffers: 0,
    events: [],
    mutedAtConnect: null,
    socket: null,
  };
  class AudioContext {
    currentTime = 0;
    destination = {};
    async resume() {}
    async close() {}
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
    constructor() {
      effects.mutedAtConnect = !track.enabled;
      effects.socket = this;
    }
    send() {}
    close() {}
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
        getUserMedia: async () => ({
          getTracks: () => [track],
          getAudioTracks: () => [track],
        }),
      },
    },
    window: { AudioWorkletNode: class {} },
    AudioContext,
    WebSocket: Socket,
    URL,
    atob,
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
