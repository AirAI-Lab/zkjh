import ctypes, ctypes.wintypes as wt
k=ctypes.windll.kernel32
k.CreateFileW.restype=ctypes.c_void_p
k.CreateFileW.argtypes=[ctypes.c_wchar_p,wt.DWORD,wt.DWORD,ctypes.c_void_p,wt.DWORD,wt.DWORD,ctypes.c_void_p]
k.SetFilePointer.argtypes=[ctypes.c_void_p,wt.LONG,ctypes.POINTER(wt.LONG),wt.DWORD]
k.ReadFile.argtypes=[ctypes.c_void_p,ctypes.c_void_p,wt.DWORD,ctypes.POINTER(wt.DWORD),ctypes.c_void_p]
h=k.CreateFileW(r"\\.\PhysicalDrive1",0x80000000,3,None,3,0,None)
if not h or h==0xFFFFFFFFFFFFFFFF:
    open(r"D:\github\zkjh\mvp\logs\scan2.txt","w").write("openfail");raise SystemExit
res=[]
CH=8*1024*1024
total=31954305024//512*512
posns=list(range(0,64*1024*1024,CH))+[total-8*1024*1024,total-16*1024*1024,total-32*1024*1024,total-64*1024*1024]
for pos in posns:
    buf=ctypes.create_string_buffer(CH); rd=wt.DWORD(0)
    hi=ctypes.c_long((pos>>32)&0xFFFFFFFF); lo=pos&0xFFFFFFFF
    k.SetFilePointer(h,lo,ctypes.byref(hi),0)
    k.ReadFile(h,buf,CH,ctypes.byref(rd),None)
    d=buf.raw[:rd.value]
    for pat in (b"panic=5",b"panic=999999999",b"bootargs=console"):
        i=d.find(pat)
        if i>=0:
            seg=d[max(0,i-80):i+260]
            txt="".join(chr(c) if 32<=c<127 else "|" for c in seg)
            res.append("pos=%d(0x%x) %s\n%s\n"%(pos,pos,pat.decode(),txt))
open(r"D:\github\zkjh\mvp\logs\scan2.txt","w").write("\n".join(res) if res else "none")
k.CloseHandle(ctypes.c_void_p(h))
