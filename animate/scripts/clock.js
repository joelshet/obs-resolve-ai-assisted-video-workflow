// Replaces the page's clock so time moves only when __advance(ms) is called.
// Timers, requestAnimationFrame, Date and performance.now all read it, and
// CSS animations and transitions are paused and set to it. If the page loaded
// sound.js, its audio is rendered up to the same time before the frame draws.
(() => {
  let now = 0, id = 0;
  const timers = new Map(), rafs = new Map(), started = new WeakMap();
  const RealDate = Date, epoch = RealDate.now();
  performance.now = () => now;
  window.Date = class extends RealDate {
    constructor(...a) { a.length ? super(...a) : super(epoch + now); }
    static now() { return epoch + now; }
  };
  window.setTimeout = (fn, ms = 0, ...args) => (timers.set(++id, { at: now + Math.max(0, +ms || 0), fn, args }), id);
  window.setInterval = (fn, ms = 0, ...args) => (timers.set(++id, { at: now + Math.max(1, +ms || 0), fn, args, every: Math.max(1, +ms || 0) }), id);
  window.clearTimeout = window.clearInterval = (i) => timers.delete(i);
  window.requestAnimationFrame = (fn) => (rafs.set(++id, fn), id);
  window.cancelAnimationFrame = (i) => rafs.delete(i);

  window.__advance = async (ms) => {
    const target = now + ms;
    for (;;) {
      let due = null, dueId;
      for (const [i, t] of timers) if (t.at <= target && (!due || t.at < due.at)) { due = t; dueId = i; }
      if (!due) break;
      now = due.at;
      if (due.every) due.at += due.every; else timers.delete(dueId);
      if (typeof due.fn === "function") due.fn(...due.args);
    }
    now = target;
    if (window.__audioStep) await window.__audioStep(now / 1000);
    const frame = [...rafs.values()]; rafs.clear();
    for (const fn of frame) fn(now);
    for (const a of document.getAnimations()) {
      if (!started.has(a)) started.set(a, now);
      const t = now - started.get(a), end = a.effect ? a.effect.getComputedTiming().endTime : Infinity;
      if (t >= end) a.finish(); else { a.pause(); a.currentTime = t; }
    }
    return now;
  };
})();
