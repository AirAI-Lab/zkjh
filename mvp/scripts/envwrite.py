import ctypes, ctypes.wintypes as wt, zlib
k=ctypes.windll.kernel32
h=k.CreateFileW(r"\\.\PhysicalDrive1",0xC0000000,3,None,3,0,None)
if h in (-1,0xFFFFFFFFFFFFFFFF):
    open(r"D:\github\zkjh\mvp\logs\envwrite.txt","w").write("open fail %d"%ctypes.GetLastError()); raise SystemExit
buf=ctypes.create_string_buffer(16*1024*1024); read=wt.DWORD(0)
k.ReadFile(h,buf,len(buf),ctypes.byref(read),None)
data=bytearray(buf.raw[:read.value])
i=data.find(b"bootargs=")
j=data.find(b"\x00\x00", i)   # end of env blob (double NUL)
orig=data[i:j+2]
open(r"D:\github\zkjh\mvp\logs\envblob_orig.bin","wb").write(bytes(orig))
# build new blob: new args + new cmd + keep others minus network items
new_args=b"bootargs=console=ttyS1,115200n8 mem=41M@0x0 rmem=23M@0x2900000 rdinit=/linuxrc panic=999999999\x00"
new_cmd=b"bootcmd=mmc read 0x80600000 0x1800 0x3000; fatload mmc 0 0x81000000 uInitrd; bootm 0x80600000 0x81000000\x00"
# keep: bootdelay, baudrate, loads_echo (drop ethaddr/ipaddr/serverip/gatewayip/netmask to save space)
keep=b"bootdelay=1\x00baudrate=115200\x00loads_echo=1\x00"
newblob=new_args+new_cmd+keep
oldlen=len(orig)
padn=oldlen-len(newblob)-2
if padn<0:
    open(r"D:\github\zkjh\mvp\logs\envwrite.txt","w").write("TOO LONG new=%d old=%d"%(len(newblob),oldlen)); k.CloseHandle(h); raise SystemExit
newblob=newblob+b"\x00"*padn+b"\x00\x00"
assert len(newblob)==oldlen
data[i:i+oldlen]=newblob
# write back
wrote=wt.DWORD(0)
k.SetFilePointer(h,i,None,0)
ok=k.WriteFile(h,bytes(newblob),len(newblob),ctypes.byref(wrote),None)
res="i=%d oldlen=%d newlen=%d wrote=%d ok=%d\n"%(i,oldlen,len(newblob),wrote.value,ok)
# verify
k.SetFilePointer(h,i,None,0)
rb=ctypes.create_string_buffer(oldlen); r2=wt.DWORD(0)
k.ReadFile(h,rb,oldlen,ctypes.byref(r2),None)
res+="verify_same=%s\n"%(rb.raw==newblob)
res+=newblob[:300].decode("ascii","replace")
open(r"D:\github\zkjh\mvp\logs\envwrite.txt","w").write(res)
k.CloseHandle(h)
