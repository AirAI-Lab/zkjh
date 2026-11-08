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
    open(r"D:\github\zkjh\mvp\logs\envfix.txt","w").write("openfail");sys.exit()
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
blk=rd(ENV,64*1024)
crc_stored=struct.unpack("<I",blk[0:4])[0]
d32=blk[4:4+32764]
crc_calc=zlib.crc32(d32)&0xffffffff
res="stored=%08x calc32k=%08x match=%s\n"%(crc_stored,crc_calc,crc_stored==crc_calc)
# also try 4k size
d4=blk[4:4+4092]; c4=zlib.crc32(d4)&0xffffffff
res+="calc4k=%08x m4=%s\n"%(c4,crc_stored==c4)
open(r"D:\github\zkjh\mvp\logs\envfix.txt","w").write(res+blk[4:600].decode("ascii","replace").replace(chr(0),"|"))
k.CloseHandle(ctypes.c_void_p(h))
