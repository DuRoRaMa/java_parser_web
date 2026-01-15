from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class NodeType(Enum):
    # Программа и структура
    PROGRAM = "Program"
    CLASS_DECLARATION = "ClassDeclaration"
    METHOD_DECLARATION = "MethodDeclaration"
    FIELD_DECLARATION = "FieldDeclaration"
    VARIABLE_DECLARATION = "VariableDeclaration"
    TYPE = "Type"
    BLOCK = "Block"
    PARAMETER = "Parameter"
    IMPORT = "Import"
    PACKAGE = "Package"


    # Выражения
    EXPRESSION_STATEMENT = "ExpressionStatement"
    ASSIGNMENT = "Assignment"
    BINARY_OPERATION = "BinaryOperation"
    TERNARY_OPERATION = "TernaryOperation"
    UNARY_OPERATION = "UnaryOperation"
    LITERAL = "Literal"
    IDENTIFIER = "Identifier"
    METHOD_CALL = "MethodCall"
    FIELD_ACCESS = "FieldAccess"
    ARRAY_CREATION = "ArrayCreation"      # NEW!
    OBJECT_CREATION = "ObjectCreation"    # NEW!
    ARRAY_ACCESS = "ArrayAccess"          # NEW! (для arr[i])
    CONSTRUCTOR_DECLARATION = "ConstructorDeclaration"
    THIS_CALL = "ThisCall"       # this(args)
    SUPER_CALL = "SuperCall"     # super(args)
    CAST_EXPRESSION = "CastExpression"

    # Управляющие конструкции
    THROW_STATEMENT = "ThrowStatement"
    INSTANCEOF_EXPRESSION = "InstanceofExpression"
    IF_STATEMENT = "IfStatement"
    WHILE_STATEMENT = "WhileStatement"
    DO_WHILE_STATEMENT = "DoWhileStatement"
    FOR_STATEMENT = "ForStatement"
    FOR_EACH_STATEMENT = "ForEachStatement"
    RETURN_STATEMENT = "ReturnStatement"
    BREAK_STATEMENT = "BreakStatement"
    CONTINUE_STATEMENT = "ContinueStatement"
    TRY_STATEMENT = "TryStatement"
    CATCH_CLAUSE = "CatchClause"
    SWITCH_STATEMENT = "SwitchStatement"
    SWITCH_CASE = "SwitchCase"
@dataclass
class Position:
    line: int
    column: int


@dataclass
class ASTNode:
    """Базовый класс для всех узлов AST."""
    node_type: NodeType
    position: Position
    children: List[ASTNode] = field(default_factory=list)
    name: str = ""

    def add_child(self, child: ASTNode):
        if child is not None:
            self.children.append(child)


@dataclass
class Identifier(ASTNode):
    """Идентификатор."""
    pass


@dataclass
class Type(ASTNode):
    """Тип данных."""
    is_array: bool = False
    generic_types: List[Type] = field(default_factory=list)


@dataclass
class Literal(ASTNode):
    """Литерал."""
    value: str = ""
    literal_type: str = ""


@dataclass
class BinaryOperation(ASTNode):
    """Бинарная операция."""
    operator: str = ""
    left: Optional[ASTNode] = None
    right: Optional[ASTNode] = None


@dataclass
class TernaryOperation(ASTNode):
    """Тернарная операция."""
    condition: Optional[ASTNode] = None
    then_expr: Optional[ASTNode] = None
    else_expr: Optional[ASTNode] = None


@dataclass
class UnaryOperation(ASTNode):
    """Унарная операция."""
    operator: str = ""
    operand: Optional[ASTNode] = None
    is_postfix: bool = False


@dataclass
class Assignment(ASTNode):
    """Присваивание."""
    operator: str = "="
    variable: Optional[ASTNode] = None
    value: Optional[ASTNode] = None


@dataclass
class MethodCall(ASTNode):
    """Вызов метода."""
    method_name: str = ""
    arguments: List[ASTNode] = field(default_factory=list)
    target: Optional[ASTNode] = None


@dataclass
class Parameter(ASTNode):
    """Параметр метода."""
    param_type: Optional[Type] = None


@dataclass
class VariableDeclaration(ASTNode):
    """Объявление переменной."""
    var_type: Optional[Type] = None
    value: Optional[ASTNode] = None
    modifiers: List[str] = field(default_factory=list)

@dataclass
class SwitchCase(ASTNode):
    """Один case в switch.
    
    Примеры:
        case 1:
        case "hello":
        case MyEnum.VALUE:
        default:
    """
    case_label: Optional[ASTNode] = None  # выражение case (None для default)
    statements: List[ASTNode] = field(default_factory=list)
    is_default: bool = False


@dataclass
class SwitchStatement(ASTNode):
    """Оператор switch.
    
    Пример:
        switch (x) {
            case 1: ...
            default: ...
        }
    """
    expression: Optional[ASTNode] = None  # выражение в switch(...)
    cases: List[SwitchCase] = field(default_factory=list)
