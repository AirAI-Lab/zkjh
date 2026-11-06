import serial, time, datetime, os
PORT="COM4"
LOG=os.path.join(r"D:\github\zkjh\mvp\logs", "bootsf_%s.log" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
ser=serial.Serial(PORT,115200,timeout=0.05)
print("[boot-sf] sf read kernel + bootm, listen 75s")
ser.write(b"\r\n"); time.sleep(0.3); ser.reset_input_buffer()
ser.write(b"sf probe\n"); time.sleep(2)
ser.write(b"sf read 0x80600000 0x98000 0x500000\n"); time.sleep(4)
ser.write(b"bootm 0x80600000\n")
t0=time.time(); total=0
with open(LOG,"wb") as fp:
    while time.time()-t0 < 75:
        d=ser.read(8192)
        if d:
            fp.write(d); fp.flush(); total+=len(d)
            print(d.decode("ascii","replace"), end="")
ser.close()
print("\n[done] %dB -> %s" % (total, LOG))
