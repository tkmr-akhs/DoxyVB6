<#
.SYNOPSIS
Imports VBA modules into a specified Excel file.

.DESCRIPTION
This script retrieves all `.bas` and `.cls` files from a specified directory and imports them into a specified Excel file (template file). The final Excel file is saved at the specified output path.

.PARAMETER ExcelFile
The path of the Excel file into which the modules will be imported.

.PARAMETER ModuleFiles
The path(s) to the `.bas` and `.cls` files.

.PARAMETER Flush
Removes all modules in the file before importing. Cannot be used simultaneously with the `Update` parameter.

.PARAMETER Update
Updates only the modules that already exist in the file and have the same name. Cannot be used simultaneously with the `Flush` parameter.

.EXAMPLE
Import-ModuleToExcelFile -ExcelFile "C:\path\to\workbook.xlsm" -ModuleFiles "C:\path\to\module.bas"

In this example, the `.bas` file at `C:\path\to\module.bas` is imported into `C:\path\to\workbook.xlsm`.

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
        Write-Error "The 'Update' and 'Flush' switches cannot be specified at the same time."
        return
    }

    # Local Functions
    function _get_modname($mod_file) {
        $mod_content = Get-Content -Path $mod_file -Encoding oem
        $vb_name_pattern = '^\s*Attribute\s+VB_Name\s+=\s+"(.+)"\s*$'
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

    function _get_modinfo($check_mod_name, $check_mod_type, [System.Collections.ArrayList]$check_mod_list) {
        foreach ($check_mod_item in $check_mod_list) {
            if ($check_mod_item.Name -eq $check_mod_name -and $check_mod_item.Type -eq $check_mod_type) {
                return $check_mod_item
            }
        }
        return $null
    }

    function _remove_comps($workbook_obj, $vb_comps) {
        $remove_after = [System.Collections.ArrayList]::new()
        foreach ($vb_comp in $vb_comps) {
            [string]$vb_comp_name = $vb_comp.Name
            if ($vb_comp_name.StartsWith("I")) {
                $remove_after.Add($vb_comp) > $null
            }
            else {
                Write-Debug "Removing the old module '$($vb_comp_name)'."
                $workbook_obj.VBProject.VBComponents.Remove($vb_comp)
                Write-Information "Removed the old module '$($vb_comp_name)'."
            }
        }
        foreach ($vb_comp in $remove_after) {
            $vb_comp_name = $vb_comp.Name
            Write-Debug "Removing the old module '$($vb_comp_name)'."
            $workbook_obj.VBProject.VBComponents.Remove($vb_comp)
            Write-Information "Removed the old module '$($vb_comp_name)'."
        }
    }

    # Main

    # Create an instance of the Excel application
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $False
    try {
        # Open the workbook
        if ($PSCmdlet.ShouldProcess($ExcelFile, "Open Excel file $($ExcelFile)")) {
            Write-Debug "Opening '$($ExcelFile)'."
            $workbook = $excel.Workbooks.Open($ExcelFile)
            Write-Information "Opened '$($ExcelFile)'."
        }
        
        # Prepare the results array
        $result = @{}

        try {
            # Build list of target modules.
            $target_modules = [System.Collections.ArrayList]::new()
            foreach ($file in $ModuleFiles) {
                $mod_name = _get_modname $file
                $mod_type = _get_modtype $file

                $mod_item = [ExcelModuleInformation]::new()
                $mod_item.Name = $mod_name
                $mod_item.Type = $mod_type
                $mod_item.File = $file
                    
                $target_modules.Add($mod_item) > $null
            }
            
            $to_be_removed = [System.Collections.ArrayList]::new()
            if ($Flush) {
                # Remove all modules.
                foreach ($component in $workbook.VBProject.VBComponents) {
                    if ($component.Type -eq 1 -or $component.Type -eq 2 -or $component.Type -eq 3) {
                        Write-Debug "Marking module '$($component.Name)' for removal."
                        $to_be_removed.Add($component) > $null
                    }
                    else {
                        Write-Debug "Skipped module '$($component.Name)' because its type is $($component.Type)."
                    }
                }
            }
            else {
                # Remove old modules.
                $removed_list = [System.Collections.ArrayList]::new()
                foreach ($component in $workbook.VBProject.VBComponents) {
                    $mod_item = _get_modinfo $component.Name $component.Type $target_modules
                    if ($null -ne $mod_item) {
                        Write-Debug "Marking module '$($component.Name)' for removal."
                        $to_be_removed.Add($component) > $null
                        $removed_list.Add($mod_item) > $null
                    }
                    else {
                        if ($component.Type -eq 1 -or $component.Type -eq 2 -or $component.Type -eq 3) {
                            Write-Information "Skipped module '$($component.Name)' because it does not to be update."
                        }
                        else {
                            Write-Debug "Skipped module '$($component.Name)' because its type is $($component.Type)."
                        }
                    }
                }
            }

            # Execute removal.
            if ($PSCmdlet.ShouldProcess($ExcelFile, "Remove listed old modules in Excel file '$($ExcelFile)'")) {
                _remove_comps $workbook $to_be_removed
            }

            if ($Update) {
                $target_modules = $removed_list
            }

            # Import files.
            foreach ($mod_item in $target_modules) {
                if ($PSCmdlet.ShouldProcess($ExcelFile, "Import module file '$($file)' to Excel file '$($ExcelFile)'")) {
                    Write-Debug "Importing '$($mod_item.File)'."
                    $workbook.VBProject.VBComponents.Import($mod_item.File) > $null
                    $result[$mod_item.File] = $true
                    Write-Information "Imported '$($mod_item.Name)'."
                }
            }
            
            if ($PSCmdlet.ShouldProcess($ExcelFile, "Save and close Excel file $($ExcelFile)")) {
                Write-Debug "Saving '$($ExcelFile)'."
                $workbook.Save()
                Write-Information "Saved '$($ExcelFile)'."
            }
        }
        finally {
            # Save and close the workbook.
            Write-Debug "Closing '$($ExcelFile)'."
            $workbook.Close($True)
            Write-Information "Closed."
            $excel.Quit()
        }

        # Return results.
        return $result
    }
    finally {
        # Release COM objects.
        if ($null -ne $workbook) { [System.Runtime.Interopservices.Marshal]::ReleaseComObject($workbook) > $null }
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel) > $null
        [System.GC]::Collect()
        [System.GC]::WaitForPendingFinalizers()
    }
}

class ExcelModuleInformation {
    [string]$Name
    [int]$Type
    $File
}