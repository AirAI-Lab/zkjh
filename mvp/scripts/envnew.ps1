$ErrorActionPreference = "Stop"
$out = "D:\github\zkjh\mvp\logs\envnew.txt"
"start" | Out-File $out -Encoding utf8
try {
  $cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RD4{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string n,uint a,uint s,IntPtr p,uint d,uint f,IntPtr t);}'
  Add-Type -TypeDefinition $cs
  [uint32]$acc = [uint32](2147483648 -bor 1073741824)
  $sfh = [RD4]::CreateFile("\\.\PhysicalDrive1", $acc, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
  if ($sfh.IsInvalid) { throw "openfail" }
  $fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)
  $orig = New-Object byte[] 1024
  $fs.Seek(211456,'Begin') | Out-Null
  $o=0; while($o -lt 1024){ $n=$fs.Read($orig,$o,1024-$o); if($n -le 0){break}; $o+=$n }
  # build new blob (326B total, pad with NULs)
  $na = [Text.Encoding]::ASCII.GetBytes("bootargs=console=ttyS1,115200n8 mem=41M@0x0 rmem=23M@0x2900000 rdinit=/linuxrc panic=999999999")
  $nc = [Text.Encoding]::ASCII.GetBytes("bootcmd=mmc read 0x80600000 0x1800 0x3000; fatload mmc 0 0x81000000 uInitrd; bootm 0x80600000 0x81000000")
  $kp = [Text.Encoding]::ASCII.GetBytes("bootdelay=1")
  $br = [Text.Encoding]::ASCII.GetBytes("baudrate=115200")
  $le = [Text.Encoding]::ASCII.GetBytes("loads_echo=1")
  $blob = New-Object byte[] 326
  $pos = 0
  foreach($part in @($na,$nc,$kp,$br,$le)){
    [Array]::Copy($part,0,$blob,$pos,$part.Length)
    $pos += $part.Length
    $blob[$pos] = 0; $pos++
  }
  # blob ends with double NUL (rest already zero)
  [Array]::Copy($blob,0,$orig,44,326)
  $fs.Seek(211456,'Begin') | Out-Null
  $fs.Write($orig,0,1024)
  $fs.Flush($true)
  $rb = New-Object byte[] 1024
  $fs.Seek(211456,'Begin') | Out-Null
  $o=0; while($o -lt 1024){ $n=$fs.Read($rb,$o,1024-$o); if($n -le 0){break}; $o+=$n }
  $same=$true; for($j=0;$j -lt 1024;$j++){ if($rb[$j] -ne $orig[$j]){$same=$false;break} }
  $txt = [Text.Encoding]::ASCII.GetString($rb[44..300]) -replace "[^\x20-\x7e]","|"
  "NEW-ENV 1024B SAME=$same" | Out-File $out -Append -Encoding utf8
  "content: $txt" | Out-File $out -Append -Encoding utf8
  $fs.Close()
} catch { "ERR: $_" | Out-File $out -Append -Encoding utf8 }
