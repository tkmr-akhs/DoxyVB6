import pytest
import pytest_mock
import pytest_raises

from DoxyVB6.codeconv import (
    CodeElement,
    CodeElementType,
    CodeElementAccessibility,
    CodeElementArgument,
)
from DoxyVB6 import conv_csharp


class Test_conv_vb6:
    @staticmethod
    def test_get_args_str():
        # Arrange
        target_elem = CodeElement(
            "TestFunction",
            CodeElementType.FUNC,
            accessibility=CodeElementAccessibility.PUBLIC,
        )
        target_elem.arguments.append(CodeElementArgument("TestArg1", "TestClass"))
        target_elem.arguments.append(CodeElementArgument("TestArg2", "TestClass"))
        target_elem.arguments.append(CodeElementArgument("TestArg3", "TestClass"))
        csharp_generator = conv_csharp.CsharpGenerator()

        # Act
        actual = csharp_generator._get_args_str(target_elem)

        # Assert
        assert actual == "TestClass TestArg1, TestClass TestArg2, TestClass TestArg3"
