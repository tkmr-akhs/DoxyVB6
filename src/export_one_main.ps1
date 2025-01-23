$ErrorActionPreference = 'Stop'
$InformationPreference = 'Continue'

Set-Variable -Name OUT_DIR_NAME -Value "modules" -Option Constant

Set-Location $PSScriptRoot
Import-Module ./ExcelModuleManager

$input_file_path = $args[0]
$xlsm_dir_path = Split-Path $input_file_path
$output_dir_path = (Join-Path $xlsm_dir_path $OUT_DIR_NAME)

Export-AllModuleFromExcelFile $input_file_path $output_dir_path -Force
