# Format F: + Copy files + Write uboot@17KB (ADMIN)
param([string]$Drive = 'F')
$ErrorActionPreference = 'Stop'

# 1. Format
Write-Host "`n[1/4] Formatting ${Drive}: as FAT32..."
if (Test-Path "${Drive}:") {
    $part = Get-Partition -DriveLetter $Drive
    $diskNum = $part.DiskNumber
    Format-Volume -DriveLetter $Drive -FileSystem FAT32 -Force | Out-Null
    Write-Host "    Formatted OK"
} else {
    throw "${Drive}: not found"
}

# 2. Copy files
Write-Host "[2/4] Copying files..."
Copy-Item 'D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin' "${Drive}:\" -Force
Copy-Item 'D:\github\zkjh\mvp\releases\ZRT_SOC_T23ZN_GC2053_UNDIRECT_FW.bin' "${Drive}:\" -Force
Get-ChildItem "${Drive}:\" | Select-Object Name, Length | Format-Table -AutoSize

# 3. Write uboot @ 17KB
Write-Host "[3/4] Writing uboot @ 17KB..."
$cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
if (-not ('RawDisk' -as [type])) { Add-Type -TypeDefinition $cs }
$ub = [IO.File]::ReadAllBytes('D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin')
$pad = [int](([math]::Ceiling($ub.Length/512))*512)
$wb = New-Object byte[] $pad
[Array]::Copy($ub,0,$wb,0,$ub.Length)
for($i=$ub.Length;$i -lt $pad;$i++){ $wb[$i]=0xFF }

[uint32]$GR = 2147483648; [uint32]$GW = 1073741824
$access = [uint32]($GR -bor $GW)
$part2 = Get-Partition -DriveLetter $Drive
$disk = Get-Disk -Number $part2.DiskNumber
$sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive" + $disk.Number, $access, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
if ($sfh.IsInvalid) { throw "CreateFile failed: $([Runtime.InteropServices.Marshal]::GetLastWin32Error())" }
$fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)
$fs.Seek(17408, 'Begin') | Out-Null
$fs.Write($wb, 0, $wb.Length)
$fs.Flush($true)

# 4. Verify
$fs.Seek(17408, 'Begin') | Out-Null
$rb = New-Object byte[] $pad
$off = 0; while($off -lt $rb.Length){ $n=$fs.Read($rb,$off,$rb.Length-$off); if($n -le 0){break}; $off+=$n }
$fs.Close(); $sfh.Close()

$ok = $true
for($i=0; $i -lt $ub.Length; $i++){ if($ub[$i] -ne $rb[$i]){ $ok=$false; break } }
if ($ok) {
    Write-Host "`n[4/4] VERIFY OK - BOOT CARD READY!" -ForegroundColor Green
    Write-Host "Next: remove card from reader, insert into board, short J16, power cycle"
} else {
    Write-Host "VERIFY FAILED - try again" -ForegroundColor Red
}