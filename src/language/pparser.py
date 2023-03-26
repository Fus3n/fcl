from .lexer import Lexer, Type, Token


class Node:
    def __init__(self, tok: Token) -> None:
        self.tok = tok

    def is_true(self) -> bool:
        return True

class Program(Node):
    def __init__(self, tok):
        super().__init__(tok)
        self.statements: list[Node] = []

    def __repr__(self):
        return f"Program<{hex(id(self))}>({self.statements})"

class BlockNode(Node):
    def __init__(self, statements, tok):
        super().__init__(tok)
        self.statements: list[Node] = statements

    def __repr__(self):
        return f"Block<{hex(id(self))}>({self.statements})"

class FunctionCallNode(Node):
    def __init__(self, func_name, args, tok: Token):
        super().__init__(tok)
        self.func_name = func_name
        self.args = args

    def __repr__(self):
        return f"FunctionCallNode<{hex(id(self))}>({self.func_name}, {self.args})"

class AssignmentNode(Node):
    def __init__(self, var_name, expr, tok: Token):
        super().__init__(tok)
        self.var_name = var_name
        self.expr = expr

    def __repr__(self):
        return f"AssignmentNode<{hex(id(self))}>({self.var_name}, {self.expr})"
    
class StringNode(Node):
    def __init__(self, value, tok: Token):
        super().__init__(tok)
        self.value = value

    def __repr__(self):
        return self.value
    
    def is_true(self) -> bool:
        return len(self.value) > 0

class NumberNode(Node):
    def __init__(self, value, tok: Token):
        super().__init__(tok)
        self.value = value

    def __repr__(self):
        return str(self.value)
    
    def is_true(self) -> bool:
        return self.value != 0
    
class ListNode(Node):
    def __init__(self, values: list[Node], tok: Token):
        super().__init__(tok)
        self.values = values

    def __repr__(self):
        return str(self.value)
    
    def is_true(self) -> bool:
        return len(self.value) != 0

class VarAccessNode(Node):
    def __init__(self, var_name, tok: Token):
        super().__init__(tok)
        self.var_name = var_name

    def __repr__(self):
        return f"VarAccessNode({self.var_name})"

class BoolNode(Node):
    def __init__(self, value, tok: Token):
        super().__init__(tok)
        self.value = value

    def __repr__(self):
        return self.value
    
    def is_true(self) -> bool:
        return (True if self.value == "true" else False)
    
class ElifNode(Node):
    def __init__(self, cond: Node, expr, tok: Token):
        super().__init__(tok)
        self.cond = cond
        self.expr = expr

    def __repr__(self):
        return f"ElifNode<{hex(id(self))}>({self.cond} ---- {self.expr})"
    
    def is_true(self) -> bool:
        return self.cond.is_true()
    
class NoneNode(Node):
    def __init__(self, tok: Token):
        super().__init__(tok)

    def __repr__(self):
        return "None"


class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tokens = lexer.tokens
        self.current_token = None
        self.token_index = 0

    def parse(self):
        self.current_token = self.tokens[self.token_index]
        ast = self.program()
        return ast

    def program(self):
        ast = Program(self.current_token)
        while self.current_token.tt != Type.Eof:
            if self.current_token.tt == Type.Identifier:
                if self.peek().tt == Type.Equal:
                    ast.statements.append(self.assignment_statement())
                elif self.peek().tt == Type.LeftParen:
                    ast.statements.append(self.function_call())
                else:
                    print(f"Invalid Syntax: {self.current_token}")
                    exit(1)
            elif self.current_token.tt == Type.LeftParen:
                ast.statements.append(self.block())
            else:
                print(f"Invalid Syntax: {self.current_token}")
                exit(1)
        return ast

    def assignment_statement(self):
        curr_tok = self.current_token
        var_name = self.current_token.value
        self.eat(Type.Identifier)
        self.eat(Type.Equal)
        expr = self.expr()
        return AssignmentNode(var_name, expr, curr_tok)

    def function_call(self):
        curr_tok = self.current_token
        func_name = self.current_token.value
        self.eat(Type.Identifier)
        self.eat(Type.LeftParen)
        args = []
        while self.current_token.tt != Type.RightParen:
            args.append(self.expr())
            if self.current_token.tt == Type.Comma:
                self.eat(Type.Comma)
            elif self.current_token.tt != Type.RightParen:
                print(f"Expected comma or ')' after each argument at {self.current_token}")
                exit(1)
        self.eat(Type.RightParen)
        return FunctionCallNode(func_name, args, curr_tok)
    
    def expr(self):
        curr_tok = self.current_token
        if self.current_token.tt == Type.String:
            value = self.current_token.value
            self.eat(Type.String)
            return StringNode(value, curr_tok)
        elif self.current_token.tt == Type.Number:
            value = self.current_token.value
            self.eat(Type.Number)
            return NumberNode(value, curr_tok)
        elif self.current_token.tt == Type.Bool:
            value = self.current_token.value
            self.eat(Type.Bool)
            return BoolNode(value, curr_tok)
        elif self.current_token.tt == Type.Identifier:
            if self.peek().tt == Type.LeftParen:
                return self.function_call()
            elif self.peek().tt == Type.Equal:
                return self.assignment_statement()
            var_name = self.current_token.value
            self.eat(Type.Identifier)
            return VarAccessNode(var_name, curr_tok)
        elif self.current_token.tt == Type.LeftParen:
            return self.block()
        elif self.current_token.tt == Type.LeftSquareBracket:
            return self.list_expr()
        else:
            print(f"Invalid Expression: {self.current_token}")
            exit(1)

    def block(self):
        curr_tok = self.current_token
        self.eat(Type.LeftParen)
        statements = []
        while self.current_token.tt != Type.RightParen:
            statements.append(self.expr())
            if self.current_token.tt == Type.Comma:
                self.eat(Type.Comma)

        self.eat(Type.RightParen)

        return BlockNode(statements, curr_tok)
    
    def list_expr(self):
        curr_tok = self.current_token
        self.eat(Type.LeftSquareBracket)
        items = []
        while self.current_token.tt != Type.RightSquareBracket:
            items.append(self.expr())
            if self.current_token.tt == Type.Comma:
                self.eat(Type.Comma)
            elif self.current_token.tt != Type.RightSquareBracket:
                print(f"Expected comma or ']' after list item at {self.current_token}")
                exit(1)
        self.eat(Type.RightSquareBracket)
        return ListNode(items, curr_tok)

    def eat(self, tt: Type):
        if self.current_token.tt == tt:
            self.token_index += 1
            if self.token_index < len(self.tokens):
                self.current_token = self.tokens[self.token_index]
            else:
                self.current_token = Token(Type.Eof, "EOF")
        else:
            print(f"Invalid Syntax: {self.current_token}, Expected: {tt}")
            exit(1)

    def peek(self):
        if self.token_index + 1 < len(self.tokens):
            return self.tokens[self.token_index + 1]
        else:
            return Token(Type.Eof, "EOF")
        

