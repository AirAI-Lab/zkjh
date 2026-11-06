import serial, time, sys, datetime, os
PORT="COM4"; LOGDIR=r"D:\github\zkjh\mvp\logs"
os.makedirs(LOGDIR, exist_ok=True)
LOG=os.path.join(LOGDIR, "longwatch_%s.log" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
s=serial.Serial(PORT,115200,timeout=0.05)
print("[longwatch] COM4 300s -> "+LOG)
t0=time.time()
with open(LOG,"a",encoding="utf-8",errors="replace") as fp:
    while time.time()-t0 < 300:
        d=s.read(8192)
        if d:
            txt=d.decode("utf-8","replace")
            print("[%6.1fs] %r" % (time.time()-t0, txt))
            fp.write("[%6.1fs] %s\n" % (time.time()-t0, txt)); fp.flush()
        if (time.time()-t0) % 30 < 0.06:
            s.write(b"\r\n")  # 每30秒戳一下,看有没有回显
            time.sleep(0.5)
s.close(); print("[done]")
