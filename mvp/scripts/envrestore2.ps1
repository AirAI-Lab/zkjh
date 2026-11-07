$ErrorActionPreference = "Stop"
$out = "D:\github\zkjh\mvp\logs\envrestore2.txt"
"start" | Out-File $out -Encoding utf8
try {
  $cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RD3{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string n,uint a,uint s,IntPtr p,uint d,uint f,IntPtr t);}'
  Add-Type -TypeDefinition $cs
  [uint32]$acc = [uint32](2147483648 -bor 1073741824)
  $sfh = [RD3]::CreateFile("\\.\PhysicalDrive1", $acc, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
  if ($sfh.IsInvalid) { throw "openfail" }
  $fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)
  # read 2 sectors from 211456
  $orig = New-Object byte[] 1024
  $fs.Seek(211456,'Begin') | Out-Null
  $o=0; while($o -lt 1024){ $n=$fs.Read($orig,$o,1024-$o); if($n -le 0){break}; $o+=$n }
  # merge blob at offset 44
  $blob = [IO.File]::ReadAllBytes("D:\github\zkjh\mvp\logs\envblob_orig.bin")
  [Array]::Copy($blob,0,$orig,44,$blob.Length)
  # write back aligned
  $fs.Seek(211456,'Begin') | Out-Null
  $fs.Write($orig,0,1024)
  $fs.Flush($true)
  $rb = New-Object byte[] 1024
  $fs.Seek(211456,'Begin') | Out-Null
  $o=0; while($o -lt 1024){ $n=$fs.Read($rb,$o,1024-$o); if($n -le 0){break}; $o+=$n }
  $same=$true; for($j=0;$j -lt 1024;$j++){ if($rb[$j] -ne $orig[$j]){$same=$false;break} }
  "ALIGNED-RESTORE 1024B SAME=$same" | Out-File $out -Append -Encoding utf8
  $fs.Close()
} catch { "ERR: $_" | Out-File $out -Append -Encoding utf8 }
