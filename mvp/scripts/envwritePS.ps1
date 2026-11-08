$ErrorActionPreference="Stop"
$out="D:\github\zkjh\mvp\logs\envwritePS.txt"
try{
$cs='using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RD5{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string n,uint a,uint s,IntPtr p,uint d,uint f,IntPtr t);}'
Add-Type -TypeDefinition $cs
[uint32]$acc=[uint32](2147483648 -bor 1073741824)
$sfh=[RD5]::CreateFile("\\.\PhysicalDrive1",$acc,[uint32]3,[IntPtr]::Zero,[uint32]3,0,[IntPtr]::Zero)
if($sfh.IsInvalid){throw "open"}
$fs=New-Object IO.FileStream($sfh,[IO.FileAccess]::ReadWrite,512,$false)
$data=[IO.File]::ReadAllBytes("D:\github\zkjh\mvp\logs\env_new_blob.bin")
$fs.Seek(263168,'Begin')|Out-Null
$fs.Write($data,0,$data.Length)
$fs.Flush($true)
$rb=New-Object byte[] $data.Length
$fs.Seek(263168,'Begin')|Out-Null
$o=0;while($o -lt $data.Length){$n=$fs.Read($rb,$o,$data.Length-$o);if($n -le 0){break};$o+=$n}
$same=$true;for($j=0;$j -lt $data.Length;$j++){if($rb[$j] -ne $data[$j]){$same=$false;break}}
"ENVFINAL $($data.Length)B SAME=$same"|Out-File $out -Encoding utf8
$txt=[Text.Encoding]::ASCII.GetString($rb[4..320]) -replace "[^\x20-\x7e]","|"
"content: $txt"|Out-File $out -Append -Encoding utf8
$fs.Close()
}catch{"ERR: $_"|Out-File $out -Encoding utf8}
