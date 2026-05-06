param (
    [string]$InnoExtractPath = ""
)

function Get-ScriptDirectory {
    Split-Path -Parent $PSCommandPath
}

function Expand-AllInstallers {
    $installers = Get-ChildItem -Path .\*.exe -Exclude innoextract.exe

    foreach ($installer in $installers) {
        $expandedPath = $installer.BaseName + ".d"
        if (Test-Path -Path $expandedPath -PathType Container) {
            Write-Host "Removing existing expanded directory: $expandedPath"
            Remove-Item -Path $expandedPath -Recurse
        }
    }

    foreach ($installer in $installers) {
        $expandedPath = $installer.BaseName + ".d"
        Write-Host "Expanding installer: $($installer.FullName)"
        & $InnoExtractPath -e "$($installer.FullName)" -d "$expandedPath"
    }
}

function Verify-AllSignatures {
    $invalids = @()

    $binaries = Get-ChildItem -Path . -Recurse -Include *.dll, *.exe, *.prm, *.scr, *.sys, *.vst3 -Exclude innoextract.exe
    foreach ($binary in $binaries) {
        if (Test-Path -Path $binary.FullName -PathType Leaf) {
            $relativePath = Resolve-Path -Relative -Path $binary.FullName
            $signature = Get-AuthenticodeSignature -FilePath $binary.FullName
            if ($signature.Status -ne 'Valid') {
                Write-Warning "Invalid signature detected: $relativePath"
                $invalids += $binary.Name
            } else {
                Write-Host "Signature valid: $relativePath"
            }
        }
    }

    if ($invalids.Count -ne 0) {
        Write-Warning "The following files have invalid signatures:"
        $invalids = $invalids | Sort-Object -Unique
        foreach ($invalid in $invalids) {
            Write-Warning "Invalid signature: $invalid"
        }
    } else {
        Write-Host "All signatures are valid."
    }
}

if ([string]::IsNullOrEmpty($InnoExtractPath)) {
    $InnoExtractPath = Join-Path -Path "." -ChildPath "innoextract.exe"
    if (-Not (Test-Path -Path $InnoExtractPath -PathType Leaf)) {
        $InnoExtractPath = Join-Path -Path (Get-ScriptDirectory) -ChildPath "innoextract.exe"
    }
} elseif (Test-Path -Path $InnoExtractPath -PathType Container) {
    $InnoExtractPath = Join-Path -Path $InnoExtractPath -ChildPath "innoextract.exe"
}

if (-Not (Test-Path -Path $InnoExtractPath -PathType Leaf)) {
    Write-Error "Please provide a valid path to innoextract.exe using the -InnoExtractPath parameter or ensure it is in the current directory."
    exit 1
}

Expand-AllInstallers
Verify-AllSignatures
