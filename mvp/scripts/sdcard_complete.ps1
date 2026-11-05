# JKD-621-T23 SD Boot Card - Complete Script (ADMIN REQUIRED)
# Step 1: Repartition F: (4MB offset)  Step 2: Copy files  Step 3: Write uboot@17KB
$ErrorActionPreference = 'Stop'
$log = 'D:\github\zkjh\mvp\logs\sdcard_setup.log'

Function Log($msg) {
    $ts = Get-Date -Format 'HH:mm:ss'
    Write-Host "[$ts] $msg"
    Add-Content -Path $log -Value "[$ts] $msg"
}

Log "=== START ==="

# --- Verify target disk ---
$part = Get-Partition -DriveLetter F -ErrorAction Stop
$disk = Get-Disk -Number $part.DiskNumber
Log "Target: F: -> PhysicalDrive$($disk.Number) $($disk.FriendlyName) $([math]::Round($disk.Size/1GB,1))GB"
if ($disk.BusType -ne 'USB') { Log "ABORT: not USB"; exit 1 }
if ($disk.Size -gt 64GB -or $disk.Size -lt 1GB) { Log "ABORT: size"; exit 1 }
if ($disk.IsBoot -or $disk.IsSystem) { Log "ABORT: system disk"; exit 1 }
Log "Safety checks PASSED"

# --- Step 1: Repartition with 4MB offset ---
Log "Step 1: Repartitioning (clean + create @4MB + FAT32)..."
$dpScript = @"
select disk $($disk.Number)
clean
create partition primary offset=4096
format fs=fat32 quick label=BOOTCARD
assign letter=F
"@
$dpScript | Out-File "$env:TEMP\dp_script.txt" -Encoding ASCII
$dpResult = diskpart /s "$env:TEMP\dp_script.txt" 2>&1
Log "diskpart: $($dpResult | Out-String)"
Start-Sleep 2

# Verify new partition
$part2 = Get-Partition -DriveLetter F -ErrorAction Stop
Log "New partition offset: $($part2.Offset) bytes ($([math]::Round($part2.Offset/1MB,1))MB)"
if ($part2.Offset -lt 2MB) { Log "ABORT: partition still <2MB"; exit 1 }

# --- Step 2: Copy files ---
Log "Step 2: Copying files..."
Copy-Item 'D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin' 'F:\' -Force
Copy-Item 'D:\github\zkjh\mvp\releases\ZRT_SOC_T23ZN_TP9950_DEBUG_FW.bin' 'F:\' -Force
$files = Get-ChildItem 'F:\' | Select-Object Name, Length
Log "Files on card: $($files | Out-String)"

# --- Step 3: Write uboot at 17KB ---
Log "Step 3: Writing uboot at 17KB offset..."

$cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
if (-not ('RawDisk' -as [type])) { Add-Type -TypeDefinition $cs }

$uboot = 'D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin'
if (-not (Test-Path $uboot)) { Log "ABORT: uboot not found"; exit 1 }

[uint32]$GENERIC_READ = 2147483648
[uint32]$GENERIC_WRITE = 1073741824
$access = [uint32]($GENERIC_READ -bor $GENERIC_WRITE)
[uint32]$SHARE_RW = 3
[uint32]$OPEN_EXISTING = 3

$sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive" + $disk.Number, $access, $SHARE_RW, [IntPtr]::Zero, $OPEN_EXISTING, 0, [IntPtr]::Zero)
if ($sfh.IsInvalid) { Log "ABORT: CreateFile failed"; exit 1 }
$fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)

try {
    # Backup
    $bak = "D:\github\zkjh\mvp\logs\sd_backup_disk$($disk.Number)_$(Get-Date -Format yyyyMMdd_HHmmss).bin"
    $fs.Seek(0,'Begin') | Out-Null
    $buf = New-Object byte[] (4MB)
    $off = 0; while($off -lt $buf.Length){ $n=$fs.Read($buf,$off,$buf.Length-$off); if($n -le 0){break}; $off+=$n }
    [IO.File]::WriteAllBytes($bak,$buf)
    Log "Backup 4MB -> $bak"

    # Pad uboot to 512 multiple
    $ub = [IO.File]::ReadAllBytes($uboot)
    $pad = [int](([math]::Ceiling($ub.Length/512))*512)
    $wb = New-Object byte[] $pad
    [Array]::Copy($ub,0,$wb,0,$ub.Length)
    for($i=$ub.Length;$i -lt $pad;$i++){ $wb[$i]=0xFF }
    Log "Writing $($ub.Length) bytes (padded $pad) @ offset 17408..."

    # Write
    $fs.Seek(17408,'Begin') | Out-Null
    $fs.Write($wb,0,$wb.Length)
    $fs.Flush($true)

    # Verify
    $fs.Seek(17408,'Begin') | Out-Null
    $rb = New-Object byte[] $pad
    $off = 0; while($off -lt $rb.Length){ $n=$fs.Read($rb,$off,$rb.Length-$off); if($n -le 0){break}; $off+=$n }
    $diff = 0; for($i=0;$i -lt $ub.Length;$i++){ if($ub[$i] -ne $rb[$i]){$diff=1;break} }

    if ($diff -eq 0) {
        Log "VERIFY OK - TF BOOT CARD READY"
        Log "=== ALL DONE ==="
        Log "Next: insert card into board, short J16, power on"
    } else {
        Log "VERIFY FAILED!"
        exit 1
    }
} finally {
    $fs.Close(); $sfh.Close()
}