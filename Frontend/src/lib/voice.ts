import { backendUrl, guestToken } from "./api";

type VoiceEvent = { type: string; [key: string]: unknown };

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

  constructor(
    private onEvent: (event: VoiceEvent) => void,
    private onLevel: (level: number) => void,
  ) {}

  async start(conversationId: string) {
    if (!navigator.mediaDevices?.getUserMedia || !window.AudioWorkletNode)
      throw new Error(
        "This browser cannot stream microphone audio. Use an up-to-date browser over HTTPS.",
      );
    this.playback = new AudioContext({ sampleRate: 24000 });
    await this.playback.resume();
    this.microphone = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
      },
    });
    if (this.closed) {
      this.microphone.getTracks().forEach((track) => track.stop());
      return;
    }
    const base = await backendUrl();
    const token = await guestToken();
    if (this.closed) return;
    const url = new URL(`${base}/api/v1/conversations/${conversationId}/voice`);
    url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(url);
    this.socket = socket;
    socket.onopen = () =>
      socket.send(JSON.stringify({ type: "authenticate", token }));
    socket.onmessage = async (message) => {
      const event = JSON.parse(message.data) as VoiceEvent;
      if (event.type === "ready" && !this.ready) {
        this.ready = true;
        try {
          await this.startCapture();
        } catch (error) {
          this.onEvent({
            type: "error",
            message:
              error instanceof Error ? error.message : "Microphone failed.",
          });
          this.stop();
        }
      } else if (event.type === "audio") {
        this.play(String(event.data));
      } else if (event.type === "interrupted") {
        this.clearPlayback();
      }
      this.onEvent(event);
    };
    socket.onerror = () =>
      this.onEvent({
        type: "error",
        message:
          "Voice connection failed. Check the backend connection and try again.",
      });
    socket.onclose = () => {
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
    if (!this.playback || this.closed) return;
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

  stop() {
    if (this.closed) return;
    this.closed = true;
    if (this.socket?.readyState === WebSocket.OPEN)
      this.socket.send(JSON.stringify({ type: "stop" }));
    this.socket?.close();
    this.microphone?.getTracks().forEach((track) => track.stop());
    this.worklet?.disconnect();
    this.clearPlayback();
    void this.capture?.close();
    void this.playback?.close();
    this.onLevel(0);
  }
}
