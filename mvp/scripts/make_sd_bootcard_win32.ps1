# TF boot-card maker via Win32 raw write (ADMIN PowerShell required)
# Why: wsl --mount does NOT support USB SD readers (0x8007000f, by design);
#      .NET File.Open on raw device mis-queries Length -> EOF flag -> write fails;
#      fix = CreateFile -> SafeFileHandle -> FileStream(handle) (no Length query).
# Writes uboot to 17KB offset, sector-padded, backup + readback verify. ASCII only.
# Usage: powershell -ExecutionPolicy Bypass -File make_sd_bootcard_win32.ps1 [-Drive F]
param([string]$Drive = 'F')
$ErrorActionPreference = 'Stop'

$cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
if (-not ('RawDisk' -as [type])) { Add-Type -TypeDefinition $cs }

$uboot = Join-Path $PSScriptRoot '..\releases\t23_sdcard_uboot_uart1.bin'
if (-not (Test-Path $uboot)) { throw "file not found: $uboot" }
$part = Get-Partition -DriveLetter $Drive -ErrorAction Stop
$disk = Get-Disk -Number $part.DiskNumber
Write-Host ("Target: {0}: -> PhysicalDrive{1}  {2}  {3:N1}GB  partition-offset {4:N1}MB" -f $Drive,$disk.Number,$disk.FriendlyName,($disk.Size/1GB),($part.Offset/1MB))
if ($disk.BusType -ne 'USB') { throw "ABORT: not USB bus" }
if ($disk.Size -gt 64GB -or $disk.Size -lt 1GB) { throw "ABORT: size abnormal" }
if ($disk.IsBoot -or $disk.IsSystem) { throw "ABORT: boot/system disk!!" }
if ($part.Offset -lt 2MB) { throw "ABORT: partition offset <2MB" }
$confirm = Read-Host "Confirm writing THIS card? type yes to continue"
if ($confirm -ine 'yes') { throw "cancelled" }

[uint32]$GENERIC_READ  = 2147483648  # 0x80000000
[uint32]$GENERIC_WRITE = 1073741824  # 0x40000000
$access = [uint32]($GENERIC_READ -bor $GENERIC_WRITE)   # 0xC0000000
[uint32]$SHARE_RW = 3; [uint32]$OPEN_EXISTING = 3
$sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive"+$disk.Number, $access, $SHARE_RW, [IntPtr]::Zero, $OPEN_EXISTING, 0, [IntPtr]::Zero)
if ($sfh.IsInvalid) { throw ("CreateFile failed, Win32Error=" + [Runtime.InteropServices.Marshal]::GetLastWin32Error()) }
$fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)

try {
  $bak = Join-Path $PSScriptRoot ("..\logs\sd_backup_disk{0}_{1}.bin" -f $disk.Number, (Get-Date -Format yyyyMMdd_HHmmss))
  New-Item -ItemType Directory -Force -Path (Split-Path $bak) | Out-Null
  $fs.Seek(0,'Begin') | Out-Null
  $buf = New-Object byte[] (4MB)
  $off=0; while($off -lt $buf.Length){ $n=$fs.Read($buf,$off,$buf.Length-$off); if($n -le 0){break}; $off+=$n }
  [IO.File]::WriteAllBytes($bak,$buf); Write-Host "backup first 4MB -> $bak"

  $ub = [IO.File]::ReadAllBytes($uboot)
  $pad = [int](([math]::Ceiling($ub.Length/512))*512)
  $wb = New-Object byte[] $pad
  [Array]::Copy($ub,0,$wb,0,$ub.Length)
  for($i=$ub.Length;$i -lt $pad;$i++){ $wb[$i]=0xFF }
  Write-Host ("writing {0} bytes (padded {1}) uboot @ offset 17408 ..." -f $ub.Length,$pad)

  $fs.Seek(17408,'Begin') | Out-Null
  $fs.Write($wb,0,$wb.Length)
  $fs.Flush($true)

  $fs.Seek(17408,'Begin') | Out-Null
  $rb = New-Object byte[] $pad
  $off=0; while($off -lt $rb.Length){ $n=$fs.Read($rb,$off,$rb.Length-$off); if($n -le 0){break}; $off+=$n }
  $diff=0; for($i=0;$i -lt $ub.Length;$i++){ if($ub[$i] -ne $rb[$i]){$diff=1; break} }
  if ($diff -eq 0) {
    Write-Host "VERIFY OK - TF BOOT CARD READY" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== ON-BOARD BURN STEPS ==="
    Write-Host "1. insert card into board TF slot, USB-TTL on J14 (115200-8N1), open serial"
    Write-Host "2. hold BOOTSEL then power on -> SD-boot uboot console on serial"
    Write-Host "3. run in serial console:"
    Write-Host "   mw.b 0x80600000 0xff 0x1000000"
    Write-Host "   fatls mmc 0"
    Write-Host "   fatload mmc 0 0x80600000 ZRT_SOC_T23ZN_TP9950_DIRECT_FW.bin"
    Write-Host "   sf probe;sf erase 0x0 0x1000000;sf write 0x80600000 0x0 0x1000000"
    Write-Host "4. power off, release BOOTSEL, power on -> new TP9950 system"
  } else { throw "readback verify FAILED! backup at $bak" }
} finally {
  $fs.Close(); $sfh.Close()
}