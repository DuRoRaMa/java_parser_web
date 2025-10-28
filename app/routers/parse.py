from fastapi import APIRouter, HTTPException
from app.models import ParseRequest, ParseResponse, ErrorResponse
from app.javaparser import Parser
from app.javaparser.errors import ParseError, UnexpectedTokenError

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
    """Convert AST node to serializable dictionary"""
    if node is None:
        return None
    
    result = {
        "node_type": node.node_type.value,
        "position": {
            "line": node.position.line,
            "column": node.position.column
        },
        "children": [_ast_to_dict(child) for child in node.children]
    }
    
    # Add type-specific fields
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
    
    # For declarations
    if hasattr(node, 'return_type'):
        result["return_type"] = _ast_to_dict(node.return_type)
    if hasattr(node, 'field_type'):
        result["field_type"] = _ast_to_dict(node.field_type)
    if hasattr(node, 'parameters'):
        result["parameters"] = [_ast_to_dict(param) for param in node.parameters]
    if hasattr(node, 'arguments'):
        result["arguments"] = [_ast_to_dict(arg) for arg in node.arguments]
    if hasattr(node, 'statements'):
        result["statements"] = [_ast_to_dict(stmt) for stmt in node.statements]
    
    # For program
    if hasattr(node, 'classes'):
        result["classes"] = [_ast_to_dict(cls) for cls in node.classes]
    if hasattr(node, 'imports'):
        result["imports"] = node.imports
    
    return result