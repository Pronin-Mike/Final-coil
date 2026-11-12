param([switch]$MemoryCache)
$engine = 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
$project = Join-Path $PSScriptRoot 'FinalCoil.uproject'
$launchArgs = @('"' + $project + '"', '-ModelContextProtocolStartServer')
if ($MemoryCache) { $launchArgs += '-DDC-ForceMemoryCache' }
Start-Process -FilePath $engine -ArgumentList $launchArgs -WindowStyle Hidden
