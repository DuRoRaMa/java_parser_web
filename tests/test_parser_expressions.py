"""Тесты выражений."""
import pytest
from app.javaparser.ast import NodeType


class TestLiterals:
    """Тесты литералов."""
    
    def test_int_literal(self, parse, expr_wrapper, make_token):
        """return 42;"""
        tokens = expr_wrapper([make_token("INT_LITERAL", "42")])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        literal = stmt.children[0]
        assert literal.node_type == NodeType.LITERAL
        assert literal.value == "42"
        assert literal.literal_type == "int"
    
    def test_float_literal(self, parse, expr_wrapper, make_token):
        """return 3.14;"""
        tokens = expr_wrapper([make_token("FLOAT_LITERAL", "3.14")])
        result = parse(tokens)
        
        literal = result.classes[0].methods[0].body.statements[0].children[0]
        assert literal.literal_type == "float"
    
    def test_string_literal(self, parse, expr_wrapper, make_token):
        """return "hello";"""
        tokens = expr_wrapper([make_token("STRING_LITERAL", '"hello"')])
        result = parse(tokens)
        
        literal = result.classes[0].methods[0].body.statements[0].children[0]
        assert literal.literal_type == "string"
    
    def test_boolean_true(self, parse, expr_wrapper, make_token):
        """return true;"""
        tokens = expr_wrapper([make_token("KEYWORD", "true")])
        result = parse(tokens)
        
        literal = result.classes[0].methods[0].body.statements[0].children[0]
        assert literal.value == "true"
        assert literal.literal_type == "boolean"
    
    def test_null_literal(self, parse, expr_wrapper, make_token):
        """return null;"""
        tokens = expr_wrapper([make_token("KEYWORD", "null")])
        result = parse(tokens)
        
        literal = result.classes[0].methods[0].body.statements[0].children[0]
        assert literal.value == "null"


class TestBinaryOperations:
    """Тесты бинарных операций."""
    
    @pytest.mark.parametrize("op", ["+", "-", "*", "/", "%"])
    def test_arithmetic_ops(self, parse, expr_wrapper, make_token, op):
        """return a OP b;"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "a"),
            make_token("OPERATOR", op),
            make_token("IDENTIFIER", "b"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.BINARY_OPERATION
        assert expr.operator == op
    
    @pytest.mark.parametrize("op", ["==", "!=", "<", ">", "<=", ">="])
    def test_comparison_ops(self, parse, expr_wrapper, make_token, op):
        """return a OP b;"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "a"),
            make_token("OPERATOR", op),
            make_token("IDENTIFIER", "b"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.operator == op
    
    @pytest.mark.parametrize("op", ["&&", "||"])
    def test_logical_ops(self, parse, expr_wrapper, make_token, op):
        """return a OP b;"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "a"),
            make_token("OPERATOR", op),
            make_token("IDENTIFIER", "b"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.operator == op
    
    def test_operator_precedence(self, parse, expr_wrapper, make_token):
        """return a + b * c; -> a + (b * c)"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "a"),
            make_token("OPERATOR", "+"),
            make_token("IDENTIFIER", "b"),
            make_token("OPERATOR", "*"),
            make_token("IDENTIFIER", "c"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.operator == "+"
        assert expr.left.name == "a"
        assert expr.right.operator == "*"


class TestUnaryOperations:
    """Тесты унарных операций."""
    
    def test_negation(self, parse, expr_wrapper, make_token):
        """return -x;"""
        tokens = expr_wrapper([
            make_token("OPERATOR", "-"),
            make_token("IDENTIFIER", "x"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.UNARY_OPERATION
        assert expr.operator == "-"
        assert expr.is_postfix == False
    
    def test_logical_not(self, parse, expr_wrapper, make_token):
        """return !flag;"""
        tokens = expr_wrapper([
            make_token("OPERATOR", "!"),
            make_token("IDENTIFIER", "flag"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.operator == "!"
    
    def test_prefix_increment(self, parse, expr_wrapper, make_token):
        """return ++i;"""
        tokens = expr_wrapper([
            make_token("OPERATOR", "++"),
            make_token("IDENTIFIER", "i"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.operator == "++"
        assert expr.is_postfix == False
    
    def test_postfix_increment(self, parse, expr_wrapper, make_token):
        """return i++;"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "i"),
            make_token("OPERATOR", "++"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.operator == "++"
        assert expr.is_postfix == True


class TestTernary:
    """Тесты тернарного оператора."""
    
    def test_simple_ternary(self, parse, expr_wrapper, make_token):
        """return a ? b : c;"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "a"),
            make_token("OPERATOR", "?"),
            make_token("IDENTIFIER", "b"),
            make_token("OPERATOR", ":"),
            make_token("IDENTIFIER", "c"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.TERNARY_OPERATION


class TestMethodCalls:
    """Тесты вызовов методов."""
    
    def test_simple_call(self, parse, expr_wrapper, make_token):
        """return foo();"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "foo"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
        ])
        result = parse(tokens)
        
        call = result.classes[0].methods[0].body.statements[0].children[0]
        assert call.node_type == NodeType.METHOD_CALL
        assert call.method_name == "foo"
    
    def test_call_with_args(self, parse, expr_wrapper, make_token):
        """return add(1, 2);"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "add"),
            make_token("SEPARATOR", "("),
            make_token("INT_LITERAL", "1"),
            make_token("SEPARATOR", ","),
            make_token("INT_LITERAL", "2"),
            make_token("SEPARATOR", ")"),
        ])
        result = parse(tokens)
        
        call = result.classes[0].methods[0].body.statements[0].children[0]
        assert len(call.arguments) == 2


class TestInstanceof:
    """Тесты instanceof."""
    
    def test_instanceof(self, parse, expr_wrapper, make_token):
        """return obj instanceof String;"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "obj"),
            make_token("KEYWORD", "instanceof"),
            make_token("IDENTIFIER", "String"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.INSTANCEOF_EXPRESSION


class TestCast:
    """Тесты приведения типов."""
    
    def test_cast_to_class(self, parse, expr_wrapper, make_token):
        """return (String) obj;"""
        tokens = expr_wrapper([
            make_token("SEPARATOR", "("),
            make_token("IDENTIFIER", "String"),
            make_token("SEPARATOR", ")"),
            make_token("IDENTIFIER", "obj"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.CAST_EXPRESSION


class TestObjectCreation:
    """Тесты создания объектов."""
    
    def test_new_object(self, parse, expr_wrapper, make_token):
        """return new ArrayList();"""
        tokens = expr_wrapper([
            make_token("KEYWORD", "new"),
            make_token("IDENTIFIER", "ArrayList"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.OBJECT_CREATION


class TestArrayAccess:
    """Тесты доступа к массивам."""
    
    def test_array_access(self, parse, expr_wrapper, make_token):
        """return arr[0];"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "arr"),
            make_token("SEPARATOR", "["),
            make_token("INT_LITERAL", "0"),
            make_token("SEPARATOR", "]"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.ARRAY_ACCESS
