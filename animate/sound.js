// Sound for decks: the typebeat synth (triangle notes on a pentatonic scale
// from A3, a noise tick for spaces and punctuation, a scope on the output).
// In a browser it plays live after the first click or key. Under frames.py it
// renders offline in step with the page clock, so the scope in each frame and
// the saved WAV are the same audio.
(() => {
  const R = window.__render; // set by frames.py: { seconds, sampleRate }
  const ctx = R
    ? new OfflineAudioContext(1, Math.ceil(R.seconds * R.sampleRate), R.sampleRate)
    : new AudioContext();
  const master = ctx.createGain(), analyser = ctx.createAnalyser(), comp = ctx.createDynamicsCompressor();
  master.gain.value = 0.5;
  analyser.fftSize = 2048;
  master.connect(analyser).connect(comp).connect(ctx.destination);
  if (!R) for (const e of ["pointerdown", "keydown"]) addEventListener(e, () => ctx.resume(), { once: true });

  const live = () => R || ctx.state === "running";
  const at = () => (R ? Math.max(ctx.currentTime, performance.now() / 1000) : ctx.currentTime);

  // Seeded, so the noise and any typing rhythm repeat exactly.
  let seed = 0x9e3779b9;
  const random = () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };

  const ROOT = 220, SCALE = [0, 2, 4, 7, 9];
  const NAMES = ["A", "A♯", "B", "C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯"];
  // A letter or digit to { hz, name }, or null for anything that ticks.
  function note(ch) {
    const c = ch.toLowerCase().charCodeAt(0);
    let step;
    if (c >= 97 && c <= 122) step = c - 97;
    else if (c >= 48 && c <= 57) step = c - 48 - SCALE.length;
    else return null;
    const span = SCALE.length * 2, i = ((step % span) + span) % span;
    const semis = SCALE[i % SCALE.length] + 12 * Math.floor(i / SCALE.length) - (step < 0 ? 12 : 0);
    const fromC = semis + 9;
    return { hz: ROOT * 2 ** (semis / 12), name: NAMES[((semis % 12) + 12) % 12] + (3 + Math.floor(fromC / 12)) };
  }

  function tone(hz, { type = "triangle", dur = 0.22, vol = 0.35 } = {}) {
    if (!live()) return;
    const t = at(), osc = ctx.createOscillator(), g = ctx.createGain();
    osc.type = type;
    osc.frequency.value = hz;
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol, t + 0.008);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    osc.connect(g).connect(master);
    osc.start(t);
    osc.stop(t + dur + 0.02);
  }

  function tick() {
    if (!live()) return;
    const t = at(), len = Math.floor(ctx.sampleRate * 0.04);
    const buf = ctx.createBuffer(1, len, ctx.sampleRate), d = buf.getChannelData(0);
    for (let i = 0; i < len; i++) d[i] = (random() * 2 - 1) * (1 - i / len);
    const src = ctx.createBufferSource(), hp = ctx.createBiquadFilter(), g = ctx.createGain();
    src.buffer = buf;
    hp.type = "highpass";
    hp.frequency.value = 2500;
    g.gain.value = 0.25;
    src.connect(hp).connect(g).connect(master);
    src.start(t);
  }

  const wave = new Float32Array(analyser.fftSize);
  window.Sound = {
    note, tone, tick, random,
    sampleRate: ctx.sampleRate,
    // The newest 2048 samples of the output.
    wave() { analyser.getFloatTimeDomainData(wave); return wave; },
  };

  if (!R) return;
  let rendering = null, wav = null;
  // Render audio up to page time t. clock.js calls this once per frame.
  window.__audioStep = async (t) => {
    if (t <= ctx.currentTime + 256 / ctx.sampleRate || t >= R.seconds) return;
    const reached = ctx.suspend(t);
    if (rendering) ctx.resume(); else rendering = ctx.startRendering();
    await reached;
  };
  // Finish, keep the first `seconds` as 16-bit mono WAV bytes, return the byte count.
  window.__audioWav = async (seconds) => {
    if (rendering) ctx.resume(); else rendering = ctx.startRendering();
    const pcm = (await rendering).getChannelData(0);
    const n = Math.min(pcm.length, Math.round(seconds * ctx.sampleRate));
    const v = new DataView(new ArrayBuffer(44 + n * 2));
    const str = (o, s) => [...s].forEach((ch, i) => v.setUint8(o + i, ch.charCodeAt(0)));
    str(0, "RIFF"); v.setUint32(4, 36 + n * 2, true); str(8, "WAVEfmt ");
    v.setUint32(16, 16, true); v.setUint16(20, 1, true); v.setUint16(22, 1, true);
    v.setUint32(24, ctx.sampleRate, true); v.setUint32(28, ctx.sampleRate * 2, true);
    v.setUint16(32, 2, true); v.setUint16(34, 16, true); str(36, "data"); v.setUint32(40, n * 2, true);
    for (let i = 0; i < n; i++) v.setInt16(44 + i * 2, Math.max(-1, Math.min(1, pcm[i])) * 32767, true);
    wav = new Uint8Array(v.buffer);
    return wav.length;
  };
  window.__audioChunk = (from, size) => {
    let s = "";
    for (const b of wav.subarray(from, from + size)) s += String.fromCharCode(b);
    return btoa(s);
  };
})();
