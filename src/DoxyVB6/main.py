"""Module of main"""

import os
import sys

from .codeconv import AbstractCodeParser, AbstractCodeGenerator
from .conv_vb6 import Vb6Parser, Vb6ModuleType
from .conv_csharp import CsharpGenerator

# from .appinit import init_app
# from .bkup import BackupFacade
# from .cnf import CnfError, ConfigurationLoader, get_cli_cnf
# from .repoinit import BackupRepositoryFactory, MetadataRepositoryFactory

SRC_ENCODING = "cp932"


class Main:
    """Class for entry point"""

    def __init__(self, args: list[str]) -> None:
        """Initializer

        Args:
            args (list[str]): Commandline arguments

        Raises:
            cnf_error: Rise when there is a problem with the config.
        """
        self._srcfile = ""
        if len(args) == 2:
            self._cmdname = args[0]
            self._srcfile = args[1]

    def execute(self) -> int:
        """Main method.

        Returns:
            int: Exit code of command
        """
        if not self._srcfile:
            sys.stderr.write(f"usage: {self._cmdname} filename")
            return 1

        # try:
        _, ext = os.path.splitext(self._srcfile)
        ext_lower = ext.lower()
        if ext_lower == ".cls":
            module_type = Vb6ModuleType.CLASS
        elif ext_lower == ".frm":
            module_type = Vb6ModuleType.FORM
        else:
            module_type = Vb6ModuleType.STANDARD

        code_parser: AbstractCodeParser = Vb6Parser(module_type)
        code_generator: AbstractCodeGenerator = CsharpGenerator()
        try:
            with open(self._srcfile, "r", encoding=SRC_ENCODING) as f:
                src_code = f.readlines()
        except IOError as e:
            sys.stderr.write(f"Cannot open {self._srcfile}: {e}\n")
            return -1

        parse_result = code_parser.parse(src_code)
        # parse_result.root.print_structure()
        sys.stdout.write(os.linesep.join(code_generator.generate(parse_result)))
        sys.stdout.write(os.linesep)
        sys.stderr.write("OK\n")
        return 0
        # except BaseException as exc:
        #    sys.stderr.write(f"FINISH_WITH_ERROR: {type(exc)}, {exc.with_traceback}")
        #    return 1
