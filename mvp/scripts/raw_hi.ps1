$ErrorActionPreference="Stop"
$out="D:\github\zkjh\mvp\logs\raw_hi.txt"
try{
$cs='using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RD6{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string n,uint a,uint s,IntPtr p,uint d,uint f,IntPtr t);}'
Add-Type -TypeDefinition $cs
[uint32]$acc=[uint32](2147483648 -bor 1073741824)
$sfh=[RD6]::CreateFile("\\.\PhysicalDrive1",$acc,[uint32]3,[IntPtr]::Zero,[uint32]3,0,[IntPtr]::Zero)
if($sfh.IsInvalid){throw "open"}
$fs=New-Object IO.FileStream($sfh,[IO.FileAccess]::ReadWrite,512,$false)
$data=[IO.File]::ReadAllBytes("D:\github\zkjh\mvp\releases\uImage-hardinitrd-lzma.bin")
$pad=[int](([math]::Ceiling($data.Length/512))*512)
$wb=New-Object byte[] $pad
[Array]::Copy($data,0,$wb,0,$data.Length)
for($i=$data.Length;$i -lt $pad;$i++){$wb[$i]=0xFF}
$fs.Seek(3145728,'Begin')|Out-Null
$fs.Write($wb,0,$wb.Length)
$fs.Flush($true)
$rb=New-Object byte[] $data.Length
$fs.Seek(3145728,'Begin')|Out-Null
$o=0;while($o -lt $data.Length){$n=$fs.Read($rb,$o,$data.Length-$o);if($n -le 0){break};$o+=$n}
$same=$true;for($j=0;$j -lt $data.Length;$j++){if($rb[$j] -ne $data[$j]){$same=$false;break}}
"HARDINITRD $($data.Length)B @3MB VERIFIED=$same"|Out-File $out -Encoding utf8
$fs.Close()
}catch{"ERR: $_"|Out-File $out -Encoding utf8}
