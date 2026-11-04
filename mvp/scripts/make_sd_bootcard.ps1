# JKD-621-T23 TF boot-card maker (run in ADMIN PowerShell)
# Writes Zeratul SD-boot uboot to 17KB offset on TF card (official Burning Guide 1.1:
#   dd if=u-boot.bin of=/dev/sdb bs=1024 seek=17)
# Safety: 3 checks (USB bus / size 1-64GB / partition offset >=2MB) + backup first 4MB
#         + readback verify.  ASCII-only on purpose (PS5.1 GBK safe).
# Usage:  powershell -ExecutionPolicy Bypass -File make_sd_bootcard.ps1 [-Drive F]
param([string]$Drive = 'F')

$ErrorActionPreference = 'Stop'
$uboot = Join-Path $PSScriptRoot '..\releases\t23_sdcard_uboot_uart1.bin'
if (-not (Test-Path $uboot)) { throw "file not found: $uboot" }

# ---- 1. locate + safety checks ----
$part = Get-Partition -DriveLetter $Drive -ErrorAction Stop
$disk = Get-Disk -Number $part.DiskNumber
Write-Host ("Target: {0}: -> PhysicalDrive{1}  {2}  {3:N1}GB  partition-offset {4:N1}MB" -f $Drive, $disk.Number, $disk.FriendlyName, ($disk.Size/1GB), ($part.Offset/1MB))
if ($disk.BusType -ne 'USB') { throw "ABORT safety check: not a USB bus device!" }
if ($disk.Size -gt 64GB -or $disk.Size -lt 1GB) { throw "ABORT safety check: abnormal size (expect 1-64GB TF card)!" }
if ($part.Offset -lt 2MB) { throw "ABORT safety check: partition offset <2MB, write@17KB would corrupt filesystem!" }
$confirm = Read-Host "Confirm writing THIS card? type yes to continue"
if ($confirm -ine 'yes') { throw "cancelled by user" }

# ---- 2. backup first 4MB ----
$bak = Join-Path $PSScriptRoot ("..\logs\sd_backup_disk{0}_{1}.bin" -f $disk.Number, (Get-Date -Format yyyyMMdd_HHmmss))
New-Item -ItemType Directory -Force -Path (Split-Path $bak) | Out-Null
$fs = [IO.File]::Open("\\.\PhysicalDrive" + $disk.Number, 'Open', 'Read', 'ReadWrite')
$buf = New-Object byte[] (4MB)
[void]$fs.Read($buf, 0, $buf.Length)
[IO.File]::WriteAllBytes($bak, $buf)
Write-Host "backup first 4MB -> $bak"

# ---- 3. write uboot at 17KB offset (17408 = 1024*17) ----
$ub = [IO.File]::ReadAllBytes($uboot)
Write-Host ("writing {0} bytes uboot @ offset 17408 ..." -f $ub.Length)
$fs.Seek(17408, 'Begin') | Out-Null
$fs.Write($ub, 0, $ub.Length)
$fs.Flush($true)

# ---- 4. readback verify ----
$fs.Seek(17408, 'Begin') | Out-Null
$rb = New-Object byte[] $ub.Length
[void]$fs.Read($rb, 0, $rb.Length)
$fs.Close()
if (@(Compare-Object $ub $rb -SyncWindow 0).Count -eq 0) {
  Write-Host "VERIFY OK - TF boot card is READY." -ForegroundColor Green
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
} else { throw "readback verify FAILED! backup at $bak, DO NOT use this card, contact owner" }