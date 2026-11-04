# JKD-621-T23 TF 启动卡一键制作脚本（需管理员 PowerShell 运行）
# 作用: 将 Zeratul SD 启动 uboot(t23_sdcard_uboot_uart1.bin) 裸写到 TF 卡 17KB 偏移处
#       (官方《烧录说明》1.1 节: dd if=u-boot.bin of=/dev/sdb bs=1024 seek=17)
# 安全: 三重校验(USB总线/容量1~64GB/分区起始>=2MB) + 首先备份前4MB + 写后回读校验
# 用法(管理员): powershell -ExecutionPolicy Bypass -File make_sd_bootcard.ps1 [-Drive F]
param([string]$Drive = 'F')

$ErrorActionPreference = 'Stop'
$uboot = Join-Path $PSScriptRoot '..\releases\t23_sdcard_uboot_uart1.bin'
if (-not (Test-Path $uboot)) { throw "file not found: $uboot" }

# ---- 1. 定位与安全校验 ----
$part = Get-Partition -DriveLetter $Drive -ErrorAction Stop
$disk = Get-Disk -Number $part.DiskNumber
Write-Host ("目标: {0}: -> PhysicalDrive{1}  {2}  {3:N1}GB  分区起始 {4:N1}MB" -f $Drive, $disk.Number, $disk.FriendlyName, ($disk.Size/1GB), ($part.Offset/1MB))
if ($disk.BusType -ne 'USB')   { throw "ABORT safety check: not a USB bus device!" }
if ($disk.Size -gt 64GB -or $disk.Size -lt 1GB) { throw "ABORT safety check: abnormal size (expect 1-64GB TF card)!" }
if ($part.Offset -lt 2MB)      { throw "ABORT safety check: partition offset <2MB, write@17KB would corrupt FS!" }
$confirm = Read-Host "Confirm writing THIS card? type yes to continue"
if ($confirm -ine 'yes') { throw "cancelled by user" }

# ---- 2. 备份前 4MB ----
$bak = Join-Path $PSScriptRoot ("..\logs\sd_backup_disk{0}_{1}.bin" -f $disk.Number, (Get-Date -Format yyyyMMdd_HHmmss))
New-Item -ItemType Directory -Force -Path (Split-Path $bak) | Out-Null
$fs = [IO.File]::Open("\\.\PhysicalDrive" + $disk.Number, 'Open', 'Read', 'ReadWrite')
$buf = New-Object byte[] (4MB)
[void]$fs.Read($buf, 0, $buf.Length)
[IO.File]::WriteAllBytes($bak, $buf)
Write-Host "backup first 4MB -> $bak"

# ---- 3. 写 uboot 到 17KB 偏移 (17408 = 1024*17) ----
$ub = [IO.File]::ReadAllBytes($uboot)
Write-Host ("写入 {0} 字节 uboot @ 偏移 17408..." -f $ub.Length)
$fs.Seek(17408, 'Begin') | Out-Null
$fs.Write($ub, 0, $ub.Length)
$fs.Flush($true)

# ---- 4. 回读校验 ----
$fs.Seek(17408, 'Begin') | Out-Null
$rb = New-Object byte[] $ub.Length
[void]$fs.Read($rb, 0, $rb.Length)
$fs.Close()
if (@(Compare-Object $ub $rb -SyncWindow 0).Count -eq 0) {
  Write-Host "校验通过! 启动卡制作完成。" -ForegroundColor Green
  Write-Host ""
  Write-Host "=== 板上使用步骤 ==="
  Write-Host "1. 卡插入板子 TF 卡座, USB-TTL 接 J14(115200), 打开串口"
  Write-Host "2. 按住 BOOTSEL 上电 -> 进入 SD 卡启动 uboot(串口出命令行)"
  Write-Host "3. 串口依次执行:"
  Write-Host "   mw.b 0x80600000 0xff 0x1000000"
  Write-Host "   fatls mmc 0"
  Write-Host "   fatload mmc 0 0x80600000 ZRT_SOC_T23ZN_TP9950_DIRECT_FW.bin"
  Write-Host "   sf probe;sf erase 0x0 0x1000000;sf write 0x80600000 0x0 0x1000000"
  Write-Host "4. 完成后断电, 恢复 BOOTSEL, 重新上电即进入新系统"
} else { throw "readback verify FAILED! backup at $bak, DO NOT use this card, contact owner" }