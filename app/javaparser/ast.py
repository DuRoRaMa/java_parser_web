from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum

class NodeType(Enum):
    PROGRAM = "Program"
    CLASS_DECLARATION = "ClassDeclaration"
    METHOD_DECLARATION = "MethodDeclaration"
    FIELD_DECLARATION = "FieldDeclaration"
    VARIABLE_DECLARATION = "VariableDeclaration"
    TYPE = "Type"
    BLOCK = "Block"
    EXPRESSION_STATEMENT = "ExpressionStatement"
    ASSIGNMENT = "Assignment"
    BINARY_OPERATION = "BinaryOperation"
    UNARY_OPERATION = "UnaryOperation"
    LITERAL = "Literal"
    IDENTIFIER = "Identifier"
    IF_STATEMENT = "IfStatement"
    WHILE_STATEMENT = "WhileStatement"
    FOR_STATEMENT = "ForStatement"
    RETURN_STATEMENT = "ReturnStatement"
    METHOD_CALL = "MethodCall"
    FIELD_ACCESS = "FieldAccess"
    PARAMETER = "Parameter"
    IMPORT = "Import"
    PACKAGE = "Package"

@dataclass
class Position:
    line: int
    column: int

@dataclass
class ASTNode:
    node_type: NodeType
    position: Position
    children: List[ASTNode] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []

    def add_child(self, child: ASTNode):
        self.children.append(child)

@dataclass
class Identifier(ASTNode):
    name: str = ""

@dataclass
class Type(ASTNode):
    name: str = ""
    is_array: bool = False
    generic_types: List[Type] = None

    def __post_init__(self):
        super().__post_init__()
        if self.generic_types is None:
            self.generic_types = []

@dataclass
class Literal(ASTNode):
    value: str = ""
    literal_type: str = ""  # "int", "float", "string", "char", "boolean", "null"

@dataclass
class BinaryOperation(ASTNode):
    operator: str = ""
    left: Optional[ASTNode] = None
    right: Optional[ASTNode] = None

@dataclass
class Assignment(ASTNode):
    variable: Optional[ASTNode] = None
    value: Optional[ASTNode] = None

@dataclass
class MethodCall(ASTNode):
    method_name: str = ""
    arguments: List[ASTNode] = None

    def __post_init__(self):
        super().__post_init__()
        if self.arguments is None:
            self.arguments = []

@dataclass
class Block(ASTNode):
    statements: List[ASTNode] = None

    def __post_init__(self):
        super().__post_init__()
        if self.statements is None:
            self.statements = []

@dataclass
class Parameter(ASTNode):
    param_type: Optional[Type] = None
    name: str = ""

@dataclass
class MethodDeclaration(ASTNode):
    name: str = ""
    return_type: Optional[Type] = None
    parameters: List[Parameter] = None
    body: Optional[Block] = None
    modifiers: List[str] = None

    def __post_init__(self):
        super().__post_init__()
        if self.parameters is None:
            self.parameters = []
        if self.modifiers is None:
            self.modifiers = []

@dataclass
class FieldDeclaration(ASTNode):
    field_type: Optional[Type] = None
    name: str = ""
    value: Optional[ASTNode] = None
    modifiers: List[str] = None

    def __post_init__(self):
        super().__post_init__()
        if self.modifiers is None:
            self.modifiers = []

@dataclass
class ClassDeclaration(ASTNode):
    name: str = ""
    fields: List[FieldDeclaration] = None
    methods: List[MethodDeclaration] = None
    modifiers: List[str] = None

    def __post_init__(self):
        super().__post_init__()
        if self.fields is None:
            self.fields = []
        if self.methods is None:
            self.methods = []
        if self.modifiers is None:
            self.modifiers = []

@dataclass
class Program(ASTNode):
    classes: List[ClassDeclaration] = None
    imports: List[str] = None

    def __post_init__(self):
        super().__post_init__()
        if self.classes is None:
            self.classes = []
        if self.imports is None:
            self.imports = []