# DoxyVB6

## Overview

This Python script is an input filter designed to convert Visual Basic 6.0 source code into a format recognizable by [Doxygen](https://www.doxygen.nl/). It is based on the processing logic of `vbfilter.py` (VB6 to C conversion), which was originally created by Basti Grembowietz and later modified by Ryo Satsuki.

## Features

- Converts VB comments into Doxygen-style documentation. Lines starting with `'*` are treated as comments for the subsequent members, while lines starting with `'!` are treated as comments for the module itself.  
- Processes functions, subprocedures, properties, enums, constants, and variables. (The internal code of functions, subprocedures, and properties is not processed.)
- For class modules, if you include the comment `'# Interface` in the code, it will be treated as an interface.

## Limitations

- Non-indexed default members are not represented as default-call members. A property marked with `VB_UserMemId = 0` is only converted to an indexer when it has index arguments; otherwise it is documented as a normal property.
- See [`docs/product-spec.md`](./docs/product-spec.md) for the detailed VB property conversion rules.

## Usage

1. Place the `build_document.bat` and `build_document_main.ps1` files into a dedicated folder of your choice. Within this chosen folder, create a subfolder named `DoxyVB6`.
2. Place the `DoxyVB6.exe` and `Doxyfile` files inside the `DoxyVB6` subfolder.
3. Create a shortcut to `build_document.bat` in the same directory that contains your `modules` folder. Leave the `Start in` field blank in the shortcut properties.
4. Double-click the shortcut to generate a `docs` folder.

## License

This project is licensed under the terms of the **GNU General Public License, version 3 (GPLv3)**, or (at your option) any later version. By using this script, you agree to the terms and conditions of this license.

For full license details, please see the [`LICENSE`](./LICENSE) file in this repository or visit the [GNU website](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an [issue](https://github.com/tkmr-akhs/DoxyVB6/issues) or submit a pull request.
