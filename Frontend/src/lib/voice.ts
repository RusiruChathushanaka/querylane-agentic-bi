import { backendUrl, guestToken } from "./api";

export type VoiceEvent = { type: string; [key: string]: unknown };

export class LiveVoice {
  private socket?: WebSocket;
  private microphone?: MediaStream;
  private capture?: AudioContext;
  private playback?: AudioContext;
  private worklet?: AudioWorkletNode;
  private playing = new Set<AudioBufferSourceNode>();
  private nextStart = 0;
  private closed = false;
  private ready = false;
  private muted = false;
  private closeTimer?: ReturnType<typeof setTimeout>;
  private connectionTimer?: ReturnType<typeof setTimeout>;

  constructor(
    private onEvent: (event: VoiceEvent) => void,
    private onLevel: (level: number) => void,
    private options: {
      spokenResponses?: boolean;
      startMuted?: boolean;
      endpoint?: string;
      textOnly?: boolean;
      analysisModel?: string;
    } = {},
  ) {
    this.muted = options.startMuted ?? false;
  }

  async start(conversationId: string) {
    try {
      await this.connect(conversationId);
    } catch (error) {
      this.stop();
      throw error;
    }
  }

  private async connect(conversationId: string) {
    if (
      !this.options.textOnly &&
      (!navigator.mediaDevices?.getUserMedia || !window.AudioWorkletNode)
    )
      throw new Error(
        "This browser cannot stream microphone audio. Use an up-to-date browser over HTTPS.",
      );
    if (typeof AudioContext !== "undefined") {
      this.playback = new AudioContext({ sampleRate: 24000 });
      await this.playback.resume();
    }
    if (!this.options.textOnly)
      this.microphone = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
    if (this.closed) {
      this.microphone?.getTracks().forEach((track) => track.stop());
      return;
    }
    this.microphone?.getAudioTracks().forEach((track) => {
      track.enabled = !this.muted;
    });
    const base = await backendUrl();
    const token = await guestToken();
    if (this.closed) return;
    const url = new URL(
      `${base}${this.options.endpoint ?? `/api/v1/conversations/${conversationId}/voice`}`,
    );
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(url);
    this.socket = socket;
    this.connectionTimer = setTimeout(() => {
      this.onEvent({
        type: "error",
        message: "Voice connection timed out. Reconnect to continue.",
      });
      this.stop();
    }, 15000);
    socket.onopen = () =>
      socket.send(
        JSON.stringify({
          type: "authenticate",
          token,
          model: this.options.analysisModel,
        }),
      );
    socket.onmessage = async (message) => {
      const event = JSON.parse(message.data) as VoiceEvent;
      if (event.type === "ready" && !this.ready) {
        clearTimeout(this.connectionTimer);
        this.ready = true;
        try {
          if (!this.options.textOnly) await this.startCapture();
        } catch (error) {
          this.onEvent({
            type: "error",
            message:
              error instanceof Error ? error.message : "Microphone failed.",
          });
          this.stop();
          return;
        }
      } else if (event.type === "audio") {
        this.play(String(event.data));
      } else if (event.type === "interrupted") {
        this.clearPlayback();
      }
      this.onEvent(event);
    };
    socket.onerror = () => {
      this.onEvent({
        type: "error",
        message:
          "Voice connection failed. Check the backend connection and try again.",
      });
      this.stop();
    };
    socket.onclose = () => {
      clearTimeout(this.closeTimer);
      const intentional = this.closed;
      this.stop();
      this.onEvent({
        type: intentional ? "stopped" : "disconnected",
        message:
          "Voice connection closed. Reconnect to resume the saved conversation.",
      });
    };
  }

  private async startCapture() {
    if (this.closed || !this.microphone) return;
    this.capture = new AudioContext();
    await this.capture.audioWorklet.addModule("/pcm-worklet.js");
    if (this.closed) return;
    const source = this.capture.createMediaStreamSource(this.microphone);
    this.worklet = new AudioWorkletNode(this.capture, "pcm-capture");
    this.worklet.port.onmessage = (event) => {
      if (this.closed || this.socket?.readyState !== WebSocket.OPEN) return;
      const samples = new Int16Array(event.data);
      let squareSum = 0;
      for (const sample of samples) squareSum += (sample / 32768) ** 2;
      this.onLevel(Math.min(1, Math.sqrt(squareSum / samples.length) * 8));
      if (this.socket.bufferedAmount > 128_000) {
        this.onEvent({
          type: "error",
          message:
            "The network is too slow for live audio. Reconnect or use text.",
        });
        this.stop();
        return;
      }
      const bytes = new Uint8Array(event.data);
      let binary = "";
      for (const byte of bytes) binary += String.fromCharCode(byte);
      this.socket.send(JSON.stringify({ type: "audio", data: btoa(binary) }));
    };
    source.connect(this.worklet);
    this.worklet.connect(this.capture.destination);
    await this.capture.resume();
  }

  private play(encoded: string) {
    if (!this.playback || this.closed || this.options.spokenResponses === false)
      return;
    const bytes = Uint8Array.from(atob(encoded), (char) => char.charCodeAt(0));
    const view = new DataView(bytes.buffer);
    const audio = this.playback.createBuffer(
      1,
      Math.floor(bytes.length / 2),
      24000,
    );
    const output = audio.getChannelData(0);
    for (let i = 0; i < output.length; i++)
      output[i] = view.getInt16(i * 2, true) / 32768;
    const source = this.playback.createBufferSource();
    source.buffer = audio;
    source.connect(this.playback.destination);
    this.playing.add(source);
    source.onended = () => this.playing.delete(source);
    this.nextStart = Math.max(this.nextStart, this.playback.currentTime + 0.02);
    source.start(this.nextStart);
    this.nextStart += audio.duration;
  }

  toggleMute() {
    this.muted = !this.muted;
    this.microphone?.getAudioTracks().forEach((track) => {
      track.enabled = !this.muted;
    });
    return this.muted;
  }

  private clearPlayback() {
    for (const source of this.playing) {
      try {
        source.stop();
      } catch {}
    }
    this.playing.clear();
    this.nextStart = 0;
  }

  sendText(text: string) {
    if (
      this.closed ||
      !this.ready ||
      this.socket?.readyState !== WebSocket.OPEN ||
      !text.trim()
    )
      return false;
    this.clearPlayback();
    this.socket.send(JSON.stringify({ type: "text", text }));
    return true;
  }

  stop(graceful = false) {
    if (this.closed) return;
    this.closed = true;
    clearTimeout(this.connectionTimer);
    if (this.socket?.readyState === WebSocket.OPEN)
      this.socket.send(JSON.stringify({ type: "stop" }));
    if (graceful && this.socket?.readyState === WebSocket.OPEN) {
      // Release microphone/speakers immediately while the server flushes its
      // last transcript and returns the final fenced draft state.
      this.closeTimer = setTimeout(() => this.socket?.close(), 5000);
    } else this.socket?.close();
    this.microphone?.getTracks().forEach((track) => track.stop());
    this.worklet?.disconnect();
    this.clearPlayback();
    void this.capture?.close();
    void this.playback?.close();
    this.onLevel(0);
  }
}
