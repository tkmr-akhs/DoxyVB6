import re
from typing import List
from .codeconv import (
    AbstractCodeParser,
    CodeParseResult,
    CodeElement,
    CodeElementArgument,
    CodeElementAccessibility,
    CodeElementType,
    CannotParseException,
)
from enum import Enum

_ELEM_DEFAULT_ACCESS_LEVEL = "public"
_VAR_DEFAULT_ACCESS_LEVEL = "private"

_ACCESS_LEVEL_RE = r"(Grobal\s+|Public\s+|Friend\s+|Private\s+|Static\s+)"

_VAL_KIND_RE = r"(Const\s+)"
_TELEM_KIND_RE = r"Type\s+"
_EELEM_KIND_RE = r"Enum\s+"
_FELEM_KIND_RE = r"Function\s+"
_SELEM_KIND_RE = r"Sub\s+"
_PGELEM_KIND_RE = r"Property\s+Get\s+"
_PSELEM_KIND_RE = r"Property\s+(Set|Let)\s+"

_ELEM_NAME_RE = r"(\w+)"
_VAL_NAME_RE = r"(\w+)(\([^\)]*\))?"

_VAL_TYPE_RE = r"(?:\s+As\s+([\w.]+))?"
_MVAL_TYPE_RE = r"(?:\s+As\s+(?:New\s+)?([\w.]+))?"
_RET_TYPE_RE = r"(?:\s*As\s+([\w.]+)(\(\))?)?"

_STRLIT_RE = r'"(?:[^"]|"")*"'
_DATELIT_RE = r"\#[^#]*\#"
_BOOLLIT_RE = r"(?:True|False)"
_NUMLIT_RE = (
    r"[+\-]?(?:"
    r"\d+(?:\.\d+)?(?:[ED][+\-]?\d+)?"
    r"|&[H][0-9A-F]+"
    r"|&[O][0-7]+"
    r"|&[B][01]+"
    r")[!#@%&]?"
)
_LIT_RE = f"(?:{_STRLIT_RE}|{_DATELIT_RE}|{_BOOLLIT_RE}|{_NUMLIT_RE})"
_ARGS_RE = r"\s*\(((?:" + _STRLIT_RE + r"|\(\)|[\w\s=,\+\-\*/\.])*)\)"

_VAL_VALUE_RE = r"(?:\s*=\s*(" + _LIT_RE + r"))?"

_VAL_RE = (
    r"^\s*"
    + r"(?:(?:"
    + _ACCESS_LEVEL_RE
    + r"|"
    + _VAL_KIND_RE
    + r")|(?:"
    + _ACCESS_LEVEL_RE
    + _VAL_KIND_RE
    + r")|Dim\s+)"
    + _VAL_NAME_RE
    + _MVAL_TYPE_RE
    + _VAL_VALUE_RE
    + r"\s*$"
)
_TELEM_RE = (
    r"^\s*(?:" + _ACCESS_LEVEL_RE + r")?" + _TELEM_KIND_RE + _ELEM_NAME_RE + r"\s*$"
)
_EELEM_RE = (
    r"^\s*(?:" + _ACCESS_LEVEL_RE + r")?" + _EELEM_KIND_RE + _ELEM_NAME_RE + r"\s*$"
)
_FELEM_RE = (
    r"^\s*(?:"
    + _ACCESS_LEVEL_RE
    + r")?"
    + _FELEM_KIND_RE
    + _ELEM_NAME_RE
    + _ARGS_RE
    + _RET_TYPE_RE
    + r"\s*$"
)
_SELEM_RE = (
    r"^\s*(?:"
    + _ACCESS_LEVEL_RE
    + r")?"
    + _SELEM_KIND_RE
    + _ELEM_NAME_RE
    + _ARGS_RE
    + r"\s*$"
)
_PGELEM_RE = (
    r"^\s*(?:"
    + _ACCESS_LEVEL_RE
    + r")?"
    + _PGELEM_KIND_RE
    + _ELEM_NAME_RE
    + r"\s*\(\s*\)\s*"
    + _RET_TYPE_RE
    + r"\s*$"
)
_PSELEM_RE = (
    r"^\s*(?:"
    + _ACCESS_LEVEL_RE
    + r")?"
    + _PSELEM_KIND_RE
    + _ELEM_NAME_RE
    + _ARGS_RE
    + r"\s*$"
)

