from lexer import Lexer
from pparser import Parser
from interpreter import Interpreter


def main():
    code = open("./file.txt", "r").read()

    lexer = Lexer(code, "./file.txt")
    lexer.tokenize()
    parser = Parser(lexer)
    ast = parser.parse()
    interp = Interpreter(ast)
    _ = interp.run()
    # print(ast)
    # print(_)

if __name__ == '__main__':
    main()