<#
.SYNOPSIS
Exports all standard modules and class modules from an Excel file.

.DESCRIPTION
This script extracts all standard modules and class modules from the specified Excel file and saves each module as a file in the specified directory.

.PARAMETER InputFile
Specifies the path of the Excel file that contains the modules to export.

.PARAMETER OutputDirectory
Specifies the path of the directory where the extracted module files will be saved.

.PARAMETER ExportDocumentModule
Exports worksheet or ThisWorkbook modules.

.PARAMETER Force
Indicates whether to delete existing files in the output folder if it is not empty. If this switch is specified, the files are forcibly deleted. If this switch is not specified, the script will terminate with an error.

.EXAMPLE
Export-AllModuleFromExcelFile -InputFile "C:\path\to\your\file.xlsm" -OutputDirectory "C:\path\to\export"

In this example, all VBA modules from the specified Excel file are extracted and saved as individual files in the specified output directory.

.LINK
https://docs.microsoft.com/powershell/
#>
function Export-AllModuleFromExcelFile {
    [CmdletBinding(SupportsShouldProcess)]
    Param (
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$InputFile,

        [Parameter(Mandatory = $true, Position = 1)]
        [string]$OutputDirectory,

        [switch]$ExportDocumentModule,
        [switch]$Force
    )

    if (-not (Test-Path $InputFile)) {
        Write-Error "Input File '$($InputFile)' does not exist."
        return
    }

    if ((Get-ChildItem -Path $OutputDirectory).Count -ne 0 -and -not $Force) {
        Write-Error "Output directory '$($OutputDirectory)' is not empty. Use the -Force switch to remove existing files."
        return
    }

    # Internal Functions

    function _get_fileext($comp_type, $export_doc) {
        if ($comp_type -eq 1) { return ".bas" }
        if ($comp_type -eq 2) { return ".cls" }
        if ($comp_type -eq 3) { return ".frm" }
        if ($export_doc -and $component.Type -eq 100) { return ".cls" }
        return $null
    }

    # Main

    # Create an instance of Excel Application
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $False
    #$excel.AutomationSecurity = [Microsoft.Office.Core.MsoAutomationSecurity]::msoAutomationSecurityLow # Change macro settings if needed

    $inputFilePath = Resolve-Path $InputFile
    
    if (-not (Test-Path $OutputDirectory)) {
        New-Item $OutputDirectory -ItemType Directory -Force | Out-Null
    }
    elseif ($Force) {
        Remove-Item -Path (Join-Path $OutputDirectory "*") -Force
    }


    $outputDirPath = Resolve-Path $OutputDirectory

    try {
        # Open the workbook
        if ($PSCmdlet.ShouldProcess($InputFile, "Open Excel file $($InputFile)")) {
            $workbook = $excel.Workbooks.Open($inputFilePath)
        }
        Write-Debug "File opened."
        try {
            # Loop through all VBComponents in the VBA project
            if ($PSCmdlet.ShouldProcess($OutputDirectory, "Export VBA modules in Excel file '$($InputFile)' to directory '$($OutputDirectory)'")) {
                foreach ($component in $workbook.VBProject.VBComponents) {
                    # Export only standard modules and class modules
                    $fileext = _get_fileext($component.Type, $ExportDocumentModule)
                    if (-not $null -eq $fileext) {
                        $filename = (Join-Path $outputDirPath $component.Name) + $fileext
                        Write-Information "Exported $($filename)"
                        $component.Export($filename)
                    }
                    else {
                        Write-Debug "Ignoring type '$($component.Name)($($component.Type))'"
                    }
                }
            }
        }
        finally {
            if ($PSCmdlet.ShouldProcess($InputFile, "Close Excel file $($InputFile)")) {
                # Close the workbook
                $workbook.Close($False)
                $excel.Quit()
            }
        }
    }
    finally {
        # Reset macro security if changed
        #$excel.AutomationSecurity = [Microsoft.Office.Core.MsoAutomationSecurity]::msoAutomationSecurityByUI

        # Release COM objects
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) > $null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
    }
}
