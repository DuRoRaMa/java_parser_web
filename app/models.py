from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict


class ParseRequest(BaseModel):
    tokens: List[Dict] = Field(default=[], description="Tokens from Java lexer")
    code: str = Field(default="", description="Optional source code for reference")


class ParseFromCodeRequest(BaseModel):
    code: str = Field(..., description="Java source code to parse")
    keep_comments: bool = Field(default=False, description="Keep comments in tokens")


class HealthResponse(BaseModel):
    status: str
    service: str
    lexer_available: bool = False


class ASTNodeOut(BaseModel):
    node_type: str
    position: Dict[str, int]
    
    # Children (для общих узлов)
    children: List['ASTNodeOut'] = []
    
    # === Common fields ===
    name: Optional[str] = None
    value: Optional[Any] = None
    literal_type: Optional[str] = None
    operator: Optional[str] = None
    modifiers: List[str] = []
    is_array: Optional[bool] = None
    
    # === BinaryOperation ===
    left: Optional['ASTNodeOut'] = None
    right: Optional['ASTNodeOut'] = None
    
    # === UnaryOperation ===
    operand: Optional['ASTNodeOut'] = None
    is_postfix: Optional[bool] = None
    
    # === TernaryOperation ===
    condition: Optional['ASTNodeOut'] = None
    then_expr: Optional['ASTNodeOut'] = None
    else_expr: Optional['ASTNodeOut'] = None
    
    # === Assignment ===
    variable: Optional['ASTNodeOut'] = None
    # value уже есть выше
    
    # === MethodCall ===
    method_name: Optional[str] = None
    target: Optional['ASTNodeOut'] = None
    arguments: List['ASTNodeOut'] = []
    
    # === Declarations ===
    return_type: Optional['ASTNodeOut'] = None
    field_type: Optional['ASTNodeOut'] = None
    param_type: Optional['ASTNodeOut'] = None
    var_type: Optional['ASTNodeOut'] = None
    parameters: List['ASTNodeOut'] = []
    
    # === Block ===
    statements: List['ASTNodeOut'] = []
    
    # === Program ===
    classes: List['ASTNodeOut'] = []
    imports: List[str] = []
    package: Optional[str] = None
    
    # === ClassDeclaration ===
    fields: List['ASTNodeOut'] = []
    methods: List['ASTNodeOut'] = []
    constructors: List['ASTNodeOut'] = []  # NEW! Конструкторы
    extends: Optional[str] = None
    implements: List[str] = []
    
    # === Type ===
    generic_types: List['ASTNodeOut'] = []
    
    # === Method body ===
    body: Optional['ASTNodeOut'] = None
    
    # === BreakStatement / ContinueStatement ===
    label: Optional[str] = None
    
    # === ForEachStatement ===
    var_name: Optional[str] = None
    iterable: Optional['ASTNodeOut'] = None

    # === ArrayCreation / ObjectCreation ===
    element_type: Optional['ASTNodeOut'] = None
    class_type: Optional['ASTNodeOut'] = None
    size: Optional['ASTNodeOut'] = None
    
    # === ArrayAccess ===
    array: Optional['ASTNodeOut'] = None
    index: Optional['ASTNodeOut'] = None
    
    # === instanceof ===
    check_type: Optional['ASTNodeOut'] = None
    
    # === throws (для методов и конструкторов) ===
    throws: Optional[List['ASTNodeOut']] = None
    
    # === ThrowStatement / общее выражение ===
    expression: Optional['ASTNodeOut'] = None
    
    # === TryStatement ===
    try_block: Optional['ASTNodeOut'] = None
    catch_clauses: List['ASTNodeOut'] = []
    finally_block: Optional['ASTNodeOut'] = None
    
    # === CatchClause ===
    exception_type: Optional['ASTNodeOut'] = None
    exception_name: Optional[str] = None
    target_type: Optional['ASTNodeOut'] = None
    cases: List['ASTNodeOut'] = []
    case_label: Optional['ASTNodeOut'] = None  # NEW! (отдельно от label)
    is_default: Optional[bool] = None

class ParseResponse(BaseModel):
    ast: ASTNodeOut
    tokens: Optional[List[Dict]] = None
    success: bool = True
    message: str = "Parsing completed successfully"


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    expected: Optional[str] = None
    actual: Optional[str] = None


# Для Pydantic v2 - разрешаем рекурсивные ссылки
ASTNodeOut.model_rebuild()
