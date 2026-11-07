$ErrorActionPreference = "Stop"
$out = "D:\github\zkjh\mvp\logs\fullrebuild.txt"
"=== FULL TF REBUILD $(Get-Date -Format T) ===" | Out-File $out -Encoding utf8
try {
  $cs = 'using System;using System.Runtime.InteropServices;using Microsoft.Win32.SafeHandles;public class RawDisk{[DllImport("kernel32.dll",SetLastError=true,CharSet=CharSet.Unicode)]public static extern SafeFileHandle CreateFile(string name,uint access,uint share,IntPtr sa,uint disp,uint flags,IntPtr tpl);}'
  Add-Type -TypeDefinition $cs
  [uint32]$access = [uint32](2147483648 -bor 1073741824)
  $sfh = [RawDisk]::CreateFile("\\.\PhysicalDrive1", $access, [uint32]3, [IntPtr]::Zero, [uint32]3, 0, [IntPtr]::Zero)
  if ($sfh.IsInvalid) { throw ("open err=" + [Runtime.InteropServices.Marshal]::GetLastWin32Error()) }
  $fs = New-Object IO.FileStream($sfh, [IO.FileAccess]::ReadWrite, 512, $false)
  function Write-Verify([byte[]]$data,[long]$off,[string]$name){
    $pad = [int](([math]::Ceiling($data.Length/512))*512)
    $wb = New-Object byte[] $pad
    [Array]::Copy($data,0,$wb,0,$data.Length)
    for($i=$data.Length;$i -lt $pad;$i++){ $wb[$i]=0xFF }
    $fs.Seek($off,'Begin') | Out-Null
    $fs.Write($wb,0,$wb.Length)
    $fs.Flush($true)
    $rb = New-Object byte[] $pad
    $fs.Seek($off,'Begin') | Out-Null
    $o=0; while($o -lt $pad){ $n=$fs.Read($rb,$o,$pad-$o); if($n -le 0){break}; $o+=$n }
    $same=$true; for($j=0;$j -lt $data.Length;$j++){ if($rb[$j] -ne $data[$j]){$same=$false;break} }
    if(-not $same){ throw "$name VERIFY FAILED" }
    "$name $($data.Length)B @offset $off VERIFIED" | Out-File $out -Append -Encoding utf8
  }
  Write-Verify ([IO.File]::ReadAllBytes("D:\github\zkjh\mvp\releases\t23_sdcard_uboot_uart1.bin")) 17408 "RAW-SDUBOOT@17KB"
  Write-Verify ([IO.File]::ReadAllBytes("D:\github\zkjh\mvp\releases\uImage-m2-lzma.bin")) 3145728 "RAW-M2KERNEL@3MB"
  $fs.Close()
  "RAW LAYER OK" | Out-File $out -Append -Encoding utf8
} catch { "ERROR: $_" | Out-File $out -Append -Encoding utf8 }
