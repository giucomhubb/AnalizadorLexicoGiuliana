# a01562646 Giuliana Herrera Lopez
import itertools
from dataclasses import dataclass
from typing import List, Dict, Union, Any, Optional



class ASTNode:
    pass

@dataclass
class VarDeclNode(ASTNode):
    name: str

@dataclass
class AssignNode(ASTNode):
    target: str
    expr: ASTNode

@dataclass
class BinaryOpNode(ASTNode):
    op: str                
    left: ASTNode
    right: ASTNode

@dataclass
class NumberNode(ASTNode):
    value: int

@dataclass
class IdentifierNode(ASTNode):
    name: str


ProgramAST = List[ASTNode]


class SymbolTable:
    
    def __init__(self):
        self._symbols: Dict[str, str] = {}

    def declare(self, name: str, type_name: str) -> Optional[str]:
        if name in self._symbols:
            return f"Variable '{name}' ya declarada"
        self._symbols[name] = type_name
        return None

    def is_declared(self, name: str) -> bool:
        return name in self._symbols

    def get_type(self, name: str) -> Optional[str]:
        return self._symbols.get(name, None)


class SemanticAnalyzer:

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[str] = []

    def analyze(self, program: ProgramAST) -> List[str]:
        for stmt in program:
            self._analyze_node(stmt)
        return self.errors

    def _analyze_node(self, node: ASTNode) -> None:
        if isinstance(node, VarDeclNode):
            err = self.symbol_table.declare(node.name, 'int')
            if err:
                self.errors.append(f"Error semántico: {err}")
            return

        if isinstance(node, AssignNode):
            if not self.symbol_table.is_declared(node.target):
                self.errors.append(f"Error semántico: Variable '{node.target}' no declarada")
            self._analyze_node(node.expr)
            return

        if isinstance(node, BinaryOpNode):
            self._analyze_node(node.left)
            self._analyze_node(node.right)
            return

        if isinstance(node, NumberNode):
            return

        if isinstance(node, IdentifierNode):
            if not self.symbol_table.is_declared(node.name):
                self.errors.append(f"Error semántico: Variable '{node.name}' no declarada")
            return

    
        self.errors.append(f"Error semántico: Nodo inesperado {node!r}")




class IntermediateCode:

    def __init__(self):
        self.instructions: List[str] = []

    def emit(self, instr: str) -> None:
        self.instructions.append(instr)

    def __iter__(self):
        return iter(self.instructions)


class CodeGenerator:
  
    def __init__(self):
        self.temp_count = itertools.count(1)
        self.code = IntermediateCode()

    def new_temp(self) -> str:
        return f"t{next(self.temp_count)}"

    def generate(self, program: ProgramAST) -> IntermediateCode:
        for stmt in program:
            self._gen_node(stmt)
        return self.code

    def _gen_node(self, node: ASTNode) -> Optional[str]:
        if isinstance(node, VarDeclNode):
           
            self.code.emit(f"declare {node.name}")
            return None

        if isinstance(node, AssignNode):
          
            rhs_temp = self._gen_node(node.expr)
            
            if rhs_temp is None and isinstance(node.expr, NumberNode):
                self.code.emit(f"{node.target} = {node.expr.value}")
            else:
                self.code.emit(f"{node.target} = {rhs_temp}")
            return None

        if isinstance(node, BinaryOpNode):
            
            left_temp = self._gen_node(node.left)
            right_temp = self._gen_node(node.right)

            if left_temp is None and isinstance(node.left, NumberNode):
                left_repr = str(node.left.value)
            else:
                left_repr = left_temp

            if right_temp is None and isinstance(node.right, NumberNode):
                right_repr = str(node.right.value)
            else:
                right_repr = right_temp

            t = self.new_temp()
            self.code.emit(f"{t} = {left_repr} {node.op} {right_repr}")
            return t

        if isinstance(node, NumberNode):
            return None

        if isinstance(node, IdentifierNode):
            return node.name

        raise RuntimeError(f"Código intermedio: nodo inesperado {node!r}")


if __name__ == "__main__":
    program_ast: ProgramAST = [
        VarDeclNode(name="x"),
        AssignNode(
            target="x",
            expr=BinaryOpNode(
                op="+",
                left=NumberNode(5),
                right=NumberNode(2)
            )
        ),
    ]


    sem = SemanticAnalyzer()
    errors = sem.analyze(program_ast)
    if errors:
        print("Errores semánticos encontrados:")
        for err in errors:
            print("  -", err)
    else:
        print("Sin errores semánticos.\n")
        gen = CodeGenerator()
        ic = gen.generate(program_ast)

        print("Código intermedio generado:")
        for instr in ic:
            print(" ", instr)



   
