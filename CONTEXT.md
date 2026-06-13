# DoxyVB6

DoxyVB6 is a Python input filter that converts VB6 / VBA source code into a form that Doxygen can parse more reliably.
This repository also contains `ExcelModuleManager`, a PowerShell module for importing and exporting VBA modules between Excel `.xlsm` workbooks and module folders.

## Folder Layout

- `src/DoxyVB6`: Python package implementation. It contains the VB6/VBA parser and C#-style output conversion logic.
- `src/ExcelModuleManager`: PowerShell module for importing and exporting Excel VBA modules.
- `src/build_document*.ps1` / `src/build_document*.bat`: wrappers for generating Doxygen documentation.
- `src/export_one*.ps1` / `src/export_one*.bat`: wrappers for exporting VBA modules from an Excel workbook.
- `tests`: pytest coverage for the Python conversion logic.
- `example`: sample workbook and usage examples.
- `build` / `dist`: generated artifacts. Do not treat them as source during normal design work.

## Language

**input filter**:
A preprocessing program that converts VB6 / VBA source into another representation before Doxygen reads it.
_Avoid_: Doxygen configuration itself.

**Doxygen comment**:
A comment written with `'*` or `'!` that should appear in Doxygen output.
_Avoid_: ordinary VBA implementation comments.

**module comment**:
A `'!` comment block that documents an entire module or class.
_Avoid_: comments attached to a following member.

**member comment**:
A `'*` comment block attached to the following member, such as a Sub, Function, Property, Enum, Const, or variable.
_Avoid_: module-level documentation.

**indexed property**:
A VB6 / VBA Property Get, Property Let, or Property Set that has one or more arguments before the assigned value.
_Avoid_: assuming the property is also a default member.

**default member**:
A VB6 / VBA member marked as the default callable member of its containing class, typically by `VB_UserMemId = 0`.
_Avoid_: any argument-bearing property that lacks a default-member marker.

**default indexed property**:
An indexed property that is also marked as the default member of its containing class.
_Avoid_: non-indexed default members.

**non-default indexed property**:
An indexed property that is not marked as the default member of its containing class.
_Avoid_: default indexed property.

**interface marker**:
A marker such as `'# Interface` that makes a class module appear as an interface in generated documentation.
_Avoid_: the VBA `Implements` statement itself.

**ExcelModuleManager**:
A PowerShell module that uses Excel COM and VBIDE to import and export modules between `.xlsm` files and `modules` folders.
_Avoid_: the Python conversion package.

**modules folder**:
A folder containing exported `.bas`, `.cls`, and form-related files from an Excel workbook.
_Avoid_: a Python package module.

## Development Notes

- For Python package behavior changes, update `tests` and pin representative before/after conversion cases.
- For PowerShell or batch changes, consider Excel COM, VBIDE access, execution policy, and path resolution effects.
- Treat `build`, `dist`, `.venv`, and `.pytest_cache` as generated artifacts. Do not edit them directly during normal development.
- Keep `example` aligned with README behavior because it documents user-facing workflows.
- Keep VBA documentation comment behavior compatible with the Doxygen-style comment rules used by the Excel macro repositories.

## Example Dialogue

Developer: Is a `'*` comment module-level documentation?
Domain expert: No. `'*` documents the following member. Use `'!` for module-level documentation.
