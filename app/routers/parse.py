import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from app.models import ParseRequest, ParseResponse
from app.javaparser import Parser
from app.javaparser.errors import ParseError
from app.javaparser.ast import (
    ASTNode, Program, ClassDeclaration, MethodDeclaration, FieldDeclaration,
    VariableDeclaration, Type, BinaryOperation, Assignment, Literal, Identifier,
    MethodCall, Block, Parameter, UnaryOperation,
    TernaryOperation, BreakStatement, ContinueStatement, DoWhileStatement,
    ForEachStatement, ArrayCreation, ObjectCreation, ArrayAccess, ThrowStatement, InstanceofExpression,
    TryStatement, CatchClause, ConstructorDeclaration, ThisCall, 
    SuperCall, CastExpression, SwitchStatement, SwitchCase   # NEW!
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/parse", tags=["parser"])


@router.post("", response_model=ParseResponse)
def parse_java(req: ParseRequest):
    """Parse Java tokens into AST."""
    try:
        parser = Parser(req.tokens)
        ast = parser.parse()
        ast_out = ast_to_dict(ast)
        return ParseResponse(ast=ast_out)
        
    except ParseError as e:
        logger.warning(f"Parse error at {e.line}:{e.column}: {e.message}")
        raise HTTPException(
            status_code=422,
            detail={
                "message": e.message,
                "line": e.line,
                "column": e.column,
                "success": False
            }
        )
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"Invalid request: {str(e)}",
                "success": False
            }
        )
    except Exception as e:
        logger.exception("Unexpected error during parsing")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Internal server error during parsing",
                "success": False
            }
        )


