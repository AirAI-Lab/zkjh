import ctypes, ctypes.wintypes as wt, zlib, struct, sys
k=ctypes.windll.kernel32
k.CreateFileW.restype=ctypes.c_void_p
k.CreateFileW.argtypes=[ctypes.c_wchar_p,wt.DWORD,wt.DWORD,ctypes.c_void_p,wt.DWORD,wt.DWORD,ctypes.c_void_p]
k.SetFilePointer.argtypes=[ctypes.c_void_p,wt.LONG,ctypes.POINTER(wt.LONG),wt.DWORD]
k.ReadFile.argtypes=[ctypes.c_void_p,ctypes.c_void_p,wt.DWORD,ctypes.POINTER(wt.DWORD),ctypes.c_void_p]
k.WriteFile.argtypes=[ctypes.c_void_p,ctypes.c_void_p,wt.DWORD,ctypes.POINTER(wt.DWORD),ctypes.c_void_p]
k.CloseHandle.argtypes=[ctypes.c_void_p]
h=k.CreateFileW(r"\\.\PhysicalDrive1",0xC0000000,3,None,3,0,None)
if not h or h==0xFFFFFFFFFFFFFFFF:
    open(r"D:\github\zkjh\mvp\logs\envfinal.txt","w").write("openfail");sys.exit()
def rd(off,n):
    b=ctypes.create_string_buffer(n); r=wt.DWORD(0)
    hi=ctypes.c_long((off>>32)&0x7FFFFFFF)
    k.SetFilePointer(h,off&0xFFFFFFFF,ctypes.byref(hi),0)
    k.ReadFile(h,b,n,ctypes.byref(r),None)
    return b.raw[:r.value]
def wr(off,data):
    src=ctypes.create_string_buffer(data); w=wt.DWORD(0)
    hi=ctypes.c_long((off>>32)&0x7FFFFFFF)
    k.SetFilePointer(h,off&0xFFFFFFFF,ctypes.byref(hi),0)
    ok=k.WriteFile(h,src,len(data),ctypes.byref(w),None)
    return ok,w.value,ctypes.GetLastError()
ENV=0x40400
data=bytearray(rd(ENV+4,32764))
# build new env text (keep tail of original untouched, replace front)
new=b"baudrate=115200\x00bootargs=console=ttyS1,115200n8 mem=41M@0x0 rmem=23M@0x2900000 rw rdinit=/linuxrc panic=999999999\x00bootcmd=mmc read 0x80600000 0x1800 0x3000; fatload mmc 0 0x82000000 uInitrd; bootm 0x80600000 0x82000000\x00bootdelay=1\x00ethact=Jz4775-9161\x00ethaddr=00:11:22:33:44:66\x00gatewayip=193.169.3.1\x00ipaddr=193.169.3.206\x00loads_echo=1\x00netmask=255.255.255.0\x00serverip=193.169.4.2\x00stderr=serial\x00stdin=serial\x00stdout=serial\x00"
data[0:len(new)]=new
# clear old remainder up to original double-NUL zone
rest=bytes(data[len(new):])
first_nn=rest.find(b"\x00\x00")
if first_nn>=0:
    data[len(new)+first_nn:]=b"\xff"*(len(data)-len(new)-first_nn)
crc=zlib.crc32(bytes(data))&0xffffffff
blob=struct.pack("<I",crc)+bytes(data)
ok,w,e=wr(ENV,blob)
chk=rd(ENV,32768)
same=(chk==blob)
res="crc=%08x wrote=%d ok=%d err=%d SAME=%s\n"%(crc,w,ok,e,same)
res+=chk[4:400].decode("ascii","replace").replace(chr(0),"|")
open(r"D:\github\zkjh\mvp\logs\envfinal.txt","w").write(res)
k.CloseHandle(ctypes.c_void_p(h))
