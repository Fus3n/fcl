from .pparser import *

class Interpreter:

    def __init__(self, ast: Program):
        self.variables = {}
        self.ast = ast

    def run(self):
        last_return = None
        for stat in self.ast.statements:
            last_return = self.evaluate(stat)

        return last_return

    def eprint(self, msg: str):
        print(msg)
        exit(1)

    def arg_error(self, func_name, arg_len, expected_len, tok, exact=True):
        if exact:
            if arg_len != expected_len:
                self.eprint(f"'{func_name}' function takes exactly {expected_len} arguments, {arg_len} were given.\n{tok}")
        else:
            if arg_len < expected_len:
                self.eprint(f"'{func_name}' function takes atleast {expected_len} arguments, {arg_len} were given.\n{tok}")

    def evaluate(self, node):
        if isinstance(node, Program):
            for statement in node.statements:
                self.evaluate(statement)
        elif isinstance(node, BlockNode):
            last_expr = NoneNode(node.tok)
            for expr in node.statements:
                last_expr = self.evaluate(expr)
            return last_expr
        elif isinstance(node, StringNode):
            return node.value
        elif isinstance(node, NumberNode):
            if "." in node.value:
                return float(node.value)
            else:
                return int(node.value)
        elif isinstance(node, ListNode):
            return node.values
        elif isinstance(node, AssignmentNode):
            v_val = self.evaluate(node.expr)
            self.variables[node.var_name] = v_val
            return v_val
        elif isinstance(node, BoolNode):
            return node
        elif isinstance(node, VarAccessNode):
            var_name = node.var_name
            value = self.variables.get(var_name)
            if value:
                return self.evaluate(value) if isinstance(value, Node) else value
            else:
                self.eprint(f"Variable '{var_name}' does not exists: {node.tok}")
        elif isinstance(node, FunctionCallNode):
            func_name = node.func_name

            # TODO: Fix clutterness and add more functions
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
                self.arg_error(func_name, len(node.args), 2, node.tok)
                return ElifNode(node.args[0], node.args[1], node.tok)

            # evaluate args for normal functions
            args = [self.evaluate(arg) if isinstance(arg, Node) else arg for arg in node.args]
            # normal functions
            if func_name == "log":
                values = [str(value) for value in args]
                print(" ".join(values))
                return NoneNode(node.tok)
            elif func_name in ("add", "sub", "mul", "div", "pow", "mod"):
                return self.run_arithmetic_op(func_name, args, node)
            elif func_name == "str":
                self.arg_error(func_name, len(args), 1, node.tok)
                return str(args[0])
            elif func_name == "index":
                # index lists and str
                self.arg_error(func_name, len(args), 2, node.tok)

                if not isinstance(args[0], (list, str)):
                    self.eprint(f"'index' function only accepts string or list as it's first argument.\n{node.tok}")
                
                if not isinstance(args[1], int):
                    self.eprint(f"'index' function only accepts integer as it's first argument.\n{node.tok}")

                indx = args[1]
                if indx > len(args[0]):
                    self.eprint(f"index out of bounds.\n{node.tok}")

                value = args[0][indx]
                return self.evaluate(value) if isinstance(value, Node) else value

            elif func_name == "len":
                self.arg_error(func_name, len(args), 1, node.tok)
                if not isinstance(args[0], (str, list)):
                    self.eprint(f"'len' function only takes string or list as it's first argument.\n{node.tok}")
                return len(args[0])
            elif func_name == "input":
                self.arg_error(func_name, len(args), 1, node.tok)

                if not isinstance(args[0], str):
                    self.eprint(f"'input' function takes string as an argument\n{node.tok}")

                ret_val = input(args[0])
                return StringNode(ret_val, node.tok)
            elif func_name in ("eq", "neq", "gt", "gte", "lt", "lte"):
                return self.run_conditionals(func_name, args, node)
            elif func_name in ("and", "or"):
                self.arg_error(func_name, len(node.args), 2, node.tok)
                arg1 = args[0]
                arg2 = args[1]
                if isinstance(arg1, BoolNode):
                    arg1 = arg1.is_true()
                if isinstance(arg2, BoolNode):
                    arg2 = arg2.is_true()

                if func_name == "and":
                    res = arg1 and arg2
                else:
                    res = arg1 or arg2
                return BoolNode("true" if res else "false", node.tok)
            else:
                self.eprint(f"function '{func_name}' does not exist at {node.tok}")
        else:
            self.eprint(f"Node not implimented {type(node)}:{node.tok}")

    def run_if(self, args: list[Node], clause):
        self.arg_error("if", len(args), 2, clause.tok, exact=False)

        condition = self.evaluate(args[0])
        then_expr = args[1]

        args = args[2:]

        # typical one conditon one expr if-statement
        if condition.is_true():
            return self.evaluate(then_expr)
        
        args = [self.evaluate(expr) if isinstance(expr, FunctionCallNode) and expr.func_name == "elif" else expr for expr in args]
        
        from pprint import pprint
        
        for clause in args:
            if isinstance(clause, ElifNode):
                cond = self.evaluate(clause.cond)
                if isinstance(cond, BoolNode):
                    if cond.is_true():
                        return self.evaluate(clause.expr)
                elif cond:
                    return self.evaluate(clause.expr)
            elif clause == args[-1]:
                return self.evaluate(clause)
            else:
                self.eprint(f"Invalid Syntax in {clause.tok}")

    def run_for(self, args: list, node: FunctionCallNode):
        self.arg_error("for", len(args), 3, node.tok, exact=False)

        if not isinstance(args[0], VarAccessNode):
            self.eprint(f"'for' function takes an identifier as it's first argument, {node.tok}")

        start_range = self.evaluate(args[1]) if isinstance(args[1], Node) else args[1]
        end_range = self.evaluate(args[2]) if isinstance(args[2], Node) else args[2]

        if not isinstance(start_range, int):
            self.eprint(f"'for' function takes an integer as it's second argument, {node.tok}")
        
        if not isinstance(end_range, int):
            self.eprint(f"'for' function takes an integer as it's third argument, {node.tok}")

        identifier = args[0].var_name
        expressions = args[3:]
        
        for i in range(start_range, end_range):
            self.variables[identifier] = NumberNode(str(i), node.tok)
            for expression in expressions:
                self.evaluate(expression) 

        del self.variables[identifier]

    def run_var(self, args: list[Node], node):
        self.arg_error("var", len(args), 2, node.tok)

        v_name = args[0]
        v_value = args[1]

        if not isinstance(v_name, VarAccessNode):
            self.eprint(f"'var' function an 'identifier' as it's first argument.\n{node.tok}")

        self.variables[v_name.var_name] = v_value
        return v_value
    
    def run_arithmetic_op(self, func_name, args: list[Node], node):
        self.arg_error(func_name, len(args), 2, node.tok)
        
        args = [self.evaluate(arg) if isinstance(arg, Node) else arg for arg in args]
        val1 = args[0]
        val2 = args[1]

        arith_ops = {
            "add": lambda a, b: a + b,
            "sub": lambda a, b: a - b,
            "mul": lambda a, b: a * b,
            "div": lambda a, b: a / b,
            "mod": lambda a, b: a % b,
            "pow": pow
        }

        if func_name == "add":
            if isinstance(val1, str) and isinstance(val2, str):
                new_val = val1 + val2
                return new_val
            
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            if func_name == "div" and str(val2) == "0":
                self.eprint(f"cannot divide by zero at '{node.tok}'")
            new_val = arith_ops[func_name](val1, val2)
            return new_val
        else:
            self.eprint(f"'{func_name}' function cannot work with types '{type(args[0])}' and '{type(args[1])}', {node.tok}")

    def run_conditionals(self, func_name, args, node):
        self.arg_error(func_name, len(args), 2, node.tok)

        cond_dict = {
            "gt": lambda x, y: x > y,
            "gte": lambda x, y: x >= y,
            "lt": lambda x, y: x < y,
            "lte": lambda x, y: x <= y,
        }

        if func_name == "eq":
            return BoolNode("true" if args[0] == args[1] else "false", node.tok)
        elif func_name == "neq":
            return BoolNode("true" if args[0] != args[1] else "false", node.tok)
        elif isinstance(args[0], int) and isinstance(args[1], int):
            res = cond_dict[func_name](args[0], args[1])
            return BoolNode("true" if res else "false", node.tok)
        else:
            self.eprint(f"functions 'gt', 'gte', 'lt', 'lte' only supports numbers, {node.tok}")
        


