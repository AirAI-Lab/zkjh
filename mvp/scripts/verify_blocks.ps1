$ErrorActionPreference = "Stop"
$out = "D:\github\zkjh\mvp\logs\verify_blocks_result.txt"
"verify $(Get-Date -Format T)" | Out-File $out -Encoding utf8
try {
  $cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
  Add-Type -TypeDefinition $cs
  [uint32]$access = [uint32](2147483648 -bor 1073741824)
  $sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive1", $access, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
  if ($sfh.IsInvalid) { throw "CreateFile failed" }
  $fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $true)

  function Read-Block([long]$off, [int]$len, [string]$name) {
    $buf = New-Object byte[] $len
    $fs.Seek($off,'Begin') | Out-Null
    $got=0; while($got -lt $len){ $n=$fs.Read($buf,$got,$len-$got); if($n -le 0){break}; $got+=$n }
    $md5 = [System.Security.Cryptography.MD5]::Create()
    $h = ($md5.ComputeHash($buf,0,$len) | ForEach-Object { $_.ToString("x2") }) -join ""
    "$name read ${got}B md5=$h" | Out-File $out -Append -Encoding utf8
    return $h
  }

  $h1 = Read-Block 17408 240792 "card@17KB "
  $src1 = [IO.File]::ReadAllBytes("D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin")
  $m = [System.Security.Cryptography.MD5]::Create()
  $s1 = ($m.ComputeHash($src1) | ForEach-Object { $_.ToString("x2") }) -join ""
  "src uboot  md5=$s1  MATCH=$($h1 -eq $s1)" | Out-File $out -Append -Encoding utf8

  $h2 = Read-Block 3145728 2500120 "card@3MB   "
  $src2 = [IO.File]::ReadAllBytes("D:\github\zkjh\mvp\releases\uImage.jzlzma")
  $s2 = ($m.ComputeHash($src2) | ForEach-Object { $_.ToString("x2") }) -join ""
  "src kernel md5=$s2  MATCH=$($h2 -eq $s2)" | Out-File $out -Append -Encoding utf8
  $fs.Close()
  "VERIFY COMPLETE" | Out-File $out -Append -Encoding utf8
} catch { "ERROR: $_" | Out-File $out -Append -Encoding utf8 }


