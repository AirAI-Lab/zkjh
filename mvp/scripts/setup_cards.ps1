# Prepare both TF cards (ADMIN) - write uboot@17KB + copy firmware
$ErrorActionPreference = 'Stop'
$cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
if (-not ('RawDisk' -as [type])) { Add-Type -TypeDefinition $cs }
$ub = [IO.File]::ReadAllBytes('D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin')
$pad = [int](([math]::Ceiling($ub.Length/512))*512)
$wb = New-Object byte[] $pad
[Array]::Copy($ub,0,$wb,0,$ub.Length)
for($i=$ub.Length;$i -lt $pad;$i++){ $wb[$i]=0xFF }

foreach ($dl in @('F','G')) {
    $part = Get-Partition -DriveLetter $dl -ErrorAction SilentlyContinue
    if (-not $part) { Write-Host "${dl}: not found"; continue }
    $disk = Get-Disk -Number $part.DiskNumber
    $sz = [math]::Round($disk.Size/1GB,1)
    Write-Host "`n===== ${dl}: ($sz GB, Disk$($disk.Number)) ====="

    if ($disk.BusType -ne 'USB') { Write-Host "  SKIP: not USB"; continue }
    if ($part.Offset -lt 2MB) { Write-Host "  SKIP: offset < 2MB"; continue }

    # Write uboot
    Write-Host "  Writing uboot $($ub.Length)B @ 17KB..."
    $sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive"+$disk.Number, [uint32]3221225472, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
    $fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)
    $fs.Seek(17408,'Begin') | Out-Null
    $fs.Write($wb,0,$wb.Length)
    $fs.Flush($true)
    # Verify
    $fs.Seek(17408,'Begin') | Out-Null
    $rb = New-Object byte[] $pad
    $off=0; while($off -lt $rb.Length){ $n=$fs.Read($rb,$off,$rb.Length-$off); if($n -le 0){break}; $off+=$n }
    $fs.Close(); $sfh.Close()
    $ok = $true
    for($i=0;$i -lt $ub.Length;$i++){ if($ub[$i] -ne $rb[$i]){$ok=$false;break} }
    if ($ok) { Write-Host "  Uboot: VERIFIED OK" -ForegroundColor Green }
    else { Write-Host "  Uboot: VERIFY FAILED!" -ForegroundColor Red; continue }

    # Copy files
    Copy-Item 'D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin' "${dl}:\" -Force
    Copy-Item 'D:\github\zkjh\mvp\releases\ZRT_SOC_T23ZN_TP9950_DEBUG_FW.bin' "${dl}:\" -Force
    Write-Host "  Files: COPIED"
    Write-Host "  ${dl}: READY!" -ForegroundColor Green
}
Write-Host "`n===== SUMMARY ====="
Get-ChildItem 'F:\','G:\' -ErrorAction SilentlyContinue | Select-Object @{n='Card';e={$_.PSDrive.Name}}, Name, Length | Format-Table -AutoSize