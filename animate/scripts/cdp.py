"""Minimal Chrome DevTools client over --remote-debugging-pipe. Stdlib only."""
import atexit, fcntl, json, os, select, shutil, subprocess, tempfile

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PATIENCE = 60  # seconds to wait on Chrome before calling it stuck


class Chrome:
    def __init__(self, width, height):
        to_r, to_w = os.pipe()
        from_r, from_w = os.pipe()
        # Chrome reads commands on fd 3 and writes replies on fd 4.
        hi_r = fcntl.fcntl(to_r, fcntl.F_DUPFD, 20)
        hi_w = fcntl.fcntl(from_w, fcntl.F_DUPFD, 20)

        def wire():
            os.dup2(hi_r, 3)
            os.dup2(hi_w, 4)

        self.profile = tempfile.mkdtemp(prefix="chrome-")
        self.proc = subprocess.Popen(
            [CHROME, "--headless=new", "--remote-debugging-pipe",
             f"--user-data-dir={self.profile}", f"--window-size={width},{height}",
             "--hide-scrollbars", "--no-first-run", "--force-device-scale-factor=1",
             "--allow-file-access-from-files", "about:blank"],
            preexec_fn=wire, pass_fds=(3, 4, hi_r, hi_w),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for fd in (to_r, from_w, hi_r, hi_w):
            os.close(fd)
        self.w = os.fdopen(to_w, "wb", buffering=0)
        self.r = from_r
        self.buf = b""
        self.n = 0
        self.events = []
        self.session = None
        self.waiting_on = "startup"
        atexit.register(self.close)

    def _read(self):
        while b"\0" not in self.buf:
            if not select.select([self.r], [], [], PATIENCE)[0]:
                raise TimeoutError(f"chrome did not answer within {PATIENCE}s ({self.waiting_on})")
            chunk = os.read(self.r, 1 << 20)
            if not chunk:
                raise EOFError("chrome closed the pipe")
            self.buf += chunk
        raw, self.buf = self.buf.split(b"\0", 1)
        return json.loads(raw)

    def send(self, method, **params):
        self.n += 1
        msg = {"id": self.n, "method": method, "params": params}
        if self.session:
            msg["sessionId"] = self.session
        self.waiting_on = f"{method} {json.dumps(params)[:120]}"
        self.w.write(json.dumps(msg).encode() + b"\0")
        while True:
            m = self._read()
            if m.get("id") == self.n:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m["result"]
            self.events.append(m)

    def wait(self, name):
        self.waiting_on = f"event {name}"
        while True:
            for i, e in enumerate(self.events):
                if e.get("method") == name:
                    return self.events.pop(i)
            self.events.append(self._read())

    def open(self, url):
        target = self.send("Target.createTarget", url="about:blank")["targetId"]
        self.session = self.send("Target.attachToTarget", targetId=target, flatten=True)["sessionId"]
        self.send("Page.enable")
        self.send("Page.navigate", url=url)
        self.wait("Page.loadEventFired")

    def js(self, expr):
        r = self.send("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        if "exceptionDetails" in r:
            raise RuntimeError(f"page script failed: {r['exceptionDetails'].get('text')} in {expr!r}")
        return r["result"].get("value")

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        shutil.rmtree(self.profile, ignore_errors=True)
