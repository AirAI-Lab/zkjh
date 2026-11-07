$ErrorActionPreference="Stop"
$out="D:\github\zkjh\mvp\logs\magic.txt"
$cs='using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class R{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string n,uint a,uint s,IntPtr p,uint d,uint f,IntPtr t);}'
Add-Type -TypeDefinition $cs
$sfh=[R]::CreateFile("\\.\PhysicalDrive1",[uint32]2147483648,[uint32]3,[IntPtr]::Zero,[uint32]3,0,[IntPtr]::Zero)
$fs=New-Object IO.FileStream($sfh,[IO.FileAccess]::Read,512,$false)
$b=New-Object byte[] 16
foreach($o in @(17408,3145728)){
  $fs.Seek($o,'Begin')|Out-Null
  $null=$fs.Read($b,0,16)
  $hex=($b|ForEach-Object{$_.ToString("x2")}) -join " "
  "offset ${o}: $hex"|Out-File $out -Append -Encoding utf8
}
$fs.Close()
