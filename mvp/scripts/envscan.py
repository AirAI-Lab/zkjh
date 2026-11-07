import ctypes, ctypes.wintypes as wt
k=ctypes.windll.kernel32
h=k.CreateFileW(r"\\.\PhysicalDrive1",0x80000000,3,None,3,0,None)
if h in (-1, 0xFFFFFFFFFFFFFFFF):
    open(r"D:\github\zkjh\mvp\logs\envscan.txt","w").write("open fail %d"%ctypes.GetLastError()); raise SystemExit
buf=ctypes.create_string_buffer(16*1024*1024)
read=wt.DWORD(0)
k.ReadFile(h,buf,len(buf),ctypes.byref(read),None)
data=buf.raw[:read.value]
i=data.find(b"bootargs=")
res="read=%d bootargs_at=%d sector=%s\n"%(read.value,i,i//512 if i>=0 else "?")
if i>=0:
    seg=data[max(0,i-64):i+800]
    res+="".join(chr(c) if 32<=c<127 else "|" for c in seg)
open(r"D:\github\zkjh\mvp\logs\envscan.txt","w").write(res)
k.CloseHandle(h)
