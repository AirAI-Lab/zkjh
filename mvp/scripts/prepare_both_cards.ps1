# Prepare BOTH TF cards for cross-testing (ADMIN REQUIRED)
# G: (7.5GB) - verify uboot@17KB, copy files
# F: (58.2GB) - repartition + write uboot + copy files
$ErrorActionPreference = 'Stop'

# --- Helper: Win32 raw disk ---
$cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
if (-not ('RawDisk' -as [type])) { Add-Type -TypeDefinition $cs }

$ubootPath = 'D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin'
$fwPath = 'D:\github\zkjh\mvp\releases\ZRT_SOC_T23ZN_TP9950_DEBUG_FW.bin'
$ub = [IO.File]::ReadAllBytes($ubootPath)

# --- Prepare Card G: (7.5GB, Disk2) - Verify uboot ---
Write-Host "`n===== G: (7.5GB) - Verify & Fix =====" -ForegroundColor Cyan
$gPart = Get-Partition -DriveLetter G -ErrorAction SilentlyContinue
if ($gPart) {
    $gDisk = Get-Disk -Number $gPart.DiskNumber
    Write-Host "G: = Disk$($gDisk.Number) $($gDisk.FriendlyName) $([math]::Round($gDisk.Size/1GB,1))GB offset=$([math]::Round($gPart.Offset/1MB,1))MB"
    if ($gPart.Offset -ge 2MB) {
        # Read 17KB and verify
        $sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive" + $gDisk.Number, [uint32]3221225472, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
        $fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)
        $fs.Seek(17408, 'Begin') | Out-Null
        $rb = New-Object byte[] 512
        $n = 0; while($n -lt 512){ $r=$fs.Read($rb,$n,512-$n); if($r -le 0){break}; $n+=$r }
        $fs.Close(); $sfh.Close()
        $match = $true
        for($i=0; $i -lt [Math]::Min(512,$ub.Length); $i++){
            if($ub[$i] -ne $rb[$i]){ $match=$false; break }
        }
        if ($match) {
            Write-Host "  Uboot@17KB: VERIFIED OK" -ForegroundColor Green
        } else {
            Write-Host "  Uboot@17KB: MISSING, rewriting..." -ForegroundColor Yellow
            # Write uboot
            $sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive" + $gDisk.Number, [uint32]3221225472, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
            $fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)
            $pad = [int](([math]::Ceiling($ub.Length/512))*512)
            $wb = New-Object byte[] $pad
            [Array]::Copy($ub,0,$wb,0,$ub.Length)
            for($i=$ub.Length;$i -lt $pad;$i++){ $wb[$i]=0xFF }
            $fs.Seek(17408,'Begin') | Out-Null
            $fs.Write($wb,0,$wb.Length)
            $fs.Flush($true)
            $fs.Close(); $sfh.Close()
            Write-Host "  Uboot@17KB: WRITTEN" -ForegroundColor Green
        }
        # Ensure files
        Copy-Item $ubootPath 'G:\' -Force
        Copy-Item $fwPath 'G:\' -Force
        Write-Host "  Files: OK"
        Write-Host "  G: READY!" -ForegroundColor Green
    } else {
        Write-Host "  ERROR: partition offset < 2MB, needs repartition"
    }
} else {
    Write-Host "  G: not found!"
}

# --- Prepare Card F: (58.2GB, Disk1) - Full setup ---
Write-Host "`n===== F: (58.2GB) - Full Setup =====" -ForegroundColor Cyan
$fPart = Get-Partition -DriveLetter F -ErrorAction SilentlyContinue
if ($fPart) {
    $fDisk = Get-Disk -Number $fPart.DiskNumber
    Write-Host "F: = Disk$($fDisk.Number) $($fDisk.FriendlyName) $([math]::Round($fDisk.Size/1GB,1))GB offset=$([math]::Round($fPart.Offset/1MB,1))MB"

    $confirm = Read-Host "Repartition F: (Disk$($fDisk.Number))? type yes"
    if ($confirm -ine 'yes') { Write-Host "Skipped F:"; exit }

    # Repartition
    Write-Host "  Repartitioning..."
    $dpScript = @"
select disk $($fDisk.Number)
clean
create partition primary offset=4096
format fs=fat32 quick label=TESTCARD
assign letter=F
"@
    $dpScript | Out-File "$env:TEMP\dp_f.txt" -Encoding ASCII
    diskpart /s "$env:TEMP\dp_f.txt" | Out-Null
    Start-Sleep 2

    # Write uboot at 17KB
    Write-Host "  Writing uboot@17KB..."
    $sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive" + $fDisk.Number, [uint32]3221225472, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
    $fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)
    $pad = [int](([math]::Ceiling($ub.Length/512))*512)
    $wb = New-Object byte[] $pad
    [Array]::Copy($ub,0,$wb,0,$ub.Length)
    for($i=$ub.Length;$i -lt $pad;$i++){ $wb[$i]=0xFF }
    $fs.Seek(17408,'Begin') | Out-Null
    $fs.Write($wb,0,$wb.Length)
    $fs.Flush($true)

    # Verify
    $fs.Seek(17408,'Begin') | Out-Null
    $rb2 = New-Object byte[] $pad
    $off=0; while($off -lt $rb2.Length){ $n2=$fs.Read($rb2,$off,$rb2.Length-$off); if($n2 -le 0){break}; $off+=$n2 }
    $fs.Close(); $sfh.Close()
    $ok = $true
    for($i=0;$i -lt $ub.Length;$i++){ if($ub[$i] -ne $rb2[$i]){$ok=$false;break} }
    if ($ok) {
        Write-Host "  Uboot: VERIFIED" -ForegroundColor Green
    } else {
        Write-Host "  Uboot: VERIFY FAILED!" -ForegroundColor Red
    }

    # Copy files
    Copy-Item $ubootPath 'F:\' -Force
    Copy-Item $fwPath 'F:\' -Force
    Write-Host "  Files: OK"
    Write-Host "  F: READY!" -ForegroundColor Green
} else {
    Write-Host "  F: not found!"
}

Write-Host "`n===== SUMMARY ====="
Get-ChildItem 'F:\','G:\' -ErrorAction SilentlyContinue | Select-Object @{n='Card';e={$_.PSDrive.Name}}, Name, Length | Format-Table -AutoSize
Write-Host "Both cards ready for cross-testing!"