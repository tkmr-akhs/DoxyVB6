import pytest
import pytest_mock
import pytest_raises

from DoxyVB6.codeconv import CodeElement, CodeElementType, CodeElementAccessibility
from DoxyVB6 import conv_vb6


class Test_conv_vb6:
    @staticmethod
    def test_parse_args():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)

        # Act
        actual = vb6_parser._build_args_list("()")

        # Assert
        assert len(actual) == 0

    @staticmethod
    def test_parse_args2():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)

        # Act
        actual = vb6_parser._build_args_list("a")

        # Assert
        assert len(actual) == 1
        assert actual[0].name == "a"

    @staticmethod
    def test_parse_args3():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(".cls")

        # Act
        actual = vb6_parser._build_args_list(
            'a, optional byref b as Integer = 123,optional byval c as String = "12""3" , paramarray d()'
        )

        # Assert
        assert len(actual) == 4
        assert actual[0].name == "a"
        assert actual[0].type == "Variant"
        assert actual[0].default_value == "default"
        assert actual[0].is_reference is True
        assert actual[0].is_str is False
        assert actual[0].is_vlargs is False

        assert actual[1].name == "b"
        assert actual[1].type == "Integer"
        assert actual[1].default_value == "123"
        assert actual[1].is_reference is True
        assert actual[1].is_str is False
        assert actual[1].is_vlargs is False

        assert actual[2].name == "c"
        assert actual[2].type == "String"
        assert actual[2].default_value == '12"3'
        assert actual[2].is_str is True
        assert actual[2].is_reference is False
        assert actual[2].is_vlargs is False

        assert actual[3].name == "d"
        assert actual[3].type == "Variant[]"
        assert actual[3].is_vlargs is True

    @staticmethod
    def test_parse_args4():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.CLASS)

        # Act
        actual = vb6_parser._build_args_list("NewValue() As TestClass")

        # Assert
        assert len(actual) == 1
        assert actual[0].name == "NewValue"
        assert actual[0].type == "TestClass[]"
        assert actual[0].default_value == "default"
        assert actual[0].is_reference is True
        assert actual[0].is_str is False
        assert actual[0].is_vlargs is False

    @staticmethod
    def test_found_member():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._found_member("", target_elem)

        # Assert
        assert actual is False
        assert len(target_elem.childs) == 0

    @staticmethod
    def test_found_member2():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._found_member("' test", target_elem)

        # Assert
        assert actual is False
        assert len(target_elem.childs) == 0

    @staticmethod
    def test_found_member3():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._found_member("'* Test Comment", target_elem)

        # Assert
        assert actual is False
        assert len(target_elem.childs) == 0

    @staticmethod
    def test_found_member4():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._found_member("Public Test", target_elem)

        # Assert
        assert actual is True
        assert len(target_elem.childs) == 1
        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.VAR
        assert target_elem.childs[0].return_type == "Variant"
        assert target_elem.childs[0].is_static is False
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PUBLIC
        assert target_elem.childs[0].value == ""
        assert target_elem.childs[0].is_str is False

    @staticmethod
    def test_found_member5():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._found_member("Const Test", target_elem)

        # Assert
        assert actual is True
        assert len(target_elem.childs) == 1
        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.CONST
        assert target_elem.childs[0].return_type == "Variant"
        assert target_elem.childs[0].is_static is False
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PRIVATE
        assert target_elem.childs[0].value == ""
        assert target_elem.childs[0].is_str is False

    @staticmethod
    def test_found_member6():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._found_member(
            'Friend Const Test() As String = "Test "" String" \'comment', target_elem
        )

        # Assert
        assert actual is True
        assert len(target_elem.childs) == 1
        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.CONST
        assert target_elem.childs[0].return_type == "String[]"
        assert target_elem.childs[0].is_static is False
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.INTERNAL
        assert target_elem.childs[0].value == 'Test " String'
        assert target_elem.childs[0].is_str is True

    @staticmethod
    def test_find_function():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._find_function(
            'Friend Const Test() As String = "Test "" String" \'comment', target_elem
        )

        # Assert
        assert actual[0] is False
        assert actual[1] == target_elem
        assert len(target_elem.childs) == 0

    @staticmethod
    def test_find_function2():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._find_function("Function Test()", target_elem)

        # Assert
        assert actual[0] is True
        assert actual[1] != target_elem
        assert len(target_elem.childs) == 1
        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.FUNC
        assert target_elem.childs[0].return_type == "Variant"
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PUBLIC

    @staticmethod
    def test_find_function3():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._find_function(
            'Private Function Test(Optional ByVal Arg1 As String ="Test "" String") As TestClass() \' comment',
            target_elem,
        )

        # Assert
        assert actual[0] is True
        assert actual[1] != target_elem
        assert len(target_elem.childs) == 1

        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.FUNC
        assert target_elem.childs[0].return_type == "TestClass[]"
        assert target_elem.childs[0].is_static is False
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PRIVATE

        assert target_elem.childs[0].arguments[0].name == "Arg1"
        assert target_elem.childs[0].arguments[0].default_value == 'Test " String'
        assert target_elem.childs[0].arguments[0].is_str is True

    @staticmethod
    def test_find_function4():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._find_function(
            'Function ConvertBooleanToString(         ByVal BooleanValue As String,         Optional ByVal FlagOnString As String = "■",         Optional ByVal FlagOffString As String = "") As String',
            target_elem,
        )

        # Assert
        assert actual[0] is True
        assert actual[1] != target_elem
        assert len(target_elem.childs) == 1

        assert len(actual[1].arguments) == 3
        assert actual[1].arguments[0].is_optional is False
        assert actual[1].arguments[0].is_str is False
        assert actual[1].arguments[1].default_value == "■"
        assert actual[1].arguments[1].is_optional is True
        assert actual[1].arguments[1].is_str is True
        assert actual[1].arguments[2].default_value == ""
        assert actual[1].arguments[2].is_optional is True
        assert actual[1].arguments[2].is_str is True

    @staticmethod
    def test_find_sub3():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._find_sub(
            'Private Sub Test(Optional ByVal Arg1 As String ="Test "" String") \' comment',
            target_elem,
        )

        # Assert
        assert actual[0] is True
        assert actual[1] != target_elem
        assert len(target_elem.childs) == 1

        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.FUNC
        assert target_elem.childs[0].return_type == "void"
        assert target_elem.childs[0].is_static is False
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PRIVATE

        assert target_elem.childs[0].arguments[0].name == "Arg1"
        assert target_elem.childs[0].arguments[0].default_value == 'Test " String'
        assert target_elem.childs[0].arguments[0].is_str is True

    @staticmethod
    def test_find_type3():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._find_type(
            "Private Type Test ' comment",
            target_elem,
        )

        # Assert
        assert actual[0] is True
        assert actual[1] != target_elem
        assert len(target_elem.childs) == 1

        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.STRUCT
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PRIVATE

    @staticmethod
    def test_find_enum3():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._find_enum(
            "Private Enum Test ' comment",
            target_elem,
        )

        # Assert
        assert actual[0] is True
        assert actual[1] != target_elem
        assert len(target_elem.childs) == 1

        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.ENUM
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PRIVATE

    @staticmethod
    def test_find_property_get3():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._find_property_get(
            "Private Property Get Test() As TestClass() ' comment", target_elem, None
        )

        # Assert
        assert actual[0] is True
        assert actual[1] != target_elem
        assert len(target_elem.childs) == 1

        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.PROPERTY
        assert target_elem.childs[0].return_type == "TestClass[]"
        assert target_elem.childs[0].is_static is False
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PRIVATE

        assert len(target_elem.childs[0].arguments) == 0

    @staticmethod
    def test_find_property_set3():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._find_property_set(
            "Private Property Set Test(NewValue() As TestClass) ' comment",
            target_elem,
            None,
        )

        # Assert
        assert actual[0] is True
        assert actual[1] != target_elem
        assert len(target_elem.childs) == 1

        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.PROPERTY
        assert target_elem.childs[0].return_type == "void"
        assert target_elem.childs[0].is_static is False
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PRIVATE

        assert target_elem.childs[0].arguments[0].name == "NewValue"
        assert target_elem.childs[0].arguments[0].type == "TestClass[]"
        assert target_elem.childs[0].arguments[0].is_str is False

    @staticmethod
    def test_find_property():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)
        _, _, prop_get = vb6_parser._find_property_get(
            "Private Property Get Test() As TestClass() ' comment", target_elem, None
        )

        # Act
        actual = vb6_parser._find_property_set(
            "Private Property Set Test(NewValue() As TestClass) ' comment",
            target_elem,
            prop_get,
        )

        # Assert
        assert actual[0] is True
        assert actual[1] != target_elem
        assert len(target_elem.childs) == 1

        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.PROPERTY
        assert target_elem.childs[0].return_type == "TestClass[]"
        assert target_elem.childs[0].is_static is False
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PRIVATE

        assert target_elem.childs[0].arguments[0].name == "NewValue"
        assert target_elem.childs[0].arguments[0].type == "TestClass[]"
        assert target_elem.childs[0].arguments[0].is_str is False

    @staticmethod
    def test_find_property2():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)
        _, _, prop_set = vb6_parser._find_property_set(
            "Private Property Set Test(NewValue() As TestClass) ' comment",
            target_elem,
            None,
        )

        # Act
        actual = vb6_parser._find_property_get(
            "Private Property Get Test() As TestClass() ' comment",
            target_elem,
            prop_set,
        )

        # Assert
        assert actual[0] is True
        assert actual[1] != target_elem
        assert len(target_elem.childs) == 1

        assert target_elem.childs[0].name == "Test"
        assert target_elem.childs[0].elem_type == CodeElementType.PROPERTY
        assert target_elem.childs[0].return_type == "TestClass[]"
        assert target_elem.childs[0].is_static is False
        assert target_elem.childs[0].accessibility == CodeElementAccessibility.PRIVATE

        assert target_elem.childs[0].arguments[0].name == "NewValue"
        assert target_elem.childs[0].arguments[0].type == "TestClass[]"
        assert target_elem.childs[0].arguments[0].is_str is False

    @staticmethod
    def test_process_enum():
        # Arrange
        vb6_parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.STANDARD)
        target_elem = CodeElement("", CodeElementType.CLASS)

        # Act
        actual = vb6_parser._process_enum(
            "Test ' comment",
            target_elem,
        )

        # Assert
        assert actual[0] is True
        assert actual[1] == target_elem
        assert len(target_elem.childs) == 1
