import pytest

from DoxyVB6 import conv_csharp, conv_vb6
from DoxyVB6.codeconv import CannotParseException


def generate_class_module(code_lines: list[str]) -> list[str]:
    parser = conv_vb6.Vb6Parser(conv_vb6.Vb6ModuleType.CLASS)
    result = parser.parse(code_lines)

    return conv_csharp.CSharpGenerator().generate(result)


def test_default_indexed_property_generates_csharp_indexer():
    actual = generate_class_module(
        [
            'Attribute VB_Name = "ObjectList"\n',
            "'* Gets an item by index.\n",
            "Public Property Get Item(ByVal ItemIndex As Long) As Variant\n",
            "Attribute Item.VB_UserMemId = 0\n",
            "End Property\n",
        ]
    )

    assert "        /// Gets an item by index." in actual
    assert (
        "        /// @note Converted from the VB default indexed property Item."
        in actual
    )
    assert "        public Variant this[Long ItemIndex] { get; }" in actual


def test_non_default_indexed_getter_generates_method_shaped_member():
    actual = generate_class_module(
        [
            'Attribute VB_Name = "Cells"\n',
            "'* Gets a cell value.\n",
            "Public Property Get Cell(ByVal RowIndex As Long, ByVal ColumnIndex As Long) As Variant\n",
            "End Property\n",
        ]
    )

    assert "        /// Gets a cell value." in actual
    assert "        /// @note Converted from a VB indexed property getter." in actual
    assert "        public Variant Cell(Long RowIndex, Long ColumnIndex)" in actual


def test_non_default_indexed_getter_and_setter_generate_method_pair():
    actual = generate_class_module(
        [
            'Attribute VB_Name = "Cells"\n',
            "'* Accesses a cell value.\n",
            "Public Property Get Cell(ByVal RowIndex As Long, ByVal ColumnIndex As Long) As Variant\n",
            "End Property\n",
            "Public Property Let Cell(ByVal RowIndex As Long, ByVal ColumnIndex As Long, ByVal Value As Variant)\n",
            "End Property\n",
        ]
    )

    assert "        /// Accesses a cell value." in actual
    assert "        /// @note Converted from a VB indexed property getter." in actual
    assert "        public Variant Cell(Long RowIndex, Long ColumnIndex)" in actual
    assert "        /// @note Converted from a VB indexed property setter." in actual
    assert (
        "        public void Cell(Long RowIndex, Long ColumnIndex, Variant Value)"
        in actual
    )


def test_default_indexed_get_let_set_group_generates_get_set_indexer():
    actual = generate_class_module(
        [
            'Attribute VB_Name = "ArrayObject"\n',
            "'* Accesses an array item.\n",
            "Public Property Get Item(ByVal ItemIndex As Long) As Variant\n",
            "Attribute Item.VB_UserMemId = 0\n",
            "End Property\n",
            "Public Property Let Item(ByVal ItemIndex As Long, ByVal ItemObject As Variant)\n",
            "End Property\n",
            "Public Property Set Item(ByVal ItemIndex As Long, ByVal ItemObject As Object)\n",
            "End Property\n",
        ]
    )

    assert "        /// Accesses an array item." in actual
    assert (
        "        /// @note Converted from the VB default indexed property Item."
        in actual
    )
    assert "        public Variant this[Long ItemIndex] { get; set; }" in actual


def test_non_indexed_default_member_remains_normal_property():
    actual = generate_class_module(
        [
            'Attribute VB_Name = "ValueHolder"\n',
            "'* Gets the value.\n",
            "Public Property Get Value() As String\n",
            "Attribute Value.VB_UserMemId = 0\n",
            "End Property\n",
        ]
    )

    assert "        /// Gets the value." in actual
    assert "        public String Value { get; }" in actual
    assert not any("default indexed property" in line for line in actual)
    assert not any(" this[" in line for line in actual)


