/* PCM capture only: samples are streamed, never recorded to a file. */
class PcmCapture extends AudioWorkletProcessor {
  constructor() {
    super();
    this.sum = 0;
    this.count = 0;
    this.position = 0;
    this.output = [];
    this.ratio = sampleRate / 16000;
  }
  process(inputs, outputs) {
    const input = inputs[0]?.[0];
    if (input) {
      for (const value of input) {
        this.sum += value;
        this.count++;
        this.position++;
        if (this.position >= this.ratio) {
          const normalized = Math.max(-1, Math.min(1, this.sum / this.count));
          this.output.push(Math.round(normalized * (normalized < 0 ? 32768 : 32767)));
          this.sum = 0;
          this.count = 0;
          this.position -= this.ratio;
          if (this.output.length === 800) {
            const pcm = new Int16Array(this.output);
            this.port.postMessage(pcm.buffer, [pcm.buffer]);
            this.output = [];
          }
        }
      }
    }
    for (const channel of outputs[0] ?? []) channel.fill(0);
    return true;
  }
}
registerProcessor("pcm-capture", PcmCapture);
