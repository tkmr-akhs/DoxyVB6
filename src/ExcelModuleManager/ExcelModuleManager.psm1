# Dot-sourcing other .psm1 files
. $PSScriptRoot\Export-ModuleFromExcelFile.ps1
. $PSScriptRoot\Export-AllModuleFromExcelFile.ps1
. $PSScriptRoot\Import-ModuleToExcelFile.ps1

# Export the required functions and variables
Export-ModuleMember -Function `
    'Export-ModuleFromExcelFile', `
    'Export-AllModuleFromExcelFile', `
    'Import-ModuleToExcelFile'