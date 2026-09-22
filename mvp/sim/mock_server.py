#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MVP 平台模拟服务器 (零依赖, 标准库)
用法: python mock_server.py [--port 8080] [--dir received]
接口:
  POST /api/event            JSON 事件+状态上报(ICD 4.3 报文)
  POST /api/image/<devid>/<name>   图片二进制上传
  GET  /api/status           收到的统计
验收点: 打印事件/图片摘要; received/ 目录留档
"""
import json, os, time, argparse
from http.server import HTTPServer, BaseHTTPRequestHandler

STAT = {"events": 0, "images": 0, "gas_alarms": 0}

class H(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    def do_GET(self):
        if self.path == "/api/status":
            return self._json(STAT)
        self.send_response(404); self.end_headers()
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        if self.path == "/api/event":
            ev = json.loads(body.decode("utf-8"))
            STAT["events"] += 1
            t = ev.get("event", {}).get("type")
            if t in (6, 7):   # 燃气低报/高报
                STAT["gas_alarms"] += 1
            print(time.strftime("%H:%M:%S"), "EVENT devid=%s type=%s name=%s battery=%s%%" % (
                ev.get("device_id"), t, ev.get("event", {}).get("name"),
                ev.get("status", {}).get("battery_pct")))
            with open(os.path.join(OUT, "events.jsonl"), "a", encoding="utf-8") as fp:
                fp.write(json.dumps(ev, ensure_ascii=False) + "\n")
            return self._json({"ok": True})
        if self.path.startswith("/api/image/"):
            parts = self.path.split("/")
            name = parts[-1]; devid = parts[-2] if len(parts) > 3 else "unknown"
            os.makedirs(os.path.join(OUT, devid), exist_ok=True)
            p = os.path.join(OUT, devid, name)
            with open(p, "wb") as fp: fp.write(body)
            STAT["images"] += 1
            print(time.strftime("%H:%M:%S"), "IMAGE devid=%s %s %dB" % (devid, name, len(body)))
            return self._json({"ok": True, "size": len(body)})
        self.send_response(404); self.end_headers()
    def log_message(self, *a): pass

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--dir", default="received")
    a = ap.parse_args()
    OUT = a.dir; os.makedirs(OUT, exist_ok=True)
    print("MockServer http://0.0.0.0:%d  -> %s/" % (a.port, OUT))
    HTTPServer(("0.0.0.0", a.port), H).serve_forever()