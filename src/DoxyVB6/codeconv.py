from typing import List, Iterator
from abc import ABCMeta, abstractmethod
from enum import Enum


class CodeElementType(Enum):
    """Enum representing different types of code elements.

    Attributes:
        OTHER (int): Represents an unspecified or other type of code element.
        VAR (int): Represents a variable.
        CONST (int): Represents a constant.
        FUNC (int): Represents a function or method.
        STRUCT (int): Represents a structure.
        DOC_COMMENT_LINE (int): Represents a single-line documentation comment.
        DOC_COMMENT_MULTI (int): Represents a multi-line documentation comment.
        CLASS (int): Represents a class.
        INTERFACE (int): Represents a class.
        ENUM (int): Represents an enumeration.
        NAME_SPACE (int): Represents a namespace.
        PROPERTY (int): Represents a property.
    """

    OTHER = 0
    VAR = 1
    CONST = 2
    FUNC = 3
    STRUCT = 4
    DOC_COMMENT_LINE = 5
    DOC_COMMENT_MULTI = 6
    CLASS = 7
    INTERFACE = 8
    ENUM = 9
    NAME_SPACE = 10
    PROPERTY = 11


class CodeElementAccessibility(Enum):
    """Enum representing different levels of code element accessibility.

    Attributes:
        UNDEF (int): Represents undefined or unknown accessibility.
        PUBLIC (int): Represents public accessibility, accessible from anywhere.
        PROTECTED (int): Represents protected accessibility, accessible within the class and its subclasses.
        INTERNAL (int): Represents internal accessibility, accessible within the same assembly or module.
        PRIVATE (int): Represents private accessibility, accessible only within the containing class or module.
    """

    UNDEF = 0
    PUBLIC = 1
    PROTECTED = 2
    INTERNAL = 4
    PRIVATE = 8


class CodeElementArgument:
    """Class representing an argument for a code element."""

    def __init__(
        self,
        arg_name: str,
        arg_type: str,
        is_reference: bool = False,
        is_optional: bool = False,
        is_vlargs: bool = False,
        is_kwargs: bool = False,
        default_value: str = "default",
        is_str: bool = False,
    ):
        """
        Initializes a CodeElementArgument.

        Args:
            arg_name (str): The name of the argument.
            arg_type (str): The type of the argument.
            is_reference (bool, optional): Whether the argument is passed by reference. Defaults to False.
            is_optional (bool, optional): Whether the argument is optional. Defaults to False.
            is_vlargs (bool, optional): Whether the argument is a variable-length argument. Defaults to False.
            is_kwargs (bool, optional): Whether the argument is a keyword argument. Defaults to False.
            default_value (str, optional): The default value of the argument. Defaults to "default".
            is_str (bool, optional): Whether the argument is represented as a string. Defaults to False.
        """
        self.name = arg_name
        self.type = arg_type
        self.is_reference = is_reference
        self.is_optional = is_optional
        self.is_vlargs = is_vlargs
        self.is_kwargs = is_kwargs
        self.default_value = default_value
        self.is_str = is_str


class CodeElementList:
    """Class representing a list of code elements."""

    def __init__(self, parent_elem: "CodeElement"):
        """
        Initializes a CodeElementList.

        Args:
            parent_elem (CodeElement): The parent code element of the list.
        """
        self._parent = parent_elem
        self._members: List["CodeElement"] = []

    @property
    def parent(self) -> "CodeElement":
        """
        Gets the parent code element.

        Returns:
            CodeElement: The parent code element.
        """
        return self._parent

    def __getitem__(self, key) -> "CodeElement":
        return self._members[key]

    def __setitem__(self, key, value: "CodeElement"):
        value._parent = self.parent
        self._members[key] = value

    def __delitem__(self, key):
        self._members[key]._parent = None
        del self._members[key]

    def __contains__(self, key) -> bool:
        return key in self._members

    def __len__(self) -> int:
        return len(self._members)

    def __iter__(self) -> Iterator["CodeElement"]:
        return iter(self._members)

    def append(self, value: "CodeElement"):
        """
        Appends a code element to the list.

        Args:
            value (CodeElement): The code element to append.
        """
        value._parent = self.parent
        self._members.append(value)

    def insert(self, index, value: "CodeElement"):
        """
        Inserts a code element into the list at a specific index.

        Args:
            index (int): The index at which to insert the code element.
            value (CodeElement): The code element to insert.
        """
        value._parent = self.parent
        self._members.insert(index, value)

    def clear(self):
        """Clears all code elements from the list."""
        for member in self._members:
            member._parent = None
        self._members.clear()


