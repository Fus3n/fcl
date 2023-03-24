from pparser import *

class Interpreter:

    def __init__(self, ast: Program):
        self.variables = {}
        self.ast = ast

    def run(self):
        last_return = None
        for stat in self.ast.statements:
            last_return = self.evaluate(stat)

        return last_return

    def evaluate(self, node):
        if isinstance(node, Program):
            for statement in node.statements:
                self.evaluate(statement)
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, NumberNode):
            if "." in node.value:
                return float(node.value)
            else:
                return int(node.value)
        elif isinstance(node, AssignmentNode):
            self.variables[node.var_name] = self.evaluate(node.expr)
            return self.variables[node.var_name]
        elif isinstance(node, BoolNode):
            return node
        elif isinstance(node, VarAccessNode):
            var_name = node.var_name
            if value := self.variables.get(var_name):
                return self.evaluate(value)
            else:
                print(f"Variable '{var_name}' does not exists: {node.tok}")
                exit(1)
        elif isinstance(node, FunctionCallNode):
            func_name = node.func_name

            # syntax level functions
            if func_name == "for":
                # syntax for(var name: Identifier, till: integer, *expressions)
                return self.run_for(node.args, node)
            elif func_name == "var":
                # syntax var(name: Identifier, value: any)
                return self.run_var(node.args, node)
            elif func_name == "if":
                return self.run_if(node.args, node)
            elif func_name == "elif":
                if len(node.args) != 2:
                    print(f"'elif' functions takes exactly 2 arguments, {len(args)} where give.\n{node.tok}")
                    exit(1)
                return ElifNode(node.args[0], node.args[1], node.tok)

            # evaluate args for normal functions
            args = [self.evaluate(arg) for arg in node.args]
            # normal functions
            if func_name == "log":
                values = [str(value) for value in args]
                print(" ".join(values))
                return NoneNode(node.tok)
            elif func_name in ["add", "sub", "mul", "div", "pow"]:
                return self.run_arithmetic_op(func_name, args, node)
            elif func_name == "str":
                if len(args) != 1:
                    print(f"'str' function takes 1 argument, {len(args)} were given.\n{node.tok}")
                    exit(1)
                return str(args[0].value)
            elif func_name == "input":
                if len(args) != 1:
                    print(f"'input' function takes 1 arguments, {len(args)} were given.\n{node.tok}")
                    exit(1)
                if not isinstance(args[0], str):
                    print(f"'input' function takes string as an argument\n{node.tok}")
                    exit(1)

                ret_val = input(args[0])
                return StringNode(ret_val, node.tok)
            elif func_name == "cmp":
                if len(args) != 2:
                    print(f"'cmp' function takes 2 arguments, {len(args)} were given.\n{node.tok}")
                
                if args[0] == args[1]:
                    return BoolNode("true", node.tok)
                else:
                    return BoolNode("false", node.tok)

            else:
                print(f"function '{func_name}' does not exist at {node.tok}")
                exit(1)
        elif isinstance(node, BlockNode):
            last_expr = NoneNode(node.tok)
            for expr in node.statements:
                last_expr = self.evaluate(expr)
            return last_expr
        else:
            print(f"Node not implimented {type(node)}")
            exit(1)

    def run_if(self, args: list[Node], node):
        if len(args) < 2:
            print(f"'if' funciton takes more than 2 arguments, {len(args)} were given.\n{node.tok}")
            exit(1)

        condition = args[0]
        then_expr = args[1]

        args = args[2:]

        # typical one conditon one expr if-statement
        if len(args) == 0 and condition.is_true():
            return self.evaluate(then_expr)
        
        args = [self.evaluate(expr) if isinstance(expr, FunctionCallNode) and expr.func_name == "elif" else expr for expr in args ]
        
        for expr in args:
            if isinstance(expr, ElifNode):
                if expr.cond.is_true():
                    return self.evaluate(expr.expr)
            elif expr == args[-1]:
                return self.evaluate(expr)
            else:
                print(f"Invalid Syntax in {expr.tok}")
                exit(1)

    def run_for(self, args: list, node: FunctionCallNode):
        if len(args) < 2:
            print(f"'for' function takes alteast two arguments, {len(args)} where given.\n{node.tok}")
            exit(1)

        if not isinstance(args[0], VarAccessNode):
            print(f"'for' function takes an identifier as it's first argument, {node.tok}")
            exit(1)

        if not isinstance(args[1], NumberNode):
            print(f"'for' function takes an integer as it's second argument, {node.tok}")
            exit(1)
        else:
            if "." in args[1].value:
                print(f"'for' function takes an integer as it's second argument, {node.tok}")
                exit(1)


        identifier = args[0].var_name
        rangee = int(args[1].value)

        expressions = args[2:]

        for i in range(rangee):
            self.variables[identifier] = NumberNode(str(i), node.tok)
            for expression in expressions:
                self.evaluate(expression) 

        del self.variables[identifier]

    def run_var(self, args: list[Node], node):
        if len(args) != 2:
            print(f"'var' function takes 2 arguments, {len(args)} were given.\n{node.tok}")
            exit(1)

        v_name = args[0]
        v_value = args[1]

        if not isinstance(v_name, VarAccessNode):
            print(f"'var' function an 'identifier' as it's first argument.\n{node.tok}")
            exit(1)

        self.variables[v_name.var_name] = v_value
        return v_value
    
    def run_arithmetic_op(self, func_name, args: list[Node], node):
        if len(args) > 2:
            print(f"Function 'add' expects 2 arguments, {len(args)} were given.\n{node.tok}")
            exit(1)
        
        val1 = args[0]
        val2 = args[1]

        arith_ops = {
            "add": lambda a, b: a + b,
            "sub": lambda a, b: a - b,
            "mul": lambda a, b: a * b,
            "div": lambda a, b: a / b,
            "pow": pow
        }

        if func_name == "add":
            if isinstance(val1, str) and isinstance(val2, str):
                new_val = val1 + val2
                return new_val
            
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            if func_name == "div" and str(val2) == "0":
                print(f"cannot divide by zero at '{node.tok}'")
                exit(1)
            new_val = arith_ops[func_name](val1, val2)
            return new_val
        else:
            print(f"'add' function cannot add '{type(args[0])}' and '{type(args[1])}', {node.tok}")
            exit(1)


        
