# One serial, resumable finish sequence for the authorized Korean voice candidate.
$ErrorActionPreference='Stop'
$root='F:\aoe_4_temp\New_custom_civilization\aoe4-korea'
$voice='F:\aoe_4_temp\ai_voice\tts-workstation'
$cpu=Join-Path $voice 'ComfyUI_windows_portable\python_embeded\python.exe'
$sdk='C:\Users\RS\AppData\Local\Programs\Python\Python313\python.exe'
$docs=Join-Path $root 'docs\voices020'
$env:PYTHONIOENCODING='utf-8'
$env:TEMP=Join-Path $voice 'temp';$env:TMP=$env:TEMP
function Status([string]$phase,[string]$state) {
    @{utc=[DateTime]::UtcNow.ToString('o');phase=$phase;state=$state} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $docs 'FINISH_PROGRESS.json') -Encoding utf8
    Write-Output ($phase+' '+$state)
}
function Run([string]$python,[string]$label,[string[]]$arguments) {
    Status $label 'running'
    $log=Join-Path $docs ($label+'.log')
    # Windows PowerShell may wrap native stderr as non-terminating errors.
    # Preserve it in the log and decide success from the actual process exit.
    $oldPreference=$ErrorActionPreference
    $ErrorActionPreference="Continue"
    & $python -X utf8 -B @arguments *> $log
    $nativeExit=$LASTEXITCODE
    $ErrorActionPreference=$oldPreference
    if ($nativeExit -ne 0) { Get-Content -LiteralPath $log -Tail 25; throw ($label+' failed; diagnostics retained in '+$log) }
    Status $label 'passed'
}
try {
    Set-Location -LiteralPath $root
    $started=[DateTime]::UtcNow
    Status 'await-synthesis-and-screening' 'waiting'
    while (-not ((Test-Path -LiteralPath (Join-Path $docs 'GENERATION_COMPLETE.json')) -and (Test-Path -LiteralPath (Join-Path $docs 'LANGUAGE_SCREENING.json')) -and (Test-Path -LiteralPath (Join-Path $docs 'TRANSCRIPTION_SAMPLES.json')))) {
        if (([DateTime]::UtcNow-$started).TotalHours -gt 8) { throw 'Completion receipts still missing after bounded wait; source remains protected.' }
        if (-not (Test-Path -LiteralPath $root) -or -not (Test-Path -LiteralPath $voice)) { throw 'Required existing F: paths became unavailable; no replacement paths created.' }
        Start-Sleep -Seconds 12
    }
    $config=Get-Content -LiteralPath (Join-Path $root 'project.json') -Raw | ConvertFrom-Json
    if ($config.version -ne '0.1.6') { throw 'Source already promoted or version changed; inspect checkpoint instead of repeating promotion.' }
    Run $cpu 'encoding-finalization' @('tools/voice020_finalize_audio.py')
    Run $cpu 'audio-audit' @('tools/voice020_audio_audit.py')
    Run $cpu 'listening-page' @('tools/voice020_review.py')
    Run $sdk 'semantic-proof-final' @('tools/voice020_semantic.py')
    Run $sdk 'source-promotion' @('tools/voice020_release.py','promote')
    Run $sdk 'focused-tests' @('tools/voice020_focused_tests.py')
    Run $sdk 'environment-final' @('tools/check_environment.py')
    Run $sdk 'inputs-final' @('tools/inputs.py','verify')
    $nativeParent='F:\aoe_4_temp\Temp_aoe4'
    $parent=Get-Item -LiteralPath $nativeParent
    if (($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'Native temporary parent is linked; resolve ownership before building.' }
    $nativeTemp=Join-Path $nativeParent 'k20'
    if (Test-Path -LiteralPath $nativeTemp) { throw 'Existing native build temp is protected; inspect before reuse.' }
    [IO.Directory]::CreateDirectory($nativeTemp) | Out-Null
    $env:TEMP=$nativeTemp;$env:TMP=$nativeTemp
    Run $sdk 'native-build-020' @('tools/build.py','--replace-current')
    Status 'local-zip-built' 'passed; final human-readable receipt and automation stop still required'
} catch {
    Status 'finish-sequence' ('stopped: '+$_.Exception.Message)
    Write-Error $_
    exit 1
}
