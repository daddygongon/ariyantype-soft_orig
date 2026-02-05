import sys
from .typing_app import TypingApp


class TypingMain:
    def main(self, argv: list[str] | None = None) -> int:
        if argv is None:
            argv = sys.argv[1:]
        TypingApp().app(argv)
        return 0


def main() -> None:
    sys.exit(TypingMain().main())


if __name__ == "__main__":
    main()