class CodeElement:
    """Class representing a code element."""

    def __init__(
        self,
        elem_name: str,
        elem_type: CodeElementType,
        return_type: str = "void",
        is_static: str = False,
        accessibility: CodeElementAccessibility = CodeElementAccessibility.UNDEF,
        elem_value: str = "",
        is_str: bool = False,
        **kwargs,
    ):
        """
        Initializes a CodeElement.

        Args:
            elem_name (str): The name of the code element.
            elem_type (CodeElementType): The type of the code element.
            return_type (str, optional): The return type of the code element. Defaults to "void".
            is_static (bool, optional): Whether the code element is static. Defaults to False.
            accessibility (CodeElementAccessibility, optional): The accessibility of the code element. Defaults to CodeElementAccessibility.UNDEF.
            elem_value (str, optional): The value of the code element. Defaults to "".
            is_str (bool, optional): Whether the code element is represented as a string. Defaults to False.
        """
        self.name = elem_name
        self.elem_type = elem_type
        self.return_type = return_type
        self.is_static = is_static
        self.accessibility = accessibility
        self.value = elem_value
        self.is_str = is_str
        self.others = kwargs
        self._parent: "CodeElement" = None

        self._childs = CodeElementList(self)
        self._args: List[CodeElementArgument] = []

    @property
    def parent(self) -> CodeElementList:
        """
        Gets the parent of the code element.

        Returns:
            CodeElementList: The parent code element list.
        """
        return self._parent

    @property
    def childs(self) -> CodeElementList:
        """
        Gets the child elements of the code element.

        Returns:
            CodeElementList: The child code element list.
        """
        return self._childs

    @property
    def arguments(self) -> List[CodeElementArgument]:
        """
        Gets the arguments of the code element.

        Returns:
            List[CodeElementArgument]: The list of arguments.
        """
        return self._args


class CodeParseResult:
    """Class representing the result of a code parsing operation."""

    def __init__(self, result_root: CodeElement):
        """
        Initializes a CodeParseResult.

        Args:
            result_root (CodeElement): The root element of the parse result.
        """
        self.root = result_root


class AbstractCodeParser(metaclass=ABCMeta):
    """Abstract base class for code parsers."""

    @abstractmethod
    def parse(self, code_lines: List[str]) -> CodeParseResult:
        """
        Parses the given code lines.

        Args:
            code_lines (List[str]): The code lines to parse.

        Returns:
            CodeParseResult: The result of the parsing operation.
        """
        pass


class AbstractCodeGenerator(metaclass=ABCMeta):
    """Abstract base class for code generators."""

    @abstractmethod
    def generate(self, parse_result: CodeParseResult) -> List[str]:
        """
        Generates code from the given parse result.

        Args:
            parse_result (CodeParseResult): The result of the code parsing operation.

        Returns:
            List[str]: The generated code lines.
        """
        pass


class CannotParseException(Exception):
    """Exception raised when code parsing fails.

    This exception is used to indicate that the parsing of the provided code lines
    could not be completed successfully.
    """

    pass


class CannotGenerateException(Exception):
    """Exception raised when code generation fails.

    This exception is used to indicate that the generation of code based on
    parsing results could not be completed successfully.
    """

    pass


def split_args(
    arg_list: List[CodeElementArgument],
) -> tuple[
    List[CodeElementArgument],
    List[CodeElementArgument],
    List[CodeElementArgument],
    List[CodeElementArgument],
]:
    """
    Splits a list of arguments into mandatory, optional, variable-length, and keyword arguments.

    Args:
        arg_list (List[CodeElementArgument]): The list of arguments to split.

    Returns:
        tuple[List[CodeElementArgument], List[CodeElementArgument], List[CodeElementArgument], List[CodeElementArgument]]:
        A tuple containing lists of mandatory, optional, variable-length, and keyword arguments.
    """
    mandatorys = []
    optionals = []
    vlargs = []
    kwargs = []

    for arg_item in arg_list:
        if arg_item.is_optional:
            optionals.append(arg_item)
        elif arg_item.is_vlargs:
            vlargs.append(arg_item)
        elif arg_item.is_kwargs:
            kwargs.append(arg_item)
        else:
            mandatorys.append(arg_item)

    return (mandatorys, optionals, vlargs, kwargs)
