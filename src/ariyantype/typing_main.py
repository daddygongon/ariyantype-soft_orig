import sys
from .typing_app import TypingApp

def main():
    TypingApp().run(sys.argv[1:])

if __name__ == "__main__":
    main()
