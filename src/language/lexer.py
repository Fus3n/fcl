from enum import Enum, auto
import sys

class Type(Enum):
    String = auto()
    Number = auto()
    Bool = auto()
    Identifier = auto()
    LeftParen = auto()
    RightParen = auto()
    LeftSquareBracket = auto()
    RightSquareBracket = auto()
    Equal = auto()
    Comma = auto()
    Void = auto()
    Eof = auto()

class Loc:
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.row = 0
        self.line = 1

    def __repr__(self) -> str:
        return f"{self.file_path}:{self.line}:{self.row}"
    
    def forward(self, char: str):
        if char == "\n":
            self.line += 1
            self.row = 0
        else:
            self.row += 1

    def copy(self):
        loc = Loc(self.file_path)
        loc.row = self.row
        loc.line = self.line
        return loc

class Token:

    def __init__(self, tt: Type, value: str, stat_loc: Loc, end_loc: Loc = None):
        self.value = value
        self.tt = tt
        self.start_loc = stat_loc
        if end_loc is None:
            self.end_loc = self.start_loc
        else:
            self.end_loc = end_loc

    def __repr__(self) -> str:
        return f"{self.start_loc.file_path}:{self.start_loc.line}:{self.start_loc.row}"

    def __str__(self) -> str:
        return self.__repr__()
    
    def match(self, tt: Type, value: str = None):
        if value is not None:
            return self.tt == tt and self.value == value
        else:
            return self.tt == tt


class Lexer:
    
    def __init__(self, code: str, file_path: str):
        self.code = code

        self.loc = Loc(file_path)
        self.tokens = []
        self.char: str = None # current char
        self.char_indx = 0

        # consume first character
        self.advance()

    def advance(self) -> None:
        if self.char_indx < len(self.code):
            self.char = self.code[self.char_indx]
        else:
            self.char = None
        
        self.loc.forward(self.char)
        self.char_indx += 1

    def valid(self) -> bool:
        """Check if current character is not none"""
        return self.char is not None

    def iss(self, value: str) -> bool:
        return self.char == value
    
    def is_not(self, value: str) -> bool:
        return self.char != value

    def peek(self, idx: int) -> str | None:
        if idx < len(self.code):
            return self.code[idx]
        return None

    def append(self, value) -> None:
        self.tokens.append(value)

    def tokenize(self) -> None:
        while self.valid():
            if self.char.isspace():
                self.advance()
            elif self.iss("="):
                self.append(Token(Type.Equal, self.char, self.loc.copy()))
                self.advance()
            elif self.iss("#"):
                self.advance()
                while self.valid() and self.is_not("\n"):
                    self.advance()
                self.advance()
            elif self.iss("("):
                self.append(Token(Type.LeftParen, self.char, self.loc.copy()))
                self.advance()
            elif self.iss(")"):
                self.append(Token(Type.RightParen, self.char, self.loc.copy()))
                self.advance()
            elif self.iss("["):
                self.append(Token(Type.LeftSquareBracket, self.char, self.loc.copy()))
                self.advance()
            elif self.iss("]"):
                self.append(Token(Type.RightSquareBracket, self.char, self.loc.copy()))
                self.advance()
            elif self.iss(","):
                self.append(Token(Type.Comma, self.char, self.loc.copy()))
                self.advance()
            elif self.iss("'") or self.iss("\""):
                self.parse_string()
            elif self.char.isdecimal():
                self.parse_number()
            elif self.char.isalpha():
                self.parse_identifier()
            else:
                print(f"Invalid Syntax: {self.loc}")
                exit(1)

        self.tokens.append(Token(Type.Eof, "EOF", self.loc))

    def parse_string(self):
        quote = self.char
        start_loc = self.loc.copy()

        self.advance()
        parsed = ""
        
        while self.valid() and self.is_not(quote):
            parsed += self.char
            self.advance()
        
        if self.is_not(quote):
            print(f"Invalid Syntax, Expected \"'\" or \"'\", at line {start_loc.line}")
            sys.exit(1)
        self.advance()

        self.append(Token(Type.String, parsed, start_loc, self.loc.copy()))

    def parse_number(self):
        parsed = ""
        start_loc = self.loc.copy()

        while self.valid() and (self.char.isdecimal() or self.iss(".")):
            parsed += self.char
            self.advance()

        self.append(Token(Type.Number, parsed, start_loc, self.loc.copy()))

    def parse_identifier(self):
        start_loc = self.loc.copy()
        parsed = self.char
        self.advance()

        while self.valid() and (self.char.isalpha() or self.char.isdecimal() or self.iss("_")):
            parsed += self.char
            self.advance()
        
        if parsed == "true" or parsed == "false":
            self.append(Token(Type.Bool, parsed, start_loc, self.loc.copy()))
        else:
            self.append(Token(Type.Identifier, parsed, start_loc, self.loc.copy()))