def test_interface_module_uses_default_indexed_property_conversion():
    actual = generate_class_module(
        [
            'Attribute VB_Name = "IArrayObject"\n',
            "'# Interface\n",
            "Public Property Get Item(ByVal ItemIndex As Long) As Variant\n",
            "Attribute Item.VB_UserMemId = 0\n",
            "End Property\n",
        ]
    )

    assert "    interface IArrayObject" in actual
    assert (
        "        /// @note Converted from the VB default indexed property Item."
        in actual
    )
    assert "        public Variant this[Long ItemIndex] { get; }" in actual


def test_default_indexed_property_preserves_optional_index_argument_default():
    actual = generate_class_module(
        [
            'Attribute VB_Name = "WorksheetRangeBounds"\n',
            "Public Property Get Item(ByVal ItemIndex As Long, Optional ByVal ColumnDirection As Boolean = False) As WorksheetRangeBounds\n",
            "Attribute Item.VB_UserMemId = 0\n",
            "End Property\n",
        ]
    )

    assert (
        "        public WorksheetRangeBounds this[Long ItemIndex, Boolean ColumnDirection = False] { get; }"
        in actual
    )


def test_later_accessor_member_comment_raises_parse_error():
    with pytest.raises(CannotParseException):
        generate_class_module(
            [
                'Attribute VB_Name = "ArrayObject"\n',
                "'* Gets an item.\n",
                "Public Property Get Item(ByVal ItemIndex As Long) As Variant\n",
                "Attribute Item.VB_UserMemId = 0\n",
                "End Property\n",
                "'* Sets an item.\n",
                "Public Property Let Item(ByVal ItemIndex As Long, ByVal ItemObject As Variant)\n",
                "End Property\n",
            ]
        )


def test_non_contiguous_property_accessor_raises_parse_error():
    with pytest.raises(CannotParseException):
        generate_class_module(
            [
                'Attribute VB_Name = "Probe"\n',
                "Public Property Get Value() As Long\n",
                "End Property\n",
                "Public Property Get Other() As Long\n",
                "End Property\n",
                "Public Property Let Value(ByVal NewValue As Long)\n",
                "End Property\n",
            ]
        )


def test_mismatched_index_signature_raises_parse_error():
    with pytest.raises(CannotParseException):
        generate_class_module(
            [
                'Attribute VB_Name = "ArrayObject"\n',
                "Public Property Get Item(ByVal ItemIndex As Long) As Variant\n",
                "Attribute Item.VB_UserMemId = 0\n",
                "End Property\n",
                "Public Property Let Item(ByVal ItemKey As String, ByVal ItemObject As Variant)\n",
                "End Property\n",
            ]
        )


def test_mismatched_user_mem_id_name_raises_parse_error():
    with pytest.raises(CannotParseException):
        generate_class_module(
            [
                'Attribute VB_Name = "ArrayObject"\n',
                "Public Property Get Item(ByVal ItemIndex As Long) As Variant\n",
                "Attribute Other.VB_UserMemId = 0\n",
                "End Property\n",
            ]
        )


def test_setter_only_let_set_pair_raises_parse_error():
    with pytest.raises(CannotParseException):
        generate_class_module(
            [
                'Attribute VB_Name = "ArrayObject"\n',
                "Public Property Let Item(ByVal ItemIndex As Long, ByVal ItemObject As Variant)\n",
                "End Property\n",
                "Public Property Set Item(ByVal ItemIndex As Long, ByVal ItemObject As Object)\n",
                "End Property\n",
            ]
        )


def test_non_default_indexed_setter_only_generates_method_shaped_member():
    actual = generate_class_module(
        [
            'Attribute VB_Name = "Cells"\n',
            "Public Property Let Cell(ByVal RowIndex As Long, ByVal ColumnIndex As Long, ByVal Value As Variant)\n",
            "End Property\n",
        ]
    )

    assert "        /// @note Converted from a VB indexed property setter." in actual
    assert (
        "        public void Cell(Long RowIndex, Long ColumnIndex, Variant Value)"
        in actual
    )
