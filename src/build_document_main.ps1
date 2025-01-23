$ErrorActionPreference = 'Stop'
$InformationPreference = 'Continue'

Set-Variable -Name SRC_DIR_NAME -Value "modules" -Option Constant
Set-Variable -Name DST_DIR_NAME -Value "doc" -Option Constant

if ([System.String]::IsNullOrEmpty($args[0])) {
    $proj_root = Get-Location
}
else {
    $proj_root = Split-Path (Get-Item $args[0])
}
Write-Host $proj_root

$src_dir = Join-Path $proj_root $SRC_DIR_NAME
$dst_dir = Join-Path $proj_root $DST_DIR_NAME

$tmp_root = New-TemporaryFile
$tmp_src_dir = Join-Path $tmp_root $SRC_DIR_NAME
$tmp_dst_dir = Join-Path $tmp_root $DST_DIR_NAME

$proj_name = Split-Path -Leaf $proj_root
$filter_file = Join-Path (Join-Path $PSScriptRoot "DoxyVB6") "DoxyVB6.exe"
$confbase_file = Join-Path (Join-Path $PSScriptRoot "DoxyVB6") "Doxyfile"
$conftmp_file = Join-Path $tmp_root "Doxyfile_tmp"
$conf_file = Join-Path $tmp_root "Doxyfile"

Set-Location $PSScriptRoot

# Convert the temporary file into a folder
Remove-Item $tmp_root
New-Item $tmp_root -ItemType Directory | Out-Null

# Copy the input folder to the temporary folder
Copy-Item $src_dir $tmp_src_dir -Recurse

# Create the output folder
New-Item $tmp_dst_dir -ItemType Directory | Out-Null

# Generate the configuration file Doxyfile
Get-Content -Path $confbase_file | ForEach-Object {
    $_ -replace '^OUTPUT_DIRECTORY *=', ('$0 ' + $tmp_dst_dir + '')
} | ForEach-Object {
    $_ -replace '^INPUT_FILTER *=', ('$0 ' + $filter_file + '')
} | ForEach-Object {
    $_ -replace '^INPUT *=', ('$0 ' + $tmp_src_dir + '')
} | ForEach-Object {
    $_ -replace '^(PROJECT_NAME *=) "My Project"', ('$1 ' + $proj_name + '')
} | Out-File -FilePath $conftmp_file -Encoding utf8
[System.IO.File]::WriteAllText($conf_file, (Get-Content $conftmp_file -Raw))

# Run Doxygen
doxygen "`"$conf_file`""

# Move the output folder to the final location
if (Test-Path $dst_dir) {
    Remove-Item $dst_dir -Recurse -Force
}
Move-Item $tmp_dst_dir $dst_dir

# Delete the temporary folder
Remove-Item $tmp_root -Recurse -Force