import ctypes, ctypes.wintypes as wt, sys
k=ctypes.windll.kernel32
k.CreateFileW.restype=ctypes.c_void_p
k.CreateFileW.argtypes=[ctypes.c_wchar_p,wt.DWORD,wt.DWORD,ctypes.c_void_p,wt.DWORD,wt.DWORD,ctypes.c_void_p]
k.SetFilePointer.argtypes=[ctypes.c_void_p,wt.LONG,ctypes.POINTER(wt.LONG),wt.DWORD]
k.ReadFile.argtypes=[ctypes.c_void_p,ctypes.c_void_p,wt.DWORD,ctypes.POINTER(wt.DWORD),ctypes.c_void_p]
k.CloseHandle.argtypes=[ctypes.c_void_p]
h=k.CreateFileW(r"\\.\PhysicalDrive1",0x80000000,3,None,3,0,None)
err=ctypes.GetLastError()
res="h=%r err=%d\n"%(h,err)
if not h or h==0xFFFFFFFFFFFFFFFF:
    open(r"D:\github\zkjh\mvp\logs\scan3.txt","w").write(res+"OPENFAIL"); sys.exit()
found=[]
CH=4*1024*1024
spots=list(range(0,48*1024*1024,CH))+[31954305024-x for x in (4*1024*1024,8*1024*1024,16*1024*1024,33*1024*1024)]
for pos in spots:
    buf=ctypes.create_string_buffer(CH); rd=wt.DWORD(0)
    hi=ctypes.c_long((pos>>32)&0x7FFFFFFF); lo=pos&0xFFFFFFFF
    k.SetFilePointer(h,lo,ctypes.byref(hi),0)
    k.ReadFile(h,buf,CH,ctypes.byref(rd),None)
    d=buf.raw[:rd.value]
    for pat in (b"panic=5",b"panic=999",b"bootargs=console",b"bootcmd=mmc"):
        i=d.find(pat)
        while i>=0:
            seg=d[max(0,i-64):i+220]
            txt="".join(chr(c) if 32<=c<127 else "|" for c in seg)
            found.append("pos=%d(0x%X) pat=%s abs=%d\n%s"%(pos,pos,pat.decode(),pos+i,txt))
            i=d.find(pat,i+1)
res+=("\n".join(found) if found else "NONE")+"\n"
open(r"D:\github\zkjh\mvp\logs\scan3.txt","w").write(res)
k.CloseHandle(h)
