import sys
from .main import Main


if __name__ == "__main__":
    main_obj = Main(sys.argv)
    sys.exit(main_obj.execute())
