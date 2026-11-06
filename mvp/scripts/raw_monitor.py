import serial, time, datetime, os, sys
PORT="COM4"
LOGDIR=r"D:\github\zkjh\mvp\logs"
LOG=os.path.join(LOGDIR, "raw_%s.bin" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
s=serial.Serial(PORT,115200,timeout=0.05)
print("[raw] COM4 180s -> "+LOG)
t0=time.time(); total=0
with open(LOG,"wb") as fp:
    while time.time()-t0 < 180:
        d=s.read(8192)
        if d:
            fp.write(d); fp.flush(); total+=len(d)
            print("[%5.1fs] +%dB : %s" % (time.time()-t0, len(d), d[:64].hex()))
        if (time.time()-t0) % 20 < 0.05:
            s.write(b"\r\n"); time.sleep(0.3)
s.close(); print("[done] total=%dB -> %s" % (total, LOG))
