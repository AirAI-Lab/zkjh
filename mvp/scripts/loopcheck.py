import serial, time, datetime, os
PORT="COM4"
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","loopcheck_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial(PORT,115200,timeout=0.01)  # 10ms high-freq poll
print("[loopcheck] COM4 150s, high-freq timestamps")
print("[loopcheck] NO user action needed - board may be self-looping")
t0=time.time()
events=[]  # (timestamp, bytes)
total=0
with open(LOG,"wb") as fp:
    while time.time()-t0 < 150:
        d=ser.read(8192)
        if d:
            ts=time.time()-t0
            events.append((ts,d))
            total+=len(d)
            fp.write(("%.3f "%ts).encode()+d.hex().encode()+b"\n"); fp.flush()
            print("[%7.3fs] +%dB %s" % (ts,len(d),d[:48].hex()))
ser.close()
print("\n===== SUMMARY =====")
print("total=%dB events=%d" % (total,len(events)))
hits=[e for e in events if b"9a7b5510" in e[1].replace(b"\r",b"").replace(b"\n",b"")]
print("9a7b5510 appearances: %d" % len(hits))
for ts,d in hits:
    print("  @ %.3fs : %s" % (ts, d.hex()))
if len(hits)>=2:
    gaps=[hits[i+1][0]-hits[i][0] for i in range(len(hits)-1)]
    print("intervals: %s" % [round(g,2) for g in gaps])
