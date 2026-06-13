# VB Indexed Property Conversion

DoxyVB6 converts VB default indexed properties to C# indexers and converts non-default indexed properties to method-shaped members with Doxygen notes. The same rules apply to class modules and interface-marked class modules, while non-indexed default members remain normal properties. Property accessors are merged only when they are contiguous, later accessor comments are rejected, and invalid accessor signature combinations fail during parsing, because this keeps the generated Doxygen input close to the original VBA API without inventing ambiguous members.
