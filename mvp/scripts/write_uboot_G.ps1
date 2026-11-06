# Write uboot to 17KB on F: (29.7GB card)
$ErrorActionPreference = 'Stop'
$cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
if (-not ('RawDisk' -as [type])) { Add-Type -TypeDefinition $cs }

$part = Get-Partition -DriveLetter F -ErrorAction Stop
$disk = Get-Disk -Number $part.DiskNumber
Write-Host "F: -> PhysicalDrive$($disk.Number) $($disk.FriendlyName) $([math]::Round($disk.Size/1GB,1))GB offset=$([math]::Round($part.Offset/1MB,1))MB"
if ($disk.BusType -ne 'USB') { throw "ABORT: not USB" }
if ($part.Offset -lt 2MB) { throw "ABORT: offset < 2MB" }

$ub = [IO.File]::ReadAllBytes('D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin')
$pad = [int](([math]::Ceiling($ub.Length/512))*512)
$wb = New-Object byte[] $pad
[Array]::Copy($ub,0,$wb,0,$ub.Length)
for($i=$ub.Length;$i -lt $pad;$i++){ $wb[$i]=0xFF }

[uint32]$GR = 2147483648; [uint32]$GW = 1073741824
$access = [uint32]($GR -bor $GW)
$sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive" + $disk.Number, $access, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
if ($sfh.IsInvalid) { throw "CreateFile failed: " + [Runtime.InteropServices.Marshal]::GetLastWin32Error() }
$fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)

$fs.Seek(17408,'Begin') | Out-Null
$fs.Write($wb,0,$wb.Length)
$fs.Flush($true)

$fs.Seek(17408,'Begin') | Out-Null
$rb = New-Object byte[] $pad
$off=0; while($off -lt $rb.Length){ $n=$fs.Read($rb,$off,$rb.Length-$off); if($n -le 0){break}; $off+=$n }
$fs.Close(); $sfh.Close()

$ok = $true
for($i=0;$i -lt $ub.Length;$i++){ if($ub[$i] -ne $rb[$i]){$ok=$false;break} }
if ($ok) {
  Write-Host "UBOOT WRITE VERIFIED - BOOT CARD READY" -ForegroundColor Green
  Write-Host ""
  Write-Host "Next steps:"
  Write-Host "  1. Remove card from reader"
  Write-Host "  2. Insert into board TF slot"
  Write-Host "  3. Short J16"
  Write-Host "  4. Power cycle"
  Write-Host "  5. Watch COM4/COM5 for U-Boot output"
} else {
  Write-Host "VERIFY FAILED!" -ForegroundColor Red
}