@dataclass
class FieldDeclaration(ASTNode):
    """Объявление поля класса."""
    field_type: Optional[Type] = None
    value: Optional[ASTNode] = None
    modifiers: List[str] = field(default_factory=list)

@dataclass
class CatchClause(ASTNode):
    """Блок catch.
    
    Пример: catch (IOException e) { ... }
    """
    exception_type: Optional[Type] = None      # тип исключения (IOException)
    exception_name: str = ""                    # имя переменной (e)
    body: Optional[Block] = None               # тело catch


@dataclass
class TryStatement(ASTNode):
    """Оператор try-catch-finally.
    
    Пример:
        try { ... } 
        catch (IOException e) { ... } 
        finally { ... }
    """
    try_block: Optional[Block] = None          # блок try
    catch_clauses: List[CatchClause] = field(default_factory=list)  # список catch
    finally_block: Optional[Block] = None      # блок finally (опционально)

@dataclass
class Block(ASTNode):
    """Блок кода."""
    statements: List[ASTNode] = field(default_factory=list)


@dataclass
class MethodDeclaration(ASTNode):
    """Объявление метода."""
    return_type: Optional[Type] = None
    parameters: List[Parameter] = field(default_factory=list)
    body: Optional[Block] = None
    modifiers: List[str] = field(default_factory=list)
    throws: List[Type] = field(default_factory=list)  # NEW!


@dataclass
class ClassDeclaration(ASTNode):
    """Объявление класса."""
    modifiers: List[str] = field(default_factory=list)
    extends: Optional[str] = None
    implements: List[str] = field(default_factory=list)
    fields: List[FieldDeclaration] = field(default_factory=list)
    methods: List[MethodDeclaration] = field(default_factory=list)
    constructors: List['ConstructorDeclaration'] = field(default_factory=list)  # NEW!


@dataclass
class BreakStatement(ASTNode):
    """Оператор break."""
    label: Optional[str] = None


@dataclass
class ContinueStatement(ASTNode):
    """Оператор continue."""
    label: Optional[str] = None


@dataclass
class DoWhileStatement(ASTNode):
    """Цикл do-while."""
    pass


@dataclass
class ForEachStatement(ASTNode):
    """Цикл for-each."""
    var_type: Optional[Type] = None
    var_name: str = ""
    iterable: Optional[ASTNode] = None
    body: Optional[ASTNode] = None

# ============ NEW CLASSES ============
@dataclass
class CastExpression(ASTNode):
    """Приведение типов: (String) obj"""
    target_type: Optional[Type] = None    # тип к которому приводим
    expression: Optional[ASTNode] = None  # выражение которое приводим
@dataclass
class ArrayCreation(ASTNode):
    """Создание массива: new int[5]"""
    element_type: Optional[Type] = None
    size: Optional[ASTNode] = None


@dataclass
class ObjectCreation(ASTNode):
    """Создание объекта: new MyClass(args)"""
    class_type: Optional[Type] = None
    arguments: List[ASTNode] = field(default_factory=list)


@dataclass
class ArrayAccess(ASTNode):
    """Доступ к элементу массива: arr[i]"""
    array: Optional[ASTNode] = None
    index: Optional[ASTNode] = None


# ============ END NEW CLASSES ============
@dataclass
class ThrowStatement(ASTNode):
    """Оператор throw: throw new Exception("error");"""
    expression: Optional[ASTNode] = None

@dataclass
class ConstructorDeclaration(ASTNode):
    """Объявление конструктора.
    
    Пример: public Person(String name) { this.name = name; }
    """
    name: str = ""                              # имя класса (Person)
    parameters: List['Parameter'] = field(default_factory=list)
    body: Optional['Block'] = None
    modifiers: List[str] = field(default_factory=list)  # public, private, protected
    throws: List['Type'] = field(default_factory=list)  # throws IOException


@dataclass  
class ThisCall(ASTNode):
    """Вызов другого конструктора этого класса.
    
    Пример: this(arg1, arg2);
    """
    arguments: List[ASTNode] = field(default_factory=list)


@dataclass
class SuperCall(ASTNode):
    """Вызов конструктора родительского класса.
    
    Пример: super(arg1, arg2);
    """
    arguments: List[ASTNode] = field(default_factory=list)

@dataclass
class InstanceofExpression(ASTNode):
    """Проверка типа: obj instanceof String"""
    expression: Optional[ASTNode] = None  # левая часть (obj)
    check_type: Optional[Type] = None      # правая часть (String)
@dataclass
class Program(ASTNode):
    """Корневой узел программы."""
    package: Optional[str] = None
    imports: List[str] = field(default_factory=list)
    classes: List[ClassDeclaration] = field(default_factory=list)