_ARG_RE = (
    r"\s*(Optional\s+)?(ByVal\s+|ByRef\s+)?(ParamArray\s+)?"
    + _VAL_NAME_RE
    + _VAL_TYPE_RE
    + r"(?:\s*=\s*("
    + _STRLIT_RE
    + r"|[^,\)]+))?,?"
)


_re_doxy = re.compile(r"^\s*'\*(.*)$")
_re_doxy_class = re.compile(r"^\s*'!(.*)$")
_re_comments = re.compile(r"((?:\"(?:[^\"]|\"\")*\"|[^\"'])*)'.*")
_re_vb_name = re.compile(r"\s*Attribute\s+VB_Name\s+=\s+\"(\w+)\"", re.I)
_re_tag = re.compile(r"^\s*'#\s*(Interface)\s*$")
_re_impl = re.compile(r"^\s*Implements\s+(\w+)\s*$")
_re_arg = re.compile(_ARG_RE, re.I)
_re_values = re.compile(_VAL_RE, re.I)
_re_function = re.compile(_FELEM_RE, re.I)
_re_end_function = re.compile(r"End\s+Function", re.I)
_re_sub = re.compile(_SELEM_RE, re.I)
_re_end_sub = re.compile(r"End\s+Sub", re.I)
_re_type = re.compile(_TELEM_RE, re.I)
_re_end_type = re.compile(r"End\s+Type", re.I)
_re_enum = re.compile(_EELEM_RE, re.I)
_re_enum_mem = re.compile(r"^\s*(\w+)(?:\s*=\s*(\w+))?\s*$", re.I)
_re_end_enum = re.compile(r"End\s+Enum", re.I)
_re_prop_get = re.compile(_PGELEM_RE, re.I)
_re_prop_set = re.compile(_PSELEM_RE, re.I)
_re_end_property = re.compile(r"End\s+Property", re.I)


class Vb6ModuleType(Enum):
    """Enum representing the types of VB6 modules.

    This Enum is used to distinguish between different types of modules
    that can exist in a VB6 project.

    Attributes:
        STANDARD (int): Represents a standard module (.bas file).
        CLASS (int): Represents a class module (.cls file).
        FORM (int): Represents a form module (.frm file).
    """

    STANDARD = 0
    CLASS = 1
    FORM = 2


