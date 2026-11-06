#!/usr/bin/env python3
"""把文件发到 TG。两种模式（由 workflow 调用）：
- dispatch 模式：发 FILE_PATH（可带 MESSAGE 先发文本）。
- --sync 模式：发本次 push 新增/修改的文件（.github/ 与 README.md 除外）。

按扩展名选发送方式：图片 <=10MB 发照片，mp4/mov 发视频流，gif 发动画，
mp3/m4a 发音频，其余发文件；>50MB 不发文件，只发 raw 链接。
环境变量：TELEGRAM_BOT_TOKEN、TELEGRAM_CHAT_ID、GITHUB_REPOSITORY（可选）。
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
import uuid

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT = os.environ["TELEGRAM_CHAT_ID"]
API = f"https://api.telegram.org/bot{TOKEN}"
REPO = os.environ.get("GITHUB_REPOSITORY", "")
MAX_UPLOAD = 50 * 1024 * 1024      # Bot API 单文件上限
MAX_PHOTO = 10 * 1024 * 1024       # 照片上限


def tg(method, data=None, files=None):
    if files is None:
        req = urllib.request.Request(
            f"{API}/{method}", data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())
    boundary = uuid.uuid4().hex
    body = b""
    for k, v in data.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; "
                 f"name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    for field, (fn, blob, mt) in files.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; "
                 f"name=\"{field}\"; filename=\"{fn}\"\r\n"
                 f"Content-Type: {mt}\r\n\r\n").encode() + blob + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{API}/{method}", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read())


def send_text(text):
    if len(text) > 4096:
        text = text[:4093] + "…"
    tg("sendMessage", {"chat_id": CHAT, "text": text})


def send_file(path):
    size = os.path.getsize(path)
    fname = os.path.basename(path)
    if size > MAX_UPLOAD:
        url = (f"https://raw.githubusercontent.com/{REPO}/main/"
               + urllib.parse.quote(path))
        send_text(f"{fname}（约 {size // 1048576}MB）超过 Bot API 50MB 上限，未发送：{url}")
        print(f"oversize, link only: {path} ({size} bytes)")
        return False
    with open(path, "rb") as f:
        blob = f.read()
    base = {"chat_id": CHAT, "caption": fname[:1020]}
    ext = fname.rsplit(".", 1)[-1].lower() if "." in fname else ""
    if ext in ("png", "jpg", "jpeg", "webp") and size <= MAX_PHOTO:
        mt = {"png": "image/png", "jpg": "image/jpeg",
              "jpeg": "image/jpeg", "webp": "image/webp"}[ext]
        tg("sendPhoto", base, {"photo": (fname, blob, mt)})
    elif ext in ("mp4", "mov"):
        tg("sendVideo", dict(base, supports_streaming=True),
           {"video": (fname, blob, "video/mp4")})
    elif ext == "gif":
        tg("sendAnimation", base, {"animation": (fname, blob, "image/gif")})
    elif ext in ("mp3", "m4a"):
        tg("sendAudio", base, {"audio": (fname, blob, "audio/mpeg")})
    else:
        tg("sendDocument", base,
           {"document": (fname, blob, "application/octet-stream")})
    print(f"sent: {path} ({size} bytes)")
    return True


def main():
    if "--sync" in sys.argv:
        before = os.environ.get("BEFORE", "")
        sha = os.environ.get("SHA", "")
        if not before or set(before) == {"0"}:
            print("no usable before SHA, skipping")
            return
        diff = subprocess.run(
            ["git", "-c", "core.quotepath=false", "diff", "--name-only",
             "--diff-filter=AM", before, sha],
            capture_output=True, text=True)
        changed = [l.strip().strip('"') for l in diff.stdout.splitlines()
                   if l.strip()]
        sendable = [f for f in changed
                    if not f.startswith(".github/") and f != "README.md"
                    and os.path.isfile(f)]
        print("changed:", changed)
        print("sendable:", sendable)
        for path in sendable:
            send_file(path)
            time.sleep(1.2)  # 私聊限速约 1 条/秒
    else:
        msg = os.environ.get("MESSAGE", "")
        if msg:
            send_text(msg)
        path = os.environ.get("FILE_PATH", "")
        if path:
            if not os.path.isfile(path):
                print(f"missing file: {path}")
                sys.exit(1)
            send_file(path)
        elif not msg:
            print("nothing to send")


main()
