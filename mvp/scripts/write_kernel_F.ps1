$ErrorActionPreference = "Stop"
$disk = Get-Disk -Number 1
if ($disk.FriendlyName -notmatch "Mass Storage") { throw "Disk1 is not TF reader!" }
$cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
Add-Type -TypeDefinition $cs
[uint32]$GR = 2147483648; [uint32]$GW = 1073741824
$access = [uint32]($GR -bor $GW)
$sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive1", $access, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
if ($sfh.IsInvalid) { throw "CreateFile failed" }
$fs = New-Object System.IO.FileStream($sfh, [System.IO.FileAccess]::ReadWrite, 3145728)

$ub = [System.IO.File]::ReadAllBytes("D:\github\zkjh\mvp\releases\uImage.jzlzma")
Write-Host ("kernel {0} bytes -> 3MB offset (block 6144)" -f $ub.Length)

$bak = "D:\github\zkjh\mvp\logs\sd_backup_kernel_area_disk1.bin"
$fs.Seek(3145728, 'Begin') | Out-Null
$bbuf = New-Object byte[] 6291456
$null = $fs.Read($bbuf, 0, 6291456)
[System.IO.File]::WriteAllBytes($bak, $bbuf)
Write-Host "backup 3-9MB done"

$fs.Seek(3145728, 'Begin') | Out-Null
$fs.Write($ub, 0, $ub.Length)
$fs.Flush()

$rb = New-Object byte[] $ub.Length
$fs.Seek(3145728, 'Begin') | Out-Null
$null = $fs.Read($rb, 0, $rb.Length)
$fs.Close()

if (-not (Compare-Object $ub $rb -SyncWindow 0)) {
  Write-Host "VERIFY OK - KERNEL @3MB READY"
  Write-Host "NEXT: eject -> insert to board -> J16 OPEN -> power cycle"
} else { throw "VERIFY FAILED" }
