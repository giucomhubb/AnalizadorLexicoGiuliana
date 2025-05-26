#a01562646 Giuliana Herrera Lopez
import re
import json
from dataclasses import dataclass
from typing import List, Dict, Any
#grammar definition
grammar = {
    'Expr': [
        ['Term', 'ExprTail'],
    ],
    'ExprTail': [
        ['PLUS', 'Term', 'ExprTail'],
        ['MINUS', 'Term', 'ExprTail'],
    ],
    'Term': [
        ['Factor', 'TermTail'],
    ],
    'TermTail': [
        ['STAR', 'Factor', 'TermTail'],
        ['SLASH', 'Factor', 'TermTail'],
        []
    ],
    'Factor': [
        ['NUMBER'],
        ['LPAREN', 'Expr', 'RPAREN'],
    ],
}
# types of tokens
tokenTypes = [
    ('NUMBER',     r'\d+'),
    ('PLUS',       r'\+'),
    ('MINUS',      r'-'),
    ('LPAREN',     r'\('),
    ('RPAREN',     r'\)'),
    ('SLASH',      r'/'),
    ('STAR',       r'\*'),
    ('WHITESPACE', r'\s+'),
]

compiledTokenTypes = [
    (name, re.compile(rf'^{pattern}'))
    for name, pattern in tokenTypes
]

#class
@dataclass
class Token:
    type: str
    value: str
    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "value": self.value}
@dataclass
class NumberNode:
    value: str

@dataclass
class BinaryOpNode:
    op: str
    left: Any
    right: Any
    
@dataclass
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current_token_index = 0
    
    def lookahead(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        else:
            return Token('EOF', '')
    def consume(self, expected_type: str):
        tok=self.lookahead()
        if tok.type == expected_type:
            self.current_token_index += 1
            return tok
        else:
            raise SyntaxError(f"Expected token type {expected_type}, but got {tok.type} instead.")
    def parse_term(self):
        node = self.parse_factor()
        while True:
            tok = self.lookahead()
            if tok.type in ('STAR', 'SLASH'):
                op = self.consume(tok.type)
                right = self.parse_factor()
                node = BinaryOpNode(op.value, node, right)
            else:
                break
        return node
    def parse_expression(self):
        node = self.parse_term()
        while True:
            tok = self.lookahead()
            if tok.type in ('PLUS', 'MINUS'):
                op = self.consume(tok.type)
                right = self.parse_term()
                node = BinaryOpNode(op.value, node, right)
            else:
                break
        return node 
    def parse_factor(self):
        tok = self.lookahead()
        if tok.type == 'NUMBER':
            self.consume('NUMBER')
            return NumberNode(tok.value)
        elif tok.type == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_expression()
            self.consume('RPAREN')
            return node
        else:
            raise SyntaxError(f"Unexpected token {tok.type} at position {self.current_token_index}")

    def parse(self):
        node = self.parse_expression()
        if self.lookahead().type != 'EOF':
            raise SyntaxError("Unexpected tokens: " +
                          self.lookahead().type)
        return node

   

# Tokenizer function
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
            lexeme_len = len(lexeme)
            # Skip whitespace tokens
            if name != 'WHITESPACE':
                tokens.append(Token(name, lexeme))
            pos += lexeme_len
            break
        else:
    
            raise SyntaxError(f"Unexpected character {text[pos]!r} at position {pos}")
    return tokens

def batch_tokenize(json_input: str) -> str:
    
    expressions = json.loads(json_input)
    result = []
    for expr in expressions:
        try:
            token_list = tokenize(expr)
        except SyntaxError as e:
            result.append({"error": str(e)})
            continue
        result.append([t.to_dict() for t in token_list])
    return json.dumps(result, indent=2)

def print_ast(node, indent=0):
    prefix = '  ' * indent
    if isinstance(node, NumberNode):
        print(f"{prefix}Number({node.value})")
    elif isinstance(node, BinaryOpNode):
        print(f"{prefix}BinaryOp('{node.op}')")
        print_ast(node.left,  indent+1)
        print_ast(node.right, indent+1)
    else:
        print(f"{prefix}{node!r}")


# example usage 
text = "3 + 4 * (2 - 1) / 55"
tokens = tokenize(text)
print("Tokens:")
for t in tokens:
    print(f"  {t.type:6} → {t.value!r}")
parser = Parser(tokens)
print_ast(parser.parse())





   