class Vb6Parser(AbstractCodeParser):
    """Parser for VB6 source code.

    This class is responsible for parsing VB6 code files and converting
    them into structured representations using `CodeElement` objects.
    It supports standard modules, class modules, and form modules.

    Attributes:
        module_type (Vb6ModuleType): The type of the VB6 module being parsed.
    """

    def __init__(self, module_type: Vb6ModuleType):
        """
        Initializes a new instance of the Vb6Parser.

        Args:
            module_type (Vb6ModuleType): The type of VB6 module to be parsed (e.g., STANDARD, CLASS, FORM).
        """
        self.module_type = module_type

    def parse(self, code_lines: List[str]) -> CodeParseResult:
        """
        Parses the given code lines.

        Args:
            code_lines (List[str]): The code lines to parse.

        Returns:
            CodeParseResult: The result of the parsing operation.
        """
        if self.module_type in (Vb6ModuleType.CLASS, Vb6ModuleType.FORM):
            root_elem = self._parse_cls(code_lines)
        else:
            root_elem = self._parse_bas(code_lines)

        return CodeParseResult(root_elem)

    def _parse_cls(self, code_lines: List[str]) -> CodeElement:
        root_elem = CodeElement("root", CodeElementType.OTHER)

        if self.module_type == Vb6ModuleType.FORM:
            target_elem = CodeElement("Form", CodeElementType.NAME_SPACE)
        else:
            target_elem = CodeElement("Class", CodeElementType.NAME_SPACE)
        root_elem.childs.append(target_elem)

        self._process_global_comments(code_lines, target_elem)
        is_intf = self._has_intf_tag(code_lines)
        target_elem = self._process_class_name(code_lines, target_elem, is_intf)
        self._process_impl(code_lines, target_elem)

        inTypeSearch = False
        inSubSearch = False
        inFunctionSearch = False
        inEnumSearch = False
        inPropertySearch = False
        lastProperty: CodeElement = None

        s = ""
        lineContinue = False
        for ln in code_lines:
            # Processes line continuation by combining lines ending with ` _`.
            if (_re_comments.match(ln) is None) and ln.endswith(" _\n"):
                if lineContinue:
                    s += ln[:-2]
                else:
                    s = ln[:-2]
                lineContinue = True
                continue
            else:
                if lineContinue:
                    s += ln
                else:
                    s = ln
                lineContinue = False

            # Processes documentation comment.
            if self._found_doxy_comment(s, target_elem):
                continue

            # Processes the code within each code block.
            if inTypeSearch:
                inTypeSearch, target_elem = self._process_type(s, target_elem)
                continue

            if inSubSearch:
                inSubSearch, target_elem = self._process_sub(s, target_elem)
                continue

            if inFunctionSearch:
                inFunctionSearch, target_elem = self._process_function(s, target_elem)
                continue

            if inPropertySearch:
                inPropertySearch, target_elem = self._process_property(s, target_elem)
                continue

            if inEnumSearch:
                inEnumSearch, target_elem = self._process_enum(s, target_elem)
                continue

            # Processes the start of a code block.
            foundProperty, target_elem, lastProperty = self._find_property_get(
                s, target_elem, lastProperty
            )
            if foundProperty:
                inPropertySearch = True
                continue

            foundProperty, target_elem, lastProperty = self._find_property_set(
                s, target_elem, lastProperty
            )
            if foundProperty:
                inPropertySearch = True
                continue

            foundType, target_elem = self._find_type(s, target_elem)
            if foundType:
                inTypeSearch = True
                continue

            if self._found_member(s, target_elem):
                continue  # For members, there is no internal processing.

            foundFunction, target_elem = self._find_function(s, target_elem)
            if foundFunction:
                inFunctionSearch = True
                continue

            foundSub, target_elem = self._find_sub(s, target_elem)
            if foundSub:
                inSubSearch = True
                continue

            foundEnum, target_elem = self._find_enum(s, target_elem)
            if foundEnum:
                inEnumSearch = True
                continue

        return root_elem

    def _parse_bas(self, code_lines: List[str]) -> CodeElement:
        root_elem = CodeElement("root", CodeElementType.OTHER)
        root_elem.childs.append(
            CodeElement("using", CodeElementType.OTHER, using=["Class"])
        )
        target_elem = CodeElement("Standard", CodeElementType.NAME_SPACE)
        root_elem.childs.append(target_elem)

        self._process_global_comments(code_lines, target_elem)
        target_elem = self._process_class_name(code_lines, target_elem)

        inTypeSearch = False

        inSubSearch = False
        inFunctionSearch = False
        inEnumSearch = False

        s = ""
        lineContinue = False
        for ln in code_lines:
            # Processes line continuation by combining lines ending with ` _`.
            if (_re_comments.match(ln) is None) and ln.endswith(" _\n"):
                if lineContinue:
                    s += ln[:-2]
                else:
                    s = ln[:-2]
                lineContinue = True
                continue
            else:
                if lineContinue:
                    s += ln
                else:
                    s = ln
                lineContinue = False

            # Processes documentation comment.
            if self._found_doxy_comment(s, target_elem):
                continue

            # Processes the code within each code block.
            if inTypeSearch:
                inTypeSearch, target_elem = self._process_type(s, target_elem)
                continue

            if inSubSearch:
                inSubSearch, target_elem = self._process_sub(s, target_elem)
                continue

            if inFunctionSearch:
                inFunctionSearch, target_elem = self._process_function(s, target_elem)
                continue

            if inEnumSearch:
                inEnumSearch, target_elem = self._process_enum(s, target_elem)
                continue

            # Processes the start of a code block.
            foundType, target_elem = self._find_type(s, target_elem)
            if foundType:
                inTypeSearch = True
                continue

            if self._found_member(s, target_elem):
                continue  # For members, there is no internal processing.

            foundFunction, target_elem = self._find_function(s, target_elem)
            if foundFunction:
                inFunctionSearch = True
                continue

            foundSub, target_elem = self._find_sub(s, target_elem)
            if foundSub:
                inSubSearch = True
                continue

            foundEnum, target_elem = self._find_enum(s, target_elem)
            if foundEnum:
                inEnumSearch = True
                continue

        return root_elem

    def _strip_comments(self, str_):
        """Removes comments from a line of code."""
        my_match = _re_comments.match(str_)
        if my_match is not None:
            return my_match.group(1)
        else:
            return str_

    def _build_args_list(self, args_str: str) -> List[CodeElementArgument]:
        """
        Parses a string of arguments into a list of CodeElementArgument objects.

        This method processes the provided argument string, identifying individual
        arguments, their types, default values, and additional properties such as
        whether they are optional, passed by reference, or represent variable-length arguments.

        Args:
            args_str (str): The string containing arguments, typically extracted from a
                            function or subroutine definition.

        Returns:
            List[CodeElementArgument]: A list of CodeElementArgument objects representing
                                    the parsed arguments.
        """
        if args_str is None:
            args_str = ""
        else:
            args_str = args_str.strip()

        result: list[CodeElementArgument] = []

        args_match_result = _re_arg.findall(args_str)

        # print(_re_arg.pattern)
        # print(args_str)

        if args_match_result is None:
            return result

        for i, item in enumerate(args_match_result):

            # for j, sub_item in enumerate(item):
            #     print(f"{i}-{j}: {sub_item}")

            opt_str: str = item[0].strip()
            val_ref: str = item[1].strip()
            param_arr: str = item[2].strip()
            arg_name: str = item[3].strip()

            arr_str: str = item[4].strip()
            arg_type: str = item[5].strip()
            arg_type = self._format_array_type(arg_type, arr_str)

            arg_default, is_str = self._extract_string_literal(item[6].strip())

            is_ref = val_ref.lower() != "byval"
            is_opt = opt_str.lower() == "optional"
            is_vlargs = param_arr.lower() == "paramarray"

            arg_obj = CodeElementArgument(
                arg_name,
                arg_type,
                is_reference=is_ref,
                is_optional=is_opt,
                is_vlargs=is_vlargs,
                is_str=is_str,
            )

            if arg_default != "" or is_str:
                arg_obj.default_value = arg_default

            result.append(arg_obj)

        return result

    def _get_accessibility(
        self, s: str, default_access: str
    ) -> tuple[CodeElementAccessibility, bool]:
        """Determines the accessibility and static status of a code element."""
        if s is None or s == "":
            accessibility = default_access
        else:
            accessibility = s.strip().lower()

        if accessibility == "private":
            return CodeElementAccessibility.PRIVATE, False
        elif accessibility == "grobal":
            return CodeElementAccessibility.PUBLIC, False
        elif accessibility == "public":
            return CodeElementAccessibility.PUBLIC, False
        elif accessibility == "friend":
            return CodeElementAccessibility.INTERNAL, False
        elif accessibility == "static":
            return CodeElementAccessibility.PUBLIC, True

    def _extract_string_literal(self, target_str: str) -> tuple[str, bool]:
        """
        Processes a string literal, handling escaped characters.

        Args:
            target_str (str): The string literal to process.

        Returns:
            tuple[str, bool]: The processed string and a boolean indicating whether it is a string literal.
        """
        if target_str is None:
            return "", False

        is_str = target_str.startswith('"')

        if is_str:
            result_str = target_str[1:-1].replace('""', '"')
        else:
            result_str = target_str

        return result_str, is_str

    def _format_array_type(self, var_type: str, arr_str: str) -> str:
        """
        Formats the array type by appending array indicators.

        Args:
            var_type (str): The base type of the variable.
            arr_str (str): The array specification string.

        Returns:
            str: The formatted array type.
        """
        if var_type is None:
            var_type = ""
        else:
            var_type = var_type.strip()

        if arr_str is None:
            arr_str = ""
        else:
            arr_str = arr_str.strip()

        if var_type == "":
            var_type = "Variant"

        if arr_str == "":
            return var_type
        else:
            return var_type + "[]"

    def _process_global_comments(self, r: List[str], target_elem: CodeElement):
        for s in r:
            gcom = _re_doxy_class.match(s)
            if gcom is not None:
                gcom_str = gcom.group(1)
                if gcom_str is not None:
                    gcom_obj = CodeElement(
                        "", CodeElementType.DOC_COMMENT_LINE, elem_value=gcom_str
                    )
                    target_elem.childs.append(gcom_obj)

    def _has_intf_tag(self, code_lines: List[str]) -> bool:
        for code_line in code_lines:
            match_result = _re_tag.match(code_line)
            if not match_result is None and match_result.group(1) == "Interface":
                return True
        return False

    def _process_class_name(
        self, r: List[str], target_elem: CodeElement, is_intf: bool = False
    ) -> CodeElement:
        class_name = "DummyName"
        for s in r:
            match_result = _re_vb_name.match(self._strip_comments(s))
            if match_result is not None:
                class_name = match_result.group(1)
                break

        if is_intf:
            class_obj = CodeElement(class_name, CodeElementType.INTERFACE)
        else:
            class_obj = CodeElement(class_name, CodeElementType.CLASS)

        target_elem.childs.append(class_obj)
        return class_obj

    def _process_impl(self, r: List[str], class_elem: CodeElement):
        super_class: str = None
        for s in r:
            match_result = _re_impl.match(self._strip_comments(s))
            if match_result is not None:
                super_class = match_result.group(1)
                break

        if super_class is None:
            return

        class_elem.others["implements"] = [super_class]

    def _found_doxy_comment(self, s, target_elem: CodeElement) -> bool:
        doxy_result = _re_doxy.match(s)
        if doxy_result is None:
            return False

        com_obj = CodeElement(
            "", CodeElementType.DOC_COMMENT_LINE, elem_value=doxy_result.group(1)
        )
        target_elem.childs.append(com_obj)
        return True

    def _found_member(self, s: str, target_elem: CodeElement) -> bool:
        match_result = _re_values.match(self._strip_comments(s))

        # print(_re_values.pattern)
        # print(self._strip_comments(s))

        if match_result is None:
            return False

        # for i, var in enumerate(member_result.groups(), start=1):
        #    print(f"{i}: {var}")

        if not match_result.group(1) is None:
            access_str = match_result.group(1).strip()
        elif not match_result.group(3) is None:
            access_str = match_result.group(3).strip()
        else:
            access_str = ""

        var_access, is_static = self._get_accessibility(
            access_str, _VAR_DEFAULT_ACCESS_LEVEL
        )

        if not match_result.group(2) is None:
            const_str = match_result.group(2).strip()
        elif not match_result.group(4) is None:
            const_str = match_result.group(4).strip()
        else:
            const_str = ""

        var_name = match_result.group(5).strip()

        arr_str = match_result.group(6)
        var_type = match_result.group(7)
        var_type = self._format_array_type(var_type, arr_str)

        var_value, is_str = self._extract_string_literal(match_result.group(8))

        if const_str.lower() == "const":
            var_obj = CodeElement(
                var_name,
                CodeElementType.CONST,
                return_type=var_type,
                accessibility=var_access,
                elem_value=var_value,
                is_str=is_str,
            )
        else:
            var_obj = CodeElement(
                var_name,
                CodeElementType.VAR,
                return_type=var_type,
                accessibility=var_access,
            )
            arg_obj = CodeElementArgument("", var_type, is_reference=False)
            var_obj.arguments.append(arg_obj)

        target_elem.childs.append(var_obj)
        return True

    def _find_function(
        self, s: str, target_elem: CodeElement
    ) -> tuple[bool, CodeElement]:
        match_result = _re_function.match(self._strip_comments(s))

        # print(_re_function.pattern)
        # print(self._strip_comments(s))

        if match_result is None:
            return False, target_elem

        # for i, var in enumerate(match_result.groups(), start=1):
        #     print(f"{i}: {var}")

        access_level, is_static = self._get_accessibility(
            match_result.group(1), _ELEM_DEFAULT_ACCESS_LEVEL
        )
        func_name = match_result.group(2).strip()
        args_list = self._build_args_list(match_result.group(3))

        ret_type = match_result.group(4)
        ret_arr = match_result.group(5)
        ret_type = self._format_array_type(ret_type, ret_arr)

        func_elem = CodeElement(
            func_name,
            CodeElementType.FUNC,
            return_type=ret_type,
            is_static=is_static,
            accessibility=access_level,
        )

        func_elem.arguments.extend(args_list)
        target_elem.childs.append(func_elem)
        return True, func_elem

    def _process_function(
        self, s: str, target_elem: CodeElement
    ) -> tuple[bool, CodeElement]:
        if _re_end_function.match(self._strip_comments(s)):
            return False, target_elem.parent

        return True, target_elem

    def _find_sub(self, s: str, target_elem: CodeElement) -> tuple[bool, CodeElement]:

        match_result = _re_sub.match(self._strip_comments(s))

        # print(_re_sub.pattern)
        # print(self._strip_comments(s))

        if match_result is None:
            return False, target_elem

        # for i, var in enumerate(match_result.groups(), start=1):
        #    print(f"{i}: {var}")

        access_level, is_static = self._get_accessibility(
            match_result.group(1), _ELEM_DEFAULT_ACCESS_LEVEL
        )
        sub_name = match_result.group(2).strip()
        args_list = self._build_args_list(match_result.group(3))

        sub_elem = CodeElement(
            sub_name,
            CodeElementType.FUNC,
            is_static=is_static,
            accessibility=access_level,
        )

        sub_elem.arguments.extend(args_list)
        target_elem.childs.append(sub_elem)
        return True, sub_elem

    def _process_sub(
        self, s: str, target_elem: CodeElement
    ) -> tuple[bool, CodeElement]:
        if _re_end_sub.match(self._strip_comments(s)):
            return False, target_elem.parent

        return True, target_elem

    def _find_type(self, s: str, target_elem: CodeElement) -> tuple[bool, CodeElement]:
        match_result = _re_type.match(self._strip_comments(s))

        # print(_re_type.pattern)
        # print(self._strip_comments(s))

        if match_result is None:
            return False, target_elem

        # for i, var in enumerate(match_result.groups(), start=1):
        #     print(f"{i}: {var}")

        access_level, is_static = self._get_accessibility(
            match_result.group(1), _ELEM_DEFAULT_ACCESS_LEVEL
        )
        type_name = match_result.group(2).strip()

        sub_elem = CodeElement(
            type_name,
            CodeElementType.STRUCT,
            accessibility=access_level,
        )

        target_elem.childs.append(sub_elem)
        return True, sub_elem

    def _process_type(
        self, s: str, target_elem: CodeElement
    ) -> tuple[bool, CodeElement]:
        if _re_end_type.match(self._strip_comments(s)):
            return False, target_elem.parent

        self._found_member(s, target_elem)
        return True, target_elem

    def _find_enum(self, s: str, target_elem: CodeElement) -> tuple[bool, CodeElement]:
        match_result = _re_enum.match(self._strip_comments(s))

        # print(_re_enum.pattern)
        # print(self._strip_comments(s))

        if match_result is None:
            return False, target_elem

        # for i, var in enumerate(match_result.groups(), start=1):
        #    print(f"{i}: {var}")

        access_level, is_static = self._get_accessibility(
            match_result.group(1), _ELEM_DEFAULT_ACCESS_LEVEL
        )
        enum_name = match_result.group(2).strip()

        enum_elem = CodeElement(
            enum_name,
            CodeElementType.ENUM,
            accessibility=access_level,
        )

        target_elem.childs.append(enum_elem)
        return True, enum_elem

    def _process_enum(
        self, s: str, target_elem: CodeElement
    ) -> tuple[bool, CodeElement]:
        if _re_end_enum.match(self._strip_comments(s)):
            return False, target_elem.parent

        match_result = _re_enum_mem.match(self._strip_comments(s))

        # print(_re_enum_mem.pattern)
        # print(self._strip_comments(s))

        if not match_result is None:
            # for i, var in enumerate(match_result.groups(), start=1):
            #     print(f"{i}: {var}")
            mem_name = match_result.group(1).strip()
            mem_value = match_result.group(2)

            if mem_value is None:
                mem_value = ""

            mem_obj = CodeElement(mem_name, CodeElementType.CONST, elem_value=mem_value)
            target_elem.childs.append(mem_obj)

        return True, target_elem

    def _find_property_get(
        self, s: str, target_elem: CodeElement, prev_elem: CodeElement
    ) -> tuple[bool, CodeElement, CodeElement]:
        match_result = _re_prop_get.match(self._strip_comments(s))

        # print(_re_prop_get.pattern)
        # print(self._strip_comments(s))

        if match_result is None:
            return False, target_elem, prev_elem

        # for i, var in enumerate(match_result.groups(), start=1):
        #    print(f"{i}: {var}")

        access_level, is_static = self._get_accessibility(
            match_result.group(1), _ELEM_DEFAULT_ACCESS_LEVEL
        )
        prop_name = match_result.group(2).strip()

        ret_type = match_result.group(3)
        ret_arr = match_result.group(4)
        ret_type = self._format_array_type(ret_type, ret_arr)

        result_elem = CodeElement(
            prop_name,
            CodeElementType.FUNC,
            is_static=is_static,
            accessibility=access_level,
        )

        if not prev_elem is None and prev_elem.name == prop_name:
            prev_elem.return_type = prev_elem.arguments[0].type
            result_elem = prev_elem
        else:
            result_elem = CodeElement(
                prop_name,
                CodeElementType.PROPERTY,
                return_type=ret_type,
                accessibility=access_level,
                is_static=is_static,
            )
            target_elem.childs.append(result_elem)

        return True, result_elem, result_elem

    def _find_property_set(
        self, s: str, target_elem: CodeElement, prev_elem: CodeElement
    ) -> tuple[bool, CodeElement, CodeElement]:
        match_result = _re_prop_set.match(self._strip_comments(s))

        # print(_re_prop_set.pattern)
        # print(self._strip_comments(s))

        if match_result is None:
            return False, target_elem, prev_elem

        # for i, var in enumerate(match_result.groups(), start=1):
        #     print(f"{i}: {var}")

        access_level, is_static = self._get_accessibility(
            match_result.group(1), _ELEM_DEFAULT_ACCESS_LEVEL
        )
        prop_name = match_result.group(3).strip()
        args_list = self._build_args_list(match_result.group(4))

        if not prev_elem is None and prev_elem.name == prop_name:
            if len(prev_elem.arguments) == 0:
                prev_elem.arguments.append(args_list[0])
            prev_elem.return_type = prev_elem.arguments[0].type
            result_elem = prev_elem
        else:
            result_elem = CodeElement(
                prop_name,
                CodeElementType.PROPERTY,
                accessibility=access_level,
                is_static=is_static,
            )
            result_elem.arguments.append(args_list[0])
            target_elem.childs.append(result_elem)

        return True, result_elem, result_elem

    def _process_property(
        self, s: str, target_elem: CodeElement
    ) -> tuple[bool, CodeElement]:
        if _re_end_property.match(self._strip_comments(s)):
            return False, target_elem.parent

        return True, target_elem
