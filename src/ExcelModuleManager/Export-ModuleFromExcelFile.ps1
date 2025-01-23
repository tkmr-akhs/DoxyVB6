<#
.SYNOPSIS
Exports a specified standard module or class module from an Excel file.

.DESCRIPTION
This script extracts a specified standard module or class module from the given Excel file and saves it as a file in the specified directory.

.PARAMETER ModuleName
The name of the module to export.

.PARAMETER InputFile
The path of the Excel file containing the module to export.

.PARAMETER OutputDirectory
The path of the directory where the extracted module file will be saved.

.PARAMETER Force
Indicates whether to delete existing files in the output folder if they have the same name. If this switch is specified, the files are forcibly deleted. If this switch is not specified, the script will terminate with an error if a file with the same name already exists.

.EXAMPLE
Export-ModuleFromExcelFile -InputFile "C:\path\to\your\file.xlsm" -OutputDirectory "C:\path\to\export"

In this example, the VBA module named `Common_Mod` is extracted from the specified Excel file and saved as a file in the specified output directory.

.LINK
https://docs.microsoft.com/powershell/
#>
function Export-ModuleFromExcelFile {
    [CmdletBinding(SupportsShouldProcess)]
    Param (
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$ModuleName,

        [Parameter(Mandatory = $true, Position = 1)]
        [string]$InputFile,

        [Parameter(Mandatory = $false, Position = 2)]
        [string]$OutputDirectory,

        [switch]$Force
    )

    if (-not (Test-Path $InputFile)) {
        Write-Error "Input File '$($InputFile)' does not exist."
        return
    }
    
    # Internal Functions

    function _get_fileext($comp_type, $export_doc) {
        if ($comp_type -eq 1) { return ".bas" }
        if ($comp_type -eq 2) { return ".cls" }
        if ($comp_type -eq 3) { return ".frm" }
        if ($component.Type -eq 100) { return ".cls" }
        return $null
    }

    # Main
    # Create an instance of Excel Application
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $False
    #$excel.AutomationSecurity = [Microsoft.Office.Core.MsoAutomationSecurity]::msoAutomationSecurityLow # Adjust macro settings if necessary

    $inputFilePath = Resolve-Path $InputFile
    
    if (-not (Test-Path $OutputDirectory)) {
        New-Item $OutputDirectory -ItemType Directory -Force | Out-Null
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
                [bool]$is_found = $false
                foreach ($component in $workbook.VBProject.VBComponents) {
                    # Export only standard modules and class modules
                    $fileext = _get_fileext($component.Type)
                    if (-not $null -eq $fileext -and $component.Name -eq $ModuleName) {
                        # Construct the file name
                        $filename = (Join-Path $outputDirPath $component.Name) + $fileext
                        Write-Debug $filename

                        # Check if the file already exists
                        if (Test-Path $filename) {
                            if ($Force) {
                                Remove-Item $filename -Force
                            }
                            else {
                                Write-Error "File name '$($filename)' already exists."
                                return
                            }
                        }

                        # Export the module
                        $component.Export($filename)
                        $is_found = $true
                    }
                    else {
                        Write-Error "Module '$($ModuleName)' is ignore type. (type:$($component.Type))"
                    }
                }

                if (-not $is_found) {
                    Write-Error "Module name '$($ModuleName)' was not found."
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
        # Reset macro security settings if they were changed
        #$excel.AutomationSecurity = [Microsoft.Office.Core.MsoAutomationSecurity]::msoAutomationSecurityByUI

        # Release COM objects
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) > $null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
    }
}