def ast_to_dict(node: Optional[ASTNode]) -> Optional[Dict[str, Any]]:
    """Convert AST node to dictionary for JSON serialization."""
    if node is None:
        return None
    
    # Базовые поля для всех узлов
    result: Dict[str, Any] = {
        "node_type": node.node_type.value if hasattr(node.node_type, 'value') else str(node.node_type),
        "position": {
            "line": node.position.line,
            "column": node.position.column
        }
    }
    
    # ========== Обработка по типам ==========
    
    # ============ NEW: ConstructorDeclaration ============
    if isinstance(node, ConstructorDeclaration):
        result["name"] = node.name
        result["modifiers"] = node.modifiers
        result["parameters"] = [ast_to_dict(p) for p in node.parameters]
        result["body"] = ast_to_dict(node.body)
        if node.throws:
            result["throws"] = [ast_to_dict(t) for t in node.throws]
        return result
    
    if isinstance(node, CastExpression):
        result["target_type"] = ast_to_dict(node.target_type)
        result["expression"] = ast_to_dict(node.expression)
        return result
    # ============ NEW: ThisCall ============
    if isinstance(node, ThisCall):
        result["arguments"] = [ast_to_dict(a) for a in node.arguments]
        return result
    
    # ============ NEW: SuperCall ============
    if isinstance(node, SuperCall):
        result["arguments"] = [ast_to_dict(a) for a in node.arguments]
        return result
    # ============ SwitchStatement ============
    if isinstance(node, SwitchStatement):
        result["expression"] = ast_to_dict(node.expression)
        result["cases"] = [ast_to_dict(c) for c in node.cases]
        return result

    # ============ SwitchCase ============
    if isinstance(node, SwitchCase):
        result["case_label"] = ast_to_dict(node.case_label)  # ПЕРЕИМЕНОВАНО
        result["statements"] = [ast_to_dict(s) for s in node.statements]
        result["is_default"] = node.is_default
        return result
    # ============ ArrayCreation ============
    if isinstance(node, ArrayCreation):
        result["element_type"] = ast_to_dict(node.element_type)
        result["size"] = ast_to_dict(node.size)
        if node.name:
            result["name"] = node.name
        if node.children:
            result["children"] = [ast_to_dict(c) for c in node.children]
        return result
    
    # ============ ObjectCreation ============
    if isinstance(node, ObjectCreation):
        result["class_type"] = ast_to_dict(node.class_type)
        result["arguments"] = [ast_to_dict(arg) for arg in node.arguments]
        if node.name:
            result["name"] = node.name
        return result
    
    # ============ TryStatement ============
    if isinstance(node, TryStatement):
        result["try_block"] = ast_to_dict(node.try_block)
        result["catch_clauses"] = [ast_to_dict(c) for c in node.catch_clauses]
        if node.finally_block:
            result["finally_block"] = ast_to_dict(node.finally_block)
        return result

    # ============ CatchClause ============
    if isinstance(node, CatchClause):
        result["exception_type"] = ast_to_dict(node.exception_type)
        result["exception_name"] = node.exception_name
        result["body"] = ast_to_dict(node.body)
        return result
    
    # ============ ArrayAccess ============
    if isinstance(node, ArrayAccess):
        result["array"] = ast_to_dict(node.array)
        result["index"] = ast_to_dict(node.index)
        return result
    
    # BinaryOperation
    if isinstance(node, BinaryOperation):
        result["operator"] = node.operator
        result["left"] = ast_to_dict(node.left)
        result["right"] = ast_to_dict(node.right)
        return result
    
    # UnaryOperation
    if isinstance(node, UnaryOperation):
        result["operator"] = node.operator
        result["operand"] = ast_to_dict(node.operand)
        result["is_postfix"] = node.is_postfix
        return result
    
    # Assignment
    if isinstance(node, Assignment):
        result["operator"] = node.operator
        result["variable"] = ast_to_dict(node.variable)
        result["value"] = ast_to_dict(node.value)
        return result
    
    # Literal
    if isinstance(node, Literal):
        result["value"] = node.value
        result["literal_type"] = node.literal_type
        return result
    
    # Identifier
    if isinstance(node, Identifier):
        result["name"] = node.name
        return result
    
    # Type
    if isinstance(node, Type):
        result["name"] = node.name
        result["is_array"] = node.is_array
        if node.generic_types:
            result["generic_types"] = [ast_to_dict(g) for g in node.generic_types]
        return result
    
    # Parameter
    if isinstance(node, Parameter):
        result["name"] = node.name
        result["param_type"] = ast_to_dict(node.param_type)
        return result
    
    # VariableDeclaration
    if isinstance(node, VariableDeclaration):
        result["name"] = node.name
        result["var_type"] = ast_to_dict(node.var_type)
        result["value"] = ast_to_dict(node.value)
        result["modifiers"] = node.modifiers
        return result
    
    # FieldDeclaration
    if isinstance(node, FieldDeclaration):
        result["name"] = node.name
        result["field_type"] = ast_to_dict(node.field_type)
        result["value"] = ast_to_dict(node.value)
        result["modifiers"] = node.modifiers
        return result
    
    # ThrowStatement
    if isinstance(node, ThrowStatement):
        result["expression"] = ast_to_dict(node.expression)
        return result
    
    # InstanceofExpression
    if isinstance(node, InstanceofExpression):
        result["expression"] = ast_to_dict(node.expression)
        result["check_type"] = ast_to_dict(node.check_type)
        return result
    
    # MethodCall
    if isinstance(node, MethodCall):
        result["method_name"] = node.method_name
        result["arguments"] = [ast_to_dict(arg) for arg in node.arguments]
        if node.target:
            result["target"] = ast_to_dict(node.target)
        if node.children:
            result["children"] = [ast_to_dict(c) for c in node.children]
        return result
    
    # Block
    if isinstance(node, Block):
        result["statements"] = [ast_to_dict(s) for s in node.statements]
        return result
    
    # MethodDeclaration
    if isinstance(node, MethodDeclaration):
        result["name"] = node.name
        result["modifiers"] = node.modifiers
        result["return_type"] = ast_to_dict(node.return_type)
        result["parameters"] = [ast_to_dict(p) for p in node.parameters]
        result["body"] = ast_to_dict(node.body)
        if node.throws:
            result["throws"] = [ast_to_dict(t) for t in node.throws]
        return result
    
    # TernaryOperation
    if isinstance(node, TernaryOperation):
        result["condition"] = ast_to_dict(node.condition)
        result["then_expr"] = ast_to_dict(node.then_expr)
        result["else_expr"] = ast_to_dict(node.else_expr)
        return result
    
    # BreakStatement
    if isinstance(node, BreakStatement):
        if node.label:
            result["label"] = node.label
        return result
    
    # ContinueStatement
    if isinstance(node, ContinueStatement):
        if node.label:
            result["label"] = node.label
        return result
    
    # DoWhileStatement
    if isinstance(node, DoWhileStatement):
        if len(node.children) >= 1:
            result["body"] = ast_to_dict(node.children[0])
        if len(node.children) >= 2:
            result["condition"] = ast_to_dict(node.children[1])
        return result
    
    # ForEachStatement
    if isinstance(node, ForEachStatement):
        result["var_type"] = ast_to_dict(node.var_type)
        result["var_name"] = node.var_name
        result["iterable"] = ast_to_dict(node.iterable)
        result["body"] = ast_to_dict(node.body)
        return result
    
    # ClassDeclaration - UPDATED!
    if isinstance(node, ClassDeclaration):
        result["name"] = node.name
        result["modifiers"] = node.modifiers
        if node.extends:
            result["extends"] = node.extends
        if node.implements:
            result["implements"] = node.implements
        result["fields"] = [ast_to_dict(f) for f in node.fields]
        result["methods"] = [ast_to_dict(m) for m in node.methods]
        result["constructors"] = [ast_to_dict(c) for c in node.constructors]  # NEW!
        if node.children:
            result["children"] = [ast_to_dict(c) for c in node.children]
        return result
    
    # Program
    if isinstance(node, Program):
        result["imports"] = node.imports
        if node.package:
            result["package"] = node.package
        result["classes"] = [ast_to_dict(c) for c in node.classes]
        return result
    
    # ========== Общий случай: ASTNode ==========
    if hasattr(node, 'name') and node.name:
        result["name"] = node.name
    
    if node.children:
        result["children"] = [ast_to_dict(c) for c in node.children]
    
    return result
