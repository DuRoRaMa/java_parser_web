from fastapi import APIRouter, HTTPException
from app.models import ParseRequest, ParseResponse, ErrorResponse
from app.javaparser import Parser
from app.javaparser.errors import ParseError, UnexpectedTokenError
from app.javaparser.ast import (  # ДОБАВЬТЕ ЭТОТ ИМПОРТ
    ASTNode, Program, ClassDeclaration, MethodDeclaration, FieldDeclaration,
    VariableDeclaration, Type, Identifier, Literal, BinaryOperation, Assignment,
    MethodCall, Block, Parameter, NodeType, Position
)

router = APIRouter(prefix="/api/parse", tags=["parser"])

@router.post("", response_model=ParseResponse)
def parse_java(req: ParseRequest):
    try:
        parser = Parser(req.tokens)
        ast = parser.parse()
        
        ast_out = _ast_to_dict(ast)
        return ParseResponse(ast=ast_out)
        
    except ParseError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "message": e.message,
                "line": e.line,
                "column": e.column,
                "success": False
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Internal server error: {str(e)}",
                "success": False
            }
        )

def _ast_to_dict(node):
    """Convert AST node to serializable dictionary - COMPLETE FIXED VERSION"""
    if node is None:
        return None
    
    # Базовая структура
    result = {
        "node_type": node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
        "position": {
            "line": node.position.line,
            "column": node.position.column
        }
    }
    
    # Обрабатываем children для всех узлов
    if hasattr(node, 'children') and node.children:
        result["children"] = [_ast_to_dict(child) for child in node.children]
    
    # Обрабатываем специфичные атрибуты для разных типов узлов
    if hasattr(node, 'name'):
        result["name"] = node.name
    
    if hasattr(node, 'value'):
        result["value"] = node.value
    
    if hasattr(node, 'literal_type'):
        result["literal_type"] = node.literal_type
    
    if hasattr(node, 'operator'):
        result["operator"] = node.operator
    
    if hasattr(node, 'modifiers'):
        result["modifiers"] = node.modifiers
    
    if hasattr(node, 'is_array'):
        result["is_array"] = node.is_array
    
    # Обрабатываем return_type
    if hasattr(node, 'return_type') and node.return_type:
        result["return_type"] = _ast_to_dict(node.return_type)
    
    # Обрабатываем field_type
    if hasattr(node, 'field_type') and node.field_type:
        result["field_type"] = _ast_to_dict(node.field_type)
    
    # Обрабатываем param_type для Parameter
    if hasattr(node, 'param_type') and node.param_type:
        result["param_type"] = _ast_to_dict(node.param_type)
    
    # Обрабатываем var_type для VariableDeclaration
    if hasattr(node, 'var_type') and node.var_type:
        result["var_type"] = _ast_to_dict(node.var_type)
    
    # Обрабатываем body для MethodDeclaration
    if hasattr(node, 'body') and node.body:
        result["body"] = _ast_to_dict(node.body)
    
    # Обрабатываем parameters
    if hasattr(node, 'parameters') and node.parameters:
        result["parameters"] = [_ast_to_dict(param) for param in node.parameters]
    
    # Обрабатываем arguments
    if hasattr(node, 'arguments') and node.arguments:
        result["arguments"] = [_ast_to_dict(arg) for arg in node.arguments]
    
    # Обрабатываем statements
    if hasattr(node, 'statements') and node.statements:
        result["statements"] = [_ast_to_dict(stmt) for stmt in node.statements]
    
    # Обрабатываем fields для ClassDeclaration
    if hasattr(node, 'fields') and node.fields:
        result["fields"] = [_ast_to_dict(field) for field in node.fields]
    
    # Обрабатываем methods для ClassDeclaration
    if hasattr(node, 'methods') and node.methods:
        result["methods"] = [_ast_to_dict(method) for method in node.methods]
    
    # Обрабатываем classes для Program
    if hasattr(node, 'classes') and node.classes:
        result["classes"] = [_ast_to_dict(cls) for cls in node.classes]
    
    # Обрабатываем imports для Program
    if hasattr(node, 'imports') and node.imports:
        result["imports"] = node.imports
    
    # Обрабатываем generic_types для Type
    if hasattr(node, 'generic_types') and node.generic_types:
        result["generic_types"] = [_ast_to_dict(gen_type) for gen_type in node.generic_types]
    
    # СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ BinaryOperation - ДОБАВЬТЕ ЭТО
    if isinstance(node, BinaryOperation):
        result["left"] = _ast_to_dict(node.left) if node.left else None
        result["right"] = _ast_to_dict(node.right) if node.right else None
    
    # СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ Assignment - ДОБАВЬТЕ ЭТО
    if isinstance(node, Assignment):
        result["variable"] = _ast_to_dict(node.variable) if node.variable else None
        result["value"] = _ast_to_dict(node.value) if node.value else None
    
    # СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ MethodCall - ДОБАВЬТЕ ЭТО
    if isinstance(node, MethodCall):
        result["method_name"] = node.method_name
        result["arguments"] = [_ast_to_dict(arg) for arg in node.arguments] if node.arguments else []
    
    # СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ VariableDeclaration - ДОБАВЬТЕ ЭТО
    if isinstance(node, VariableDeclaration):
        result["var_type"] = _ast_to_dict(node.var_type) if node.var_type else None
        result["value"] = _ast_to_dict(node.value) if node.value else None
    
    # Убираем None значения для чистого JSON
    result = {k: v for k, v in result.items() if v is not None and v != [] and v != ""}
    
    return result