from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class ParseRequest(BaseModel):
    tokens: List[Dict] = Field([], description="Tokens from Java lexer")
    code: str = Field("", description="Optional source code for reference")

class ParseFromCodeRequest(BaseModel):
    code: str = Field(..., description="Java source code to parse")
    keep_comments: bool = Field(False, description="Keep comments in tokens")

class HealthResponse(BaseModel):
    status: str
    service: str
    lexer_available: bool = False

class ASTNodeOut(BaseModel):
    node_type: str
    position: Dict[str, int]
    children: List['ASTNodeOut'] = []
    
    # Common fields
    name: Optional[str] = None
    value: Optional[str] = None
    literal_type: Optional[str] = None
    operator: Optional[str] = None
    modifiers: List[str] = []
    is_array: Optional[bool] = None
    
    # For declarations
    return_type: Optional['ASTNodeOut'] = None
    field_type: Optional['ASTNodeOut'] = None
    parameters: List['ASTNodeOut'] = []
    arguments: List['ASTNodeOut'] = []
    statements: List['ASTNodeOut'] = []
    
    # For program
    classes: List['ASTNodeOut'] = []
    imports: List[str] = []

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

# Используем model_rebuild вместо update_forward_refs для Pydantic v2
ASTNodeOut.model_rebuild()