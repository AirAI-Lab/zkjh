# TF boot-card maker via WSL raw-mount + dd (ADMIN PowerShell required)
# ASCII-only. Usage: powershell -ExecutionPolicy Bypass -File make_sd_bootcard_wsl.ps1 [-Drive F]
# NOTE: wsl --mount requires the disk NOT in use -> we offline it first, online it at the end.
param([string]$Drive = 'F')
$ErrorActionPreference = 'Stop'

$part = Get-Partition -DriveLetter $Drive -ErrorAction Stop
$disk = Get-Disk -Number $part.DiskNumber
Write-Host ("Target: {0}: -> PhysicalDrive{1}  {2}  {3:N1}GB  partition-offset {4:N1}MB" -f $Drive,$disk.Number,$disk.FriendlyName,($disk.Size/1GB),($part.Offset/1MB))
if ($disk.BusType -ne 'USB') { throw "ABORT: not USB bus" }
if ($disk.Size -gt 64GB -or $disk.Size -lt 1GB) { throw "ABORT: size abnormal" }
if ($disk.IsBoot -or $disk.IsSystem) { throw "ABORT: boot/system disk!!" }
$confirm = Read-Host "Close Explorer windows on $Drive`: , then type yes to continue"
if ($confirm -ine 'yes') { throw "cancelled" }

$phys = "\\.\PHYSICALDRIVE" + $disk.Number
$n = $disk.Number

Write-Host "step1: taking disk $n offline (this unmounts $Drive`: temporarily)..."
Set-Disk -Number $n -IsOffline $true
Start-Sleep 1
if (-not (Get-Disk -Number $n).IsOffline) { throw "failed to offline disk $n (close any program using $Drive`:)" }

$mounted = $false
try {
  Write-Host "step2: wsl --mount bare..."
  wsl --mount $phys --bare
  if ($LASTEXITCODE -ne 0) { throw "wsl --mount failed (code $LASTEXITCODE). Try 'wsl --update' then rerun." }
  $mounted = $true
  Write-Host "step3: dd uboot to 17KB offset + verify (answer yes in WSL prompt)..."
  wsl -d Ubuntu -- bash /mnt/d/github/zkjh/mvp/scripts/wsl_dd_bootcard.sh ("{0:N1}" -f ($disk.Size/1GB))
  if ($LASTEXITCODE -ne 0) { throw "dd script failed (see messages above)" }
} finally {
  if ($mounted) { Write-Host "step4: wsl --unmount..."; wsl --unmount $phys | Out-Null; Start-Sleep 1 }
  Write-Host "step5: bringing disk $n back online..."
  Set-Disk -Number $n -IsOffline $false
  Start-Sleep 2
  $p2 = Get-Partition -DiskNumber $n -ErrorAction SilentlyContinue | Where-Object DriveLetter
  if ($p2) { Write-Host ("OK, disk back online as {0}:" -f $p2[0].DriveLetter) }
  else { Write-Host "disk online but no drive letter - replug the USB reader to get it back (card content is intact)" }
}
Write-Host "ALL DONE."