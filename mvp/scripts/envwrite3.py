import ctypes, ctypes.wintypes as wt
k=ctypes.windll.kernel32
k.CreateFileW.restype=ctypes.c_void_p
k.CreateFileW.argtypes=[ctypes.c_wchar_p,wt.DWORD,wt.DWORD,ctypes.c_void_p,wt.DWORD,wt.DWORD,ctypes.c_void_p]
k.SetFilePointer.argtypes=[ctypes.c_void_p,wt.LONG,ctypes.POINTER(wt.LONG),wt.DWORD]
k.WriteFile.argtypes=[ctypes.c_void_p,ctypes.c_void_p,wt.DWORD,ctypes.POINTER(wt.DWORD),ctypes.c_void_p]
k.ReadFile.argtypes=[ctypes.c_void_p,ctypes.c_void_p,wt.DWORD,ctypes.POINTER(wt.DWORD),ctypes.c_void_p]
h=k.CreateFileW(r"\\.\PhysicalDrive1",0xC0000000,3,None,3,0,None)
if not h or h==0xFFFFFFFFFFFFFFFF:
    open(r"D:\github\zkjh\mvp\logs\envwrite.txt","w").write("open fail"); raise SystemExit
buf=ctypes.create_string_buffer(16*1024*1024); read=wt.DWORD(0)
k.ReadFile(h,buf,len(buf),ctypes.byref(read),None)
data=bytearray(buf.raw[:read.value])
i=data.find(b"bootargs=")
j=data.find(b"\x00\x00",i)
oldlen=j+2-i
na=b"bootargs=console=ttyS1,115200n8 mem=41M@0x0 rmem=23M@0x2900000 rdinit=/linuxrc panic=999999999\x00"
nc=b"bootcmd=mmc read 0x80600000 0x1800 0x3000; fatload mmc 0 0x81000000 uInitrd; bootm 0x80600000 0x81000000\x00"
kp=b"bootdelay=1\x00baudrate=115200\x00loads_echo=1\x00"
nb=na+nc+kp
pad=oldlen-len(nb)-2
nb=nb+b"\x00"*pad+b"\x00\x00"
hi=ctypes.c_long(0)
k.SetFilePointer(h,i,ctypes.byref(hi),0)
src=ctypes.create_string_buffer(bytes(nb))
w=wt.DWORD(0)
ok=k.WriteFile(h,src,len(nb),ctypes.byref(w),None)
err=ctypes.GetLastError()
k.SetFilePointer(h,i,ctypes.byref(ctypes.c_long(0)),0)
rb=ctypes.create_string_buffer(oldlen); r2=wt.DWORD(0)
k.ReadFile(h,rb,oldlen,ctypes.byref(r2),None)
same=(rb.raw==bytes(nb))
open(r"D:\github\zkjh\mvp\logs\envwrite.txt","w").write("wrote=%d ok=%d err=%d SAME=%s\n%s"%(w.value,ok,err,same,rb.raw[:200].decode("ascii","replace")))
k.CloseHandle(ctypes.c_void_p(h))
