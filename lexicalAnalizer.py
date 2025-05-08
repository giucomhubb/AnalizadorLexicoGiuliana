import re
import json
from dataclasses import dataclass
from typing import List, Dict, Any

# Define and compile the token types
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

@dataclass
class Token:
    type: str
    value: str

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "value": self.value}

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
    """
    Expects a JSON array of string expressions, returns a JSON array of token lists.
    """
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

#  JSON input with 4 test cases
json_input = json.dumps([
    "23 + (5 - 2) / 10",
    "7 * 8 - 9",
    "12 +    34",
    "111-111",
    "bad$char"
])


output_json = batch_tokenize(json_input)
print("Input JSON:")
print(json_input)
print("\nOutput JSON:")
print(output_json)



   
