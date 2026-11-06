import serial, time, io, datetime, os
LOG=os.path.join(r"D:\github\zkjh\mvp\logs","fix3b_%s.log"%datetime.datetime.now().strftime("%H%M%S"))
ser=serial.Serial("COM6",115200,timeout=0.05)
out=io.open(LOG,"w",encoding="utf-8",errors="replace")
print("[fix3b] ESC-interrupt autoboot then boot fix3")
buf=b""; t0=time.time(); sent_esc=False; got_prompt=False
while time.time()-t0<150:
    d=ser.read(4096)
    if d:
        buf+=d; out.write(d.decode("ascii","replace")); out.flush()
    if (b"stop autoboot" in buf[-400:]) and not sent_esc:
        ser.write(b"\x1b"); time.sleep(0.05); ser.write(b"\r\n"); sent_esc=True
    if sent_esc and b"isvp_t23#" in buf[-200:]:
        got_prompt=True; break
if not got_prompt:
    out.close(); ser.close(); print("NO PROMPT"); exit(1)
time.sleep(0.5); ser.reset_input_buffer()
print("[fix3b] prompt! boot fix3")
def run(cmd,wait):
    ser.write((cmd+"\n").encode())
    t1=time.time(); b=b""
    while time.time()-t1<wait:
        d=ser.read(4096)
        if d: b+=d
    out.write(">>> %s\n%s\n"%(cmd,b.decode("ascii","replace"))); out.flush()
    return b
run("setenv verify no",2)
run("fatload mmc 0 0x80600000 uImage-fix3-lzma.bin",12)
b=run("bootm 0x80600000",20)
print("bootm:",b.decode("ascii","replace")[:150].replace("\n","|"))
t2=time.time()
while time.time()-t2<100:
    d=ser.read(4096)
    if d: out.write(d.decode("ascii","replace")); out.flush()
ser.close(); out.close(); print("DONE")
