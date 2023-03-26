from language import *
import sys
import time

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("Usage: python main.py <filename>")
        exit(1)
    
    file_name = args[0]
    code = open(file_name, "r").read()

    start = time.perf_counter()
    lexer = Lexer(code, file_name)
    lexer.tokenize()
    parser = Parser(lexer)
    ast = parser.parse()
    interp = Interpreter(ast)
    _ = interp.run()
    end = time.perf_counter() - start
    # print()
    # print(end, "time")
    # print(last_expression)

if __name__ == '__main__':
    main()