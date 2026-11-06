$ErrorActionPreference = "Stop"
$out = "D:\github\zkjh\mvp\logs\check_card_result.txt"
"check $(Get-Date -Format T)" | Out-File $out -Encoding utf8
try {
  $cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
  Add-Type -TypeDefinition $cs
  [uint32]$access = [uint32](2147483648 -bor 1073741824)
  $sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive1", $access, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
  if ($sfh.IsInvalid) { throw "open failed" }
  $fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)
  function Magic([long]$off, [int]$len, [string]$name) {
    $buf = New-Object byte[] $len
    $fs.Seek($off,'Begin') | Out-Null
    $got=0; while($got -lt $len){ $n=$fs.Read($buf,$got,$len-$got); if($n -le 0){break}; $got+=$n }
    $hex = ($buf | ForEach-Object { $_.ToString("x2") }) -join " "
    "$name @offset ${off}: $hex" | Out-File $out -Append -Encoding utf8
  }
  Magic 17408 16 "raw17KB(expect 4c 50 53 4d LPSM)"
  Magic 3145728 16 "raw3MB(expect 27 05 19 56 uImage)"
  $fs.Close()
  "CHECK DONE" | Out-File $out -Append -Encoding utf8
} catch { "ERROR: $_" | Out-File $out -Append -Encoding utf8 }
