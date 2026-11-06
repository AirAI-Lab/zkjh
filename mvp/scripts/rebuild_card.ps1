$ErrorActionPreference = "Stop"
$out = "D:\github\zkjh\mvp\logs\rebuild_card_result.txt"
"start $(Get-Date -Format T)" | Out-File $out -Encoding utf8
try {
  # 1. repartition via diskpart
  diskpart /s D:\github\zkjh\mvp\scripts\repartition_f.txt | Out-File $out -Append -Encoding utf8
  Start-Sleep 3
  # 2. raw write uboot@17KB + kernel@3MB
  $cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
  Add-Type -TypeDefinition $cs
  [uint32]$access = [uint32](2147483648 -bor 1073741824)
  $sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive1", $access, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
  if ($sfh.IsInvalid) { $e=[Runtime.InteropServices.Marshal]::GetLastWin32Error(); throw "CreateFile err=$e" }
  $fs = New-Object System.IO.FileStream($sfh, [System.IO.FileAccess]::ReadWrite, 3145728)
  function Write-Block([byte[]]$data, [long]$off, [string]$name) {
    $fs.Seek($off, 'Begin') | Out-Null
    $fs.Write($data, 0, $data.Length)
    $fs.Flush()
    $rb = New-Object byte[] $data.Length
    $fs.Seek($off, 'Begin') | Out-Null
    $null = $fs.Read($rb, 0, $rb.Length)
    if (Compare-Object $data $rb -SyncWindow 0) { throw "$name VERIFY FAILED" }
    "$name $($data.Length)B @offset $off : OK" | Out-File $out -Append -Encoding utf8
  }
  $ub = [System.IO.File]::ReadAllBytes("D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin")
  Write-Block $ub 17408 "uboot"
  $kern = [System.IO.File]::ReadAllBytes("D:\github\zkjh\mvp\releases\uImage.jzlzma")
  Write-Block $kern 3145728 "kernel"
  $fs.Close()
  # 3. copy FAT files for future debugging
  Copy-Item D:\github\zkjh\mvp\releases\u-boot-with-spl.bin F:\ -Force
  Copy-Item D:\github\zkjh\mvp\releases\ZRT_SOC_T23ZN_GC2053_UNDIRECT_NOPQUIET_FW.bin F:\ -Force
  "FAT files copied" | Out-File $out -Append -Encoding utf8
  "ALL DONE" | Out-File $out -Append -Encoding utf8
} catch { "ERROR: $_" | Out-File $out -Append -Encoding utf8 }
