#################################
# This script restarts the EDMarketConnector process and updates the launch.json file with the new process ID.
# It is intended to be run from the .vscode folder in the EDMarketConnector directory.
#################################

# Define the process name
$ProcessName = "EDMarketConnector"

if (Get-Process -Name $ProcessName -ErrorAction SilentlyContinue) {
    Stop-Process -Name $ProcessName -Force
}
Start-Process -FilePath 'C:\Program Files (x86)\EDMarketConnector\EDMarketConnector.exe'


# Get the PID of the process
$Process = Get-Process | Where-Object { $_.ProcessName -eq $ProcessName }

if ($null -eq $Process) {
    Write-Host "Error: Process '$ProcessName' not found."
    exit 1
}

$ProcessID = $Process.Id
Write-Host "Found '$ProcessName' running with PID: $ProcessID"

# Define the path to launch.json
$LaunchJsonPath = "$PSScriptRoot\launch.json"

if (!(Test-Path $LaunchJsonPath)) {
    Write-Host "Error: launch.json not found at $LaunchJsonPath"
    exit 1
}

# Read launch.json content
$LaunchJson = Get-Content -Raw -Path $LaunchJsonPath | ConvertFrom-Json

# Update the processId field
foreach ($config in $LaunchJson.configurations) {
    if ($config.name -eq "Attach to EDMarketConnector") {
        $config.processId = $ProcessID
    }
}

# Write updated JSON back to file
$LaunchJson | ConvertTo-Json -Depth 3 | Set-Content -Path $LaunchJsonPath

Write-Host "Updated launch.json with process ID: $ProcessID"