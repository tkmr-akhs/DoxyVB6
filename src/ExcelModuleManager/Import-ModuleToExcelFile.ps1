<#
.SYNOPSIS
Imports VBA modules into a specified Excel file.

.DESCRIPTION
This script retrieves all `.bas` and `.cls` files from a specified directory and imports them into a specified Excel file (template file). The final Excel file is saved at the specified output path.

.PARAMETER ExcelFile
The path of the Excel file into which the modules will be imported.

.PARAMETER ModuleFile
The path to the `.bas` and `.cls` files.

.PARAMETER Force
Removes all modules in the file before importing. Cannot be used simultaneously with the `Update` parameter.

.PARAMETER Update
Updates only the modules with the same name that already exist in the file. Cannot be used simultaneously with the `Force` parameter.

.EXAMPLE
Import-ModuleToExcelFile -ExcelFile "C:\path\to\template.xlsm" -ModuleDirectory "C:\path\to\module.bas"

In this example, all VBA modules from the directory `C:\path\to\modules` are retrieved and imported into `C:\path\to\template.xlsm`. The result is then saved as `C:\path\to\output.xlsm`.

.LINK
https://docs.microsoft.com/powershell/
#>
function Import-ModuleToExcelFile {
    [CmdletBinding(SupportsShouldProcess)]
    Param (
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$ExcelFile,

        [Parameter(Mandatory = $true, Position = 1)]
        [string[]]$ModuleFiles,

        [switch]$Flush,

        [switch]$Update
    )

    if ($Flush -and $Update) {
        Write-Error The "'Update' and 'Flush' switches cannot be specified at the same time."
        return
    }

    # Local Functions
    function _get_modname($mod_file) {
        $mod_content = Get-Content -Path $mod_file -Encoding oem
        $vb_name_pattern = '^\*sAttribute\s+VB_Name\s+=\s+"(.+)"\s*$'
        foreach ($mod_line in $mod_content) {
            if ($mod_line -match $vb_name_pattern) {
                return $matches[1]
            }
        }
        return (Split-Path $mod_file -Leaf) -replace '^(\.?(?:[^.]+\.?$|[^.]+))(\.[^\.]+\.?$)?', '$1'
    }

    function _get_modtype($mod_file) {
        $mod_ext = (Split-Path $mod_file -Leaf) -replace '^(\.?(?:[^.]+\.?$|[^.]+))(\.[^\.]+\.?$)?', '$2'
        if ($mod_ext -eq ".bas") {
            return 1
        }
        elseif ($mod_ext -eq ".cls") {
            return 2
        }
        elseif ($mod_ext -eq ".frm") {
            return 3
        }
        else {
            return -1
        }
    }

    # Main

    # Create an instance of Excel Application
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $False
    try {
        # Open the workbook
        if ($PSCmdlet.ShouldProcess($ExcelFile, "Open Excel file $($ExcelFile)")) {
            Write-Debug "Opening $($ExcelFile)."
            $workbook = $excel.Workbooks.Open($ExcelFile)
            Write-Information "Opened $($ExcelFile)."
        }
        
        # Prepare the results array
        $result = @{}

        try {
            if ($Flush) {
                if ($PSCmdlet.ShouldProcess($ExcelFile, "Flush modules in Excel file '$($ExcelFile)'")) {
                    foreach ($component in $workbook.VBProject.VBComponents) {
                        Write-Debug "Checking module $($component.Type) -eq $($mod_type)."
                        if ($Flush -and ($component.Type -eq 1 -or $component.Type -eq 2 -or $component.Type -eq 3)) {
                            Write-Debug "Removing old module $($component.Name)."
                            $workbook.VBProject.VBComponents.Remove($component)
                            Write-Debug "Removed old module $($component.Name)."
                        }
                    }
                }
            }

            # Import files
            foreach ($file in $ModuleFiles) {
                if ($PSCmdlet.ShouldProcess($ExcelFile, "Import module file '$($file)' to Excel file '$($ExcelFile)'")) {
                    $mod_name = _get_modname($file)
                    $mod_type = _get_modtype($file)
                    
                    if ($Update) { 
                        # Update
                        [bool]$updated = $false
                        foreach ($component in $workbook.VBProject.VBComponents) {
                            Write-Debug "Checking module $($component.Name) -eq $($mod_name) -and $($component.Type) -eq $($mod_type)."
                            if ($component.Name -eq $mod_name -and $component.Type -eq $mod_type) {
                                if (-not $Flush) {
                                    Write-Debug "Removing module $($mod_name)."
                                    $workbook.VBProject.VBComponents.Remove($component)
                                    Write-Debug "Removed module $($mod_name)."
                                }
                                Write-Debug "Importing $($file)."
                                $workbook.VBProject.VBComponents.Import($file) > $null
                                $updated = $true
                                Write-Information "Imported $($mod_name)."
                            }
                        }
                        $result[$file] = $updated
                    }
                    else {
                        # Standard import
                        if (-not $Flush) {
                            foreach ($component in $workbook.VBProject.VBComponents) {
                                Write-Debug "Checking module $($component.Name) -eq $($mod_name) -and $($component.Type) -eq $($mod_type)."
                                if ($component.Name -eq $mod_name -and $component.Type -eq $mod_type) {
                                    Write-Debug "Removing module $($mod_name)."
                                    $workbook.VBProject.VBComponents.Remove($component)
                                    Write-Debug "Removed module $($mod_name)."
                                }
                            }
                        }
                        
                        Write-Debug "Importing $($file)."
                        $workbook.VBProject.VBComponents.Import($file) > $null
                        $result[$file] = $true
                        Write-Information "Imported $($mod_name)."
                    }
                }
            }
        }
        finally {
            # Save and close the workbook
            if ($PSCmdlet.ShouldProcess($ExcelFile, "Save and close Excel file $($ExcelFile)")) {
                Write-Debug "Saving $($ExcelFile)."
                $workbook.Save()
                Write-Information "Saved."
                Write-Debug "Closing $($ExcelFile)."
                $workbook.Close($True)
                Write-Information "Closed."
                $excel.Quit()
            }
        }

        # Return results
        $result
    }
    finally {
        # Release COM objects
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) > $null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
    }
}
