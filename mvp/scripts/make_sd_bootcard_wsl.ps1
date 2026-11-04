# TF boot-card maker via WSL raw-mount + dd (ADMIN PowerShell required)
# ASCII-only. Usage: powershell -ExecutionPolicy Bypass -File make_sd_bootcard_wsl.ps1 [-Drive F]
param([string]$Drive = 'F')
$ErrorActionPreference = 'Stop'

$part = Get-Partition -DriveLetter $Drive -ErrorAction Stop
$disk = Get-Disk -Number $part.DiskNumber
Write-Host ("Target: {0}: -> PhysicalDrive{1}  {2}  {3:N1}GB  partition-offset {4:N1}MB" -f $Drive,$disk.Number,$disk.FriendlyName,($disk.Size/1GB),($part.Offset/1MB))
if ($disk.BusType -ne 'USB') { throw "ABORT: not USB bus" }
if ($disk.Size -gt 64GB -or $disk.Size -lt 1GB) { throw "ABORT: size abnormal" }
$confirm = Read-Host "Confirm writing THIS card? type yes to continue"
if ($confirm -ine 'yes') { throw "cancelled" }

$phys = "\\.\PHYSICALDRIVE" + $disk.Number
wsl --mount $phys --bare
if ($LASTEXITCODE -ne 0) { throw "wsl --mount failed (try: wsl --update). Card NOT touched." }
try {
  wsl -d Ubuntu -- bash /mnt/d/github/zkjh/mvp/scripts/wsl_dd_bootcard.sh ("{0:N1}" -f ($disk.Size/1GB))
  if ($LASTEXITCODE -ne 0) { throw "dd script failed (see above). Card gap area only, backup exists." }
} finally {
  wsl --unmount $phys | Out-Null
}
Write-Host "Done. Drive $Drive`:\ is back in Windows."