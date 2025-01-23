# DoxyVB6

## Overview

This Python script is an input filter designed to convert Visual Basic 6.0 source code into a format recognizable by [Doxygen](https://www.doxygen.nl/). It is based on the processing logic of `vbfilter.py` (VB6 to C conversion), which was originally created by Basti Grembowietz and later modified by Ryo Satsuki.

## Features

- Converts VB comments into Doxygen-style documentation. Lines starting with `'*` are treated as comments for the subsequent members, while lines starting with `'!` are treated as comments for the module itself.  
- Processes functions, subprocedures, properties, enums, constants, and variables. (The internal code of functions, subprocedures, and properties is not processed.)
- For class modules, if you include the comment `'# Interface` in the code, it will be treated as an interface.

## Usage

1. Place `build_document.bat` and `build_document_main.ps1` in any folder. And create a `DoxyVB6` folder in the folder.
2. Place `DoxyVB6.exe` and `Doxyfile` in the `DoxyVB6` folder.
3. Create a shortcut to `build_document.bat` in the same directory that contains your `modules` folder. Leave the `Start in` field blank in the shortcut properties.
4. Double-click the shortcut to generate a `doc` folder.

Please refer to the [example](./example) directory in the GitHub repository for sample usage.

# ExcelModuleManager

## Overview

A PowerShell module for exporting and importing modules to and from Excel files.

## Features

- `Export-AllModuleFromExcelFile`: Exports all standard modules and class modules.
- `Export-ModuleFromExcelFile`: Exports a specified standard module or class module by name.
- `Import-ModuleToExcelFile`: Imports specified standard modules or class modules into an Excel file.

## Usage

1. Enable the checkbox for `[Trust access to the VBA project object model]` in Excel by going to `[File]` > `[Options]` > `[Trust Center]` > `[Macro Settings]`.
2. Place `export_one.bat` and `export_one_main.ps1` in any folder.
3. Create a shortcut to `export_one.bat` and place it in the same directory as your .xlsm file.
4. Drag and drop your .xlsm file onto the shortcut you just created.
5. A new `modules` folder will be created, containing the exported module files. (Any pre-existing `modules` folder will be forcibly deleted before processing.)

Please refer to the [example](./example) directory in the GitHub repository for sample usage.

# License

This project is licensed under the terms of the **GNU General Public License, version 3 (GPLv3)**, or (at your option) any later version. By using this script, you agree to the terms and conditions of this license.

For full license details, please see the [`LICENSE`](./LICENSE) file in this repository or visit the [GNU website](https://www.gnu.org/licenses/gpl-3.0.en.html).

# Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an [issue](https://github.com/tkmr-akhs/DoxyVB6/issues) or submit a pull request.
