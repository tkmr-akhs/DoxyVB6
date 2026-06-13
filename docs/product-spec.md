# DoxyVB6 Product Spec

## VB Property Conversion

DoxyVB6 converts VB6 / VBA property procedures into C#-style declarations for Doxygen input.

The same conversion rules apply to normal class modules and to class modules treated as interfaces by the `'# Interface` marker.

### Supported Shapes

Normal non-indexed properties keep the existing property-shaped output.

Default indexed properties are supported. A contiguous Property Get, Property Let, or Property Set group is treated as a default indexed property when any accessor in the group contains a matching `Attribute <PropertyName>.VB_UserMemId = 0` marker and the property has index arguments. The generated C#-style member is an indexer. If an accessor group contains a `VB_UserMemId` marker for a different member name, parsing fails.

Non-default indexed properties are supported as method-shaped members. A getter is emitted as a return-value method. A setter is emitted as a `void` method that includes the assigned value argument.

Non-indexed default members are not supported as default-member semantics. If a property has `VB_UserMemId = 0` but no index arguments, DoxyVB6 keeps the existing normal property-shaped output and does not attempt to represent the VB default-call behavior.

Optional index arguments and their default values are preserved in generated declarations when Doxygen accepts the resulting C#-style declaration.

### Accessor Grouping

Property accessor groups must be contiguous. If a later accessor for the same property appears after another member, parsing fails.

The first accessor comment is the only accepted member comment for a grouped property. Later accessors in the same contiguous group must not have their own member comments.

Property Get, Property Let, and Property Set accessors in the same group must have the same index signature. Setter value arguments are not part of the index signature. If a getter exists, the generated property type comes from the getter return type. If both Let and Set exist with different value argument types, that difference is allowed only when a getter exists.

### Generated Doxygen Notes

Default indexed properties generate this note:

```csharp
/// @note Converted from the VB default indexed property <Name>.
```

Non-default indexed property getters generate this note:

```csharp
/// @note Converted from a VB indexed property getter.
```

Non-default indexed property setters generate this note:

```csharp
/// @note Converted from a VB indexed property setter.
```

Generated notes are emitted even when the original accessor has no member comment, so the converted indexed property remains visible when Doxygen extraction depends on documentation comments.

### Parse Failures

Parsing fails when grouped property accessors cannot be represented without ambiguity. This includes mismatched index signatures between accessors, mismatched Let and Set index signatures, and setter-only Let and Set pairs where no getter exists to provide the representative property type.

Parsing also fails for non-contiguous accessors of the same property, later accessor member comments, and mismatched `VB_UserMemId` attribute member names inside a property accessor group.

### Acceptance Coverage

Acceptance tests should cover default indexed properties, non-default indexed getters, non-default indexed getter and setter pairs, default indexed Get / Let / Set groups with Variant and Object setter value types, non-indexed default members, interface class modules, later accessor comments, non-contiguous accessors, and index signature mismatches.
