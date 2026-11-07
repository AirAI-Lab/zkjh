import ctypes, ctypes.wintypes as wt
k=ctypes.windll.kernel32
h=k.CreateFileW(r"\\.\PhysicalDrive1",0xC0000000,3,None,3,0,None)
if h in (-1,0xFFFFFFFFFFFFFFFF):
    open(r"D:\github\zkjh\mvp\logs\envwrite.txt","w").write("open fail %d"%ctypes.GetLastError()); raise SystemExit
buf=ctypes.create_string_buffer(16*1024*1024); read=wt.DWORD(0)
k.ReadFile(h,buf,len(buf),ctypes.byref(read),None)
data=bytearray(buf.raw[:read.value])
i=data.find(b"bootargs=")
j=data.find(b"\x00\x00", i)
orig=bytes(data[i:j+2]); oldlen=len(orig)
new_args=b"bootargs=console=ttyS1,115200n8 mem=41M@0x0 rmem=23M@0x2900000 rdinit=/linuxrc panic=999999999\x00"
new_cmd=b"bootcmd=mmc read 0x80600000 0x1800 0x3000; fatload mmc 0 0x81000000 uInitrd; bootm 0x80600000 0x81000000\x00"
keep=b"bootdelay=1\x00baudrate=115200\x00loads_echo=1\x00"
nb=new_args+new_cmd+keep
padn=oldlen-len(nb)-2
if padn<0:
    open(r"D:\github\zkjh\mvp\logs\envwrite.txt","w").write("TOO LONG"); k.CloseHandle(h); raise SystemExit
nb=nb+b"\x00"*padn+b"\x00\x00"
assert len(nb)==oldlen
# write with proper pointer
hi=ctypes.c_long(0)
k.SetFilePointer(h, i & 0xFFFFFFFF, ctypes.byref(hi), 0)
wrote=wt.DWORD(0)
ok=k.WriteFile(h, bytes(nb), len(nb), ctypes.byref(wrote), None)
err=ctypes.GetLastError()
# verify
k.SetFilePointer(h, i & 0xFFFFFFFF, ctypes.byref(ctypes.c_long(0)), 0)
rb=ctypes.create_string_buffer(oldlen); r2=wt.DWORD(0)
k.ReadFile(h,rb,oldlen,ctypes.byref(r2),None)
same=(rb.raw==nb)
res="i=%d old=%d wrote=%d ok=%d err=%d SAME=%s\n%s"%(i,oldlen,wrote.value,ok,err,same,nb[:220].decode("ascii","replace"))
open(r"D:\github\zkjh\mvp\logs\envwrite.txt","w").write(res)
k.CloseHandle(h)
