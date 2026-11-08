$ErrorActionPreference="Stop"
$out="D:\github\zkjh\mvp\logs\verify_hi.txt"
try{
$cs='using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RD7{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string n,uint a,uint s,IntPtr p,uint d,uint f,IntPtr t);}'
Add-Type -TypeDefinition $cs
$sfh=[RD7]::CreateFile("\\.\PhysicalDrive1",[uint32]2147483648,[uint32]3,[IntPtr]::Zero,[uint32]3,0,[IntPtr]::Zero)
if($sfh.IsInvalid){throw "open"}
$fs=New-Object IO.FileStream($sfh,[IO.FileAccess]::Read,512,$false)
$rb=New-Object byte[] 4096
$fs.Seek(3145728,'Begin')|Out-Null
$n=$fs.Read($rb,0,4096)
$hex=($rb[0..31]|ForEach-Object{$_.ToString("x2")}) -join " "
"first32: $hex"|Out-File $out -Encoding utf8
$src=[IO.File]::ReadAllBytes("D:\github\zkjh\mvp\releases\uImage-hardinitrd-lzma.bin")
$same=$true;for($j=0;$j -lt [Math]::Min(4096,$src.Length);$j++){if($rb[$j] -ne $src[$j]){$same=$false;break}}
"head4k match: $same (src len $($src.Length))"|Out-File $out -Append -Encoding utf8
$fs.Close()
}catch{"ERR: $_"|Out-File $out -Encoding utf8}

