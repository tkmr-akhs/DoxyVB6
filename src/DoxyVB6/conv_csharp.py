from typing import List
from .codeconv import (
    AbstractCodeGenerator,
    CodeParseResult,
    CodeElement,
    CodeElementArgument,
    CodeElementType,
    CodeElementAccessibility,
    CannotGenerateException,
    split_args,
)

_INDENT_STR = "    "


# Replacement map corresponding to basic C# escape sequences
_replacements = {
    "\\": "\\\\",  # Backslash
    '"': '\\"',  # Double quote
    "\0": "\\0",  # Null character
    "\a": "\\a",  # Bell
    "\b": "\\b",  # Backspace
    "\f": "\\f",  # Form feed
    "\n": "\\n",  # Line feed (newline)
    "\r": "\\r",  # Carriage return
    "\t": "\\t",  # Horizontal tab
    "\v": "\\v",  # Vertical tab
}


class CsharpGenerator(AbstractCodeGenerator):
    def generate(self, parse_result: CodeParseResult) -> List[str]:
        """
        Generates code from the given parse result.

        Args:
            parse_result (CodeParseResult): The result of the code parsing operation.

        Returns:
            List[str]: The generated code lines.
        """
        code_lines: List[str] = []
        self._generate_common(code_lines, 0, parse_result.root)
        return code_lines

    def _generate_common(
        self,
        code_lines: List[str],
        indent: int,
        target_elem: CodeElement,
        as_intf: bool = False,
    ):
        if target_elem.elem_type == CodeElementType.VAR:
            self._generate_var(code_lines, indent, target_elem)
        elif target_elem.elem_type == CodeElementType.CONST:
            self._generate_const(code_lines, indent, target_elem)
        elif target_elem.elem_type == CodeElementType.FUNC:
            self._generate_func(code_lines, indent, target_elem, as_intf)
        elif target_elem.elem_type == CodeElementType.STRUCT:
            self._generate_struct(code_lines, indent, target_elem)
        elif target_elem.elem_type == CodeElementType.DOC_COMMENT_LINE:
            self._generate_doc_line(code_lines, indent, target_elem)
        elif target_elem.elem_type == CodeElementType.DOC_COMMENT_MULTI:
            self._generate_doc_multi(code_lines, indent, target_elem)
        elif target_elem.elem_type == CodeElementType.CLASS:
            self._generate_class(code_lines, indent, target_elem)
        elif target_elem.elem_type == CodeElementType.INTERFACE:
            self._generate_intf(code_lines, indent, target_elem)
        elif target_elem.elem_type == CodeElementType.ENUM:
            self._generate_enum(code_lines, indent, target_elem)
        elif target_elem.elem_type == CodeElementType.NAME_SPACE:
            self._generate_namespace(code_lines, indent, target_elem)
        elif target_elem.elem_type == CodeElementType.PROPERTY:
            self._generate_property(code_lines, indent, target_elem)
        else:
            raise NotImplementedError()

    def _get_indent_str(self, indent: int) -> str:
        """Gets the indentation string based on the given indentation level."""
        return _INDENT_STR * indent

    def _get_access_str(self, target_elem: CodeElement) -> str:
        """Gets the access modifier string for the given code element."""
        access = target_elem.accessibility
        if access == CodeElementAccessibility.PUBLIC:
            return "public "
        elif access == CodeElementAccessibility.PROTECTED:
            return "protected "
        elif access == CodeElementAccessibility.INTERNAL:
            return "internal "
        elif access == CodeElementAccessibility.PRIVATE:
            return "private "
        else:
            return ""

    def _get_static_str(self, target_elem: CodeElement) -> str:
        """Gets the static keyword string for the given code element."""
        if target_elem.is_static:
            return "static "
        else:
            return ""

    def _get_value_str(self, target_value: str, is_str: bool) -> str:
        """
        Converts the given value into a valid C# literal string.

        Args:
            target_value (str): The value to be converted.
            is_str (bool): Whether the value is a string.

        Returns:
            str: The escaped string literal or the original value.
        """
        if is_str:
            escaped_chars = []
            for ch in target_value:
                if ch in _replacements:
                    escaped_chars.append(_replacements[ch])
                else:
                    # 上記以外の文字はそのまま追加する。
                    # （必要に応じて Unicode エスケープなど追加処理を行うことも可能）
                    escaped_chars.append(ch)

            # ダブルクォートで囲んで返す
            return '"' + "".join(escaped_chars) + '"'
        else:
            return target_value

    def _get_valref_str(self, target_arg: CodeElementArgument) -> str:
        """Gets the reference keyword string (e.g., "ref") for the given argument."""
        if target_arg.is_reference:
            return "ref "
        else:
            return ""

    def _get_args_str(self, target_elem: CodeElement) -> str:
        """Generates the argument string for a method or function."""

        def _get_args_str_core(arg_obj: CodeElementArgument) -> str:
            val_ref = self._get_valref_str(arg_obj)
            if arg_obj.is_optional:
                default_value = self._get_value_str(
                    arg_obj.default_value, arg_obj.is_str
                )
                return f"{val_ref}{arg_obj.type} {arg_obj.name} = {default_value}"
            else:
                return f"{val_ref}{arg_obj.type} {arg_obj.name}"

        result: List[str] = []

        if len(target_elem.arguments) == 0:
            return ""

        result.append(_get_args_str_core(target_elem.arguments[0]))

        for arg_item in target_elem.arguments[1:]:
            result.append(", ")
            result.append(_get_args_str_core(arg_item))

        return "".join(result)

    def _get_getset_str(self, target_elem: CodeElement) -> str:
        """Generates the argument string for a method or function."""
        is_get = not target_elem.return_type in ("void", "", None)
        is_set = len(target_elem.arguments) != 0

        if is_get and not is_set:
            return "get;"
        elif not is_get and is_set:
            return "set;"
        elif is_get and is_set:
            return "get; set;"
        else:
            raise CannotGenerateException(
                "The property has neither a getter nor a setter."
            )

    def _generate_var(
        self, code_lines: List[str], indent: int, target_elem: CodeElement
    ):
        indent_str = self._get_indent_str(indent)
        elem_access = self._get_access_str(target_elem)
        elem_static = self._get_static_str(target_elem)
        code_lines.append(
            indent_str
            + f"{elem_access}{elem_static}{target_elem.return_type} {target_elem.name};"
        )
        code_lines.append(indent_str)

    def _generate_const(
        self, code_lines: List[str], indent: int, target_elem: CodeElement
    ):
        indent_str = self._get_indent_str(indent)
        elem_access = self._get_access_str(target_elem)
        elem_value = self._get_value_str(target_elem.value, target_elem.is_str)
        code_lines.append(
            indent_str
            + f"{elem_access}const {target_elem.return_type} {target_elem.name} = {elem_value};"
        )
        code_lines.append(indent_str)

    def _generate_doc_line(
        self, code_lines: List[str], indent: int, target_elem: CodeElement
    ):
        indent_str = self._get_indent_str(indent)
        code_lines.append(indent_str + f"///{target_elem.value}")

    def _generate_doc_multi(
        self, code_lines: List[str], indent: int, target_elem: CodeElement
    ):
        raise NotImplementedError()

    def _generate_func(
        self,
        code_lines: List[str],
        indent: int,
        target_elem: CodeElement,
        as_intf: bool = False,
    ):
        indent_str = self._get_indent_str(indent)
        elem_access = self._get_access_str(target_elem)
        elem_static = self._get_static_str(target_elem)
        elem_args = self._get_args_str(target_elem)
        if as_intf:
            code_lines.append(
                indent_str
                + f"{elem_access}{elem_static}{target_elem.return_type} {target_elem.name}({elem_args});"
            )
            code_lines.append(indent_str)
        else:
            code_lines.append(
                indent_str
                + f"{elem_access}{elem_static}{target_elem.return_type} {target_elem.name}({elem_args})"
            )
            code_lines.append(indent_str + "{")
            # Skipping the processing of child elements for now
            code_lines.append(indent_str + "}")
            code_lines.append(indent_str)

    def _generate_property(
        self, code_lines: List[str], indent: int, target_elem: CodeElement
    ):
        indent_str = self._get_indent_str(indent)
        elem_access = self._get_access_str(target_elem)
        elem_static = self._get_static_str(target_elem)
        elem_getset = self._get_getset_str(target_elem)
        code_lines.append(
            indent_str
            + f"{elem_access}{elem_static}{target_elem.return_type} {target_elem.name} {{ {elem_getset} }})"
        )

    def _generate_struct(
        self, code_lines: List[str], indent: int, target_elem: CodeElement
    ):
        indent_str = self._get_indent_str(indent)
        indent_str_mem = self._get_indent_str(indent + 1)
        elem_access = self._get_access_str(target_elem)
        code_lines.append(indent_str + f"{elem_access}struct {target_elem.name}")
        code_lines.append("{")
        for child_elem in target_elem.childs:
            if child_elem.elem_type == CodeElementType.DOC_COMMENT_LINE:
                self._generate_doc_line(code_lines, indent + 1, child_elem)
            elif child_elem.elem_type == CodeElementType.DOC_COMMENT_MULTI:
                self._generate_doc_multi(code_lines, indent + 1, child_elem)
            else:
                code_lines.append(
                    indent_str_mem
                    + f"public {child_elem.return_type} {child_elem.name};"
                )
                code_lines.append(indent_str)
        code_lines.append("}")

    def _generate_enum(
        self, code_lines: List[str], indent: int, target_elem: CodeElement
    ):
        indent_str = self._get_indent_str(indent)
        indent_str_mem = self._get_indent_str(indent + 1)
        elem_access = self._get_access_str(target_elem)
        code_lines.append(indent_str + f"{elem_access}enum {target_elem.name}")
        code_lines.append("{")
        for child_elem in target_elem.childs:
            if child_elem.elem_type == CodeElementType.DOC_COMMENT_LINE:
                self._generate_doc_line(code_lines, indent + 1, child_elem)
            elif child_elem.elem_type == CodeElementType.DOC_COMMENT_MULTI:
                self._generate_doc_multi(code_lines, indent + 1, child_elem)
            else:
                if child_elem.value == "":
                    code_lines.append(indent_str_mem + f"{child_elem.name},")
                else:
                    code_lines.append(
                        indent_str_mem + f"{child_elem.name} = {child_elem.value},"
                    )
        code_lines.append("}")

    def _generate_class(
        self, code_lines: List[str], indent: int, target_elem: CodeElement
    ):
        indent_str = self._get_indent_str(indent)
        elem_access = self._get_access_str(target_elem)
        elem_static = self._get_static_str(target_elem)
        if "super" in target_elem.others:
            elem_super = " : " + ", ".join(target_elem.others["extends"])
        else:
            elem_super = ""

        if "implements" in target_elem.others:
            if elem_super == "":
                elem_super = " : " + ", ".join(target_elem.others["implements"])
            else:
                elem_super = (
                    elem_super + ", " + ", ".join(target_elem.others["implements"])
                )

        code_lines.append(
            indent_str
            + f"{elem_access}{elem_static}class {target_elem.name}{elem_super}"
        )
        code_lines.append(indent_str + "{")
        for child_elem in target_elem.childs:
            self._generate_common(code_lines, indent + 1, child_elem)
        code_lines.append(indent_str + "}")
        code_lines.append(indent_str)

    def _generate_intf(
        self, code_lines: List[str], indent: int, target_elem: CodeElement
    ):
        indent_str = self._get_indent_str(indent)
        elem_access = self._get_access_str(target_elem)
        elem_static = self._get_static_str(target_elem)
        if "super" in target_elem.others:
            elem_super = " : " + ", ".join(target_elem.others["extends"])
        else:
            elem_super = ""

        if "implements" in target_elem.others:
            if elem_super == "":
                elem_super = " : " + ", ".join(target_elem.others["implements"])
            else:
                elem_super = (
                    elem_super + ", " + ", ".join(target_elem.others["implements"])
                )

        code_lines.append(
            indent_str
            + f"{elem_access}{elem_static}interface {target_elem.name}{elem_super}"
        )
        code_lines.append(indent_str + "{")
        for child_elem in target_elem.childs:
            self._generate_common(code_lines, indent + 1, child_elem, True)
        code_lines.append(indent_str + "}")
        code_lines.append(indent_str)

    def _generate_namespace(
        self, code_lines: List[str], indent: int, target_elem: CodeElement
    ):
        indent_str = self._get_indent_str(indent)
        code_lines.append(indent_str + f"namespace {target_elem.name}")
        code_lines.append("{")
        for child_elem in target_elem.childs:
            self._generate_common(code_lines, indent + 1, child_elem)
        code_lines.append("}")
