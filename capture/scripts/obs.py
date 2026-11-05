#!/usr/bin/env python3
"""obs — send one obs-websocket request and print the reply's data as JSON.

  obs.py GetRecordStatus
  obs.py SetCurrentProgramScene '{"sceneName": "Shoot + Me"}'

Exits 1 with the reason on stderr when OBS isn't reachable or refuses.
"""
import base64, hashlib, json, os, socket, struct, sys

CONFIG = "~/Library/Application Support/obs-studio/plugin_config/obs-websocket/config.json"


def b64sha(text):
    return base64.b64encode(hashlib.sha256(text.encode()).digest()).decode()


class Socket:
    def __init__(self, port):
        self.s = socket.create_connection(("127.0.0.1", port), timeout=20)
        key = base64.b64encode(os.urandom(16)).decode()
        self.s.sendall(
            f"GET / HTTP/1.1\r\nHost: localhost:{port}\r\nUpgrade: websocket\r\n"
            f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n"
            "Sec-WebSocket-Protocol: obswebsocket.json\r\n\r\n".encode())
        self.buf = b""
        while b"\r\n\r\n" not in self.buf:
            self.buf += self.s.recv(4096)
        self.buf = self.buf.split(b"\r\n\r\n", 1)[1]

    def take(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(1 << 20)
            if not chunk:
                raise EOFError("OBS closed the connection")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def recv(self):
        out = b""
        while True:
            head = self.take(2)
            n = head[1] & 127
            if n == 126:
                n = struct.unpack(">H", self.take(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self.take(8))[0]
            data = self.take(n)
            if head[0] & 15 == 9:  # ping
                continue
            out += data
            if head[0] & 0x80:
                return json.loads(out)

    def send(self, message):
        data = json.dumps(message).encode()
        mask = os.urandom(4)
        n = len(data)
        size = bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack(">H", n)
        self.s.sendall(bytes([0x81]) + size + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__.strip())
    request = sys.argv[1]
    data = json.loads(sys.argv[2]) if len(sys.argv) == 3 else {}
    try:
        with open(os.path.expanduser(CONFIG)) as f:
            config = json.load(f)
        ws = Socket(config.get("server_port", 4455))
        auth = ws.recv()["d"]["authentication"]
        secret = b64sha(config["server_password"] + auth["salt"])
        ws.send({"op": 1, "d": {"rpcVersion": 1, "authentication": b64sha(secret + auth["challenge"]),
                                "eventSubscriptions": 0}})
        ws.recv()
        ws.send({"op": 6, "d": {"requestType": request, "requestId": "1", "requestData": data}})
        while True:
            reply = ws.recv()
            if reply["op"] == 7:
                break
    except (OSError, EOFError) as e:
        sys.exit(f"obs: can't reach OBS: {e}")
    status = reply["d"]["requestStatus"]
    if not status["result"]:
        sys.exit(f"obs: {request}: {status.get('comment', status['code'])}")
    print(json.dumps(reply["d"].get("responseData", {})))


if __name__ == "__main__":
    main()
