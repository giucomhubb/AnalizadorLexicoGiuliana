# a01562646 Giuliana Herrera Lopez

import re
from dataclasses import dataclass
from typing import List, Any, Union


tokenTypes = [
    ('NUMBER',     r'\d+'),
    ('PLUS',       r'\+'),
    ('MINUS',      r'-'),
    ('LPAREN',     r'\('),
    ('RPAREN',     r'\)'),
    ('SLASH',      r'/'),
    ('STAR',       r'\*'),
    ('EQUALS',     r'='),
    ('IDENT',      r'[A-Za-z_]\w*'),
    ('WHITESPACE', r'\s+'),
]

compiledTokenTypes = [
    (name, re.compile(rf'^{pattern}'))
    for name, pattern in tokenTypes
]

@dataclass
class Token:
    type: str
    value: str

def tokenize(text: str) -> List[Token]:
    tokens: List[Token] = []
    pos = 0
    length = len(text)
    while pos < length:
        for name, regex in compiledTokenTypes:
            match = regex.match(text[pos:])
            if not match:
                continue
            lexeme = match.group(0)
            if name != 'WHITESPACE':
                tokens.append(Token(name, lexeme))
            pos += len(lexeme)
            break
        else:
            raise SyntaxError(f"Carácter inesperado '{text[pos]}' en la posición {pos}.")
    tokens.append(Token('EOF', ''))
    return tokens


@dataclass
class NumberNode:
    value: Union[int, float]

@dataclass
class BinaryOpNode:
    op: str         
    left: Any       
    right: Any       

@dataclass
class AssignNode:
    var_name: str   
    expr: Any       


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_token_index = 0

    def lookahead(self) -> Token:
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return Token('EOF', '')

    def consume(self, expected_type: str) -> Token:
        tok = self.lookahead()
        if tok.type != expected_type:
            raise SyntaxError(
                f"Token esperado '{expected_type}', pero '{tok.type}' "
                f"en la posición {self.current_token_index}."
            )
        self.current_token_index += 1
        return tok

    def parse_statement(self) -> Any:

        if self.lookahead().type == 'IDENT':
            var_token = self.consume('IDENT')
            if self.lookahead().type == 'EQUALS':
                self.consume('EQUALS')
                expr_node = self.parse_expression()
                return AssignNode(var_token.value, expr_node)
            else:
                self.current_token_index -= 1
        return self.parse_expression()

    def parse_expression(self) -> Any:
        node = self.parse_term()
        while self.lookahead().type in ('PLUS', 'MINUS'):
            op = self.consume(self.lookahead().type)
            right = self.parse_term()
            node = BinaryOpNode(op.value, node, right)
        return node

    def parse_term(self) -> Any:
        node = self.parse_factor()
        while True:
            tok = self.lookahead()
            if tok.type in ('STAR', 'SLASH'):
                op = self.consume(tok.type)
                right = self.parse_factor()
                node = BinaryOpNode(op.value, node, right)
            elif tok.type == 'LPAREN':
                right = self.parse_factor()
                node = BinaryOpNode('*', node, right)
            else:
                break
        return node

    def parse_factor(self) -> Any:
        tok = self.lookahead()
        if tok.type == 'NUMBER':
            self.consume('NUMBER')
            return NumberNode(int(tok.value))
        elif tok.type == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_expression()
            self.consume('RPAREN')
            return node
        else:
            raise SyntaxError(
                f"Token inesperado '{tok.type}' en la posición {self.current_token_index}."
            )

    def parse(self) -> Any:
        node = self.parse_statement()
        if self.lookahead().type != 'EOF':
            raise SyntaxError(
                f"Token inesperado '{self.lookahead().type}' al final de la entrada."
            )
        return node


def print_ast(node: Any, indent: int = 0) -> None:
    prefix = '  ' * indent
    if isinstance(node, NumberNode):
        print(f"{prefix}Number({node.value})")
    elif isinstance(node, BinaryOpNode):
        print(f"{prefix}BinaryOp('{node.op}')")
        print_ast(node.left, indent + 1)
        print_ast(node.right, indent + 1)
    elif isinstance(node, AssignNode):
        print(f"{prefix}Assign('{node.var_name}', )")
        print_ast(node.expr, indent + 1)
    else:
        print(f"{prefix}{node!r}")



def semantic_check_ast(ast: Any, sym_table: dict = None) -> Union[None, str]:

    if sym_table is None:
        sym_table = {}


    if isinstance(ast, AssignNode):

        err_expr = semantic_check_ast(ast.expr, sym_table)
        if err_expr:
            return err_expr
    
        sym_table[ast.var_name] = True
        return None

    if isinstance(ast, NumberNode):
        return None

    if isinstance(ast, BinaryOpNode):
    
        err_left = semantic_check_ast(ast.left, sym_table)
        if err_left:
            return err_left
      
        err_right = semantic_check_ast(ast.right, sym_table)
        if err_right:
            return err_right
  
        if ast.op == '/' and isinstance(ast.right, NumberNode) and ast.right.value == 0:
            return "Error semántico: división por cero detectada en AST."
        return None

    return None


def evaluate(node: Any, sym_values: dict = None) -> Union[int, float, dict]:

    if sym_values is None:
        sym_values = {}

    if isinstance(node, NumberNode):
        return node.value

    if isinstance(node, BinaryOpNode):
        left_val = evaluate(node.left, sym_values)
        right_val = evaluate(node.right, sym_values)
        if node.op == '+':
            return left_val + right_val
        if node.op == '-':
            return left_val - right_val
        if node.op == '*':
            return left_val * right_val
        if node.op == '/':
            if right_val == 0:
                raise ZeroDivisionError("División por cero en tiempo de ejecución.")
            return left_val / right_val
        raise Exception(f"Operador desconocido '{node.op}'")

    if isinstance(node, AssignNode):
        val = evaluate(node.expr, sym_values)
        sym_values[node.var_name] = val
        return sym_values

    raise Exception("Nodo AST inválido")


if __name__ == "__main__":
   
    expression_to_test = "y = 3 + 4(2 - 1) / 55"

    print(f"Expresión a analizar: {expression_to_test}\n")

    try:
        tokens = tokenize(expression_to_test)
        print("Tokens generados:")
        for t in tokens[:-1]:
            print(f"  {t.type:6} → {t.value!r}")
    except SyntaxError as e:
        print(f"Error léxico: {e}")
        exit(1)

    try:
        parser = Parser(tokens)
        ast = parser.parse()
        print("\nAST generado:")
        print_ast(ast)
    except SyntaxError as e:
        print(f"\nError sintáctico: {e}")
        exit(1)


    sem_error = semantic_check_ast(ast, sym_table={})
    if sem_error:
        print(f"\n{sem_error}")
        exit(1)

    try:
        resultado = evaluate(ast, sym_values={})
        if isinstance(resultado, dict):
            print("\nNo se encontraron errores semánticos.")
            print("Valores de variables después de la ejecución:")
            for var, val in resultado.items():
                print(f"  {var} = {val}")
        else:
            print(f"\nNo se encontraron errores semánticos. Resultado = {resultado}")
    except ZeroDivisionError as e:
        print(f"\nError semántico en tiempo de ejecución: {e}")
        exit(1)




   
