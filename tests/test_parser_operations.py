"""Тесты парсера для операций: арифметические, логические, унарные."""
import pytest
from tests.conftest import make_token


class TestBinaryOperations:
    """Тесты бинарных операций."""
    
    @pytest.fixture
    def arithmetic_tokens(self):
        """Токены для: int result = a + b * 2;"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "Calc", 1, 14),
            make_token("SEPARATOR", "{", 1, 19),
            make_token("KEYWORD", "public", 2, 5),
            make_token("KEYWORD", "static", 2, 12),
            make_token("KEYWORD", "void", 2, 19),
            make_token("IDENTIFIER", "main", 2, 24),
            make_token("SEPARATOR", "(", 2, 28),
            make_token("IDENTIFIER", "String", 2, 29),
            make_token("SEPARATOR", "[", 2, 35),
            make_token("SEPARATOR", "]", 2, 36),
            make_token("IDENTIFIER", "args", 2, 38),
            make_token("SEPARATOR", ")", 2, 42),
            make_token("SEPARATOR", "{", 2, 44),
            # int a = 10;
            make_token("KEYWORD", "int", 3, 9),
            make_token("IDENTIFIER", "a", 3, 13),
            make_token("OPERATOR", "=", 3, 15),
            make_token("INT_LITERAL", "10", 3, 17),
            make_token("SEPARATOR", ";", 3, 19),
            # int b = 3;
            make_token("KEYWORD", "int", 4, 9),
            make_token("IDENTIFIER", "b", 4, 13),
            make_token("OPERATOR", "=", 4, 15),
            make_token("INT_LITERAL", "3", 4, 17),
            make_token("SEPARATOR", ";", 4, 18),
            # int result = a + b * 2;
            make_token("KEYWORD", "int", 5, 9),
            make_token("IDENTIFIER", "result", 5, 13),
            make_token("OPERATOR", "=", 5, 20),
            make_token("IDENTIFIER", "a", 5, 22),
            make_token("OPERATOR", "+", 5, 24),
            make_token("IDENTIFIER", "b", 5, 26),
            make_token("OPERATOR", "*", 5, 28),
            make_token("INT_LITERAL", "2", 5, 30),
            make_token("SEPARATOR", ";", 5, 31),
            make_token("SEPARATOR", "}", 6, 5),
            make_token("SEPARATOR", "}", 7, 1),
        ]
    
    def test_addition_operator(self, parse, arithmetic_tokens):
        """Проверяет оператор +."""
        ast = parse(arithmetic_tokens)
        statements = ast.classes[0].methods[0].body.statements
        
        # int result = a + b * 2; (третий statement)
        result_decl = statements[2]
        assert result_decl.value is not None
        
        # Корень выражения - это + (из-за приоритета)
        expr = result_decl.value
        assert expr.node_type.value == "BinaryOperation"
        assert expr.operator == "+"
    
    def test_operator_precedence(self, parse, arithmetic_tokens):
        """Проверяет приоритет: * перед +."""
        ast = parse(arithmetic_tokens)
        result_decl = ast.classes[0].methods[0].body.statements[2]
        
        # a + (b * 2)
        expr = result_decl.value
        assert expr.operator == "+"
        assert expr.left.name == "a"  # левый операнд - a
        
        # правый операнд - b * 2
        right = expr.right
        assert right.node_type.value == "BinaryOperation"
        assert right.operator == "*"
        assert right.left.name == "b"
        assert right.right.value == "2"


class TestUnaryOperations:
    """Тесты унарных операций."""
    
    @pytest.fixture
    def unary_tokens(self):
        """Токены для: i++; --i;"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "Unary", 1, 14),
            make_token("SEPARATOR", "{", 1, 20),
            make_token("KEYWORD", "public", 2, 5),
            make_token("KEYWORD", "static", 2, 12),
            make_token("KEYWORD", "void", 2, 19),
            make_token("IDENTIFIER", "main", 2, 24),
            make_token("SEPARATOR", "(", 2, 28),
            make_token("IDENTIFIER", "String", 2, 29),
            make_token("SEPARATOR", "[", 2, 35),
            make_token("SEPARATOR", "]", 2, 36),
            make_token("IDENTIFIER", "args", 2, 38),
            make_token("SEPARATOR", ")", 2, 42),
            make_token("SEPARATOR", "{", 2, 44),
            # int i = 0;
            make_token("KEYWORD", "int", 3, 9),
            make_token("IDENTIFIER", "i", 3, 13),
            make_token("OPERATOR", "=", 3, 15),
            make_token("INT_LITERAL", "0", 3, 17),
            make_token("SEPARATOR", ";", 3, 18),
            # i++;
            make_token("IDENTIFIER", "i", 4, 9),
            make_token("OPERATOR", "++", 4, 10),
            make_token("SEPARATOR", ";", 4, 12),
            # --i;
            make_token("OPERATOR", "--", 5, 9),
            make_token("IDENTIFIER", "i", 5, 11),
            make_token("SEPARATOR", ";", 5, 12),
            make_token("SEPARATOR", "}", 6, 5),
            make_token("SEPARATOR", "}", 7, 1),
        ]
    
    def test_postfix_increment(self, parse, unary_tokens):
        """Проверяет постфиксный i++."""
        ast = parse(unary_tokens)
        statements = ast.classes[0].methods[0].body.statements
        
        # i++; это ExpressionStatement с UnaryOperation внутри
        expr_stmt = statements[1]  # После int i = 0;
        
        # Берём expression из statement
        if hasattr(expr_stmt, 'children') and expr_stmt.children:
            unary = expr_stmt.children[0]
        else:
            unary = expr_stmt
        
        assert unary.node_type.value == "UnaryOperation"
        assert unary.operator == "++"
        assert unary.is_postfix == True
        assert unary.operand.name == "i"
    
    def test_prefix_decrement(self, parse, unary_tokens):
        """Проверяет префиксный --i."""
        ast = parse(unary_tokens)
        statements = ast.classes[0].methods[0].body.statements
        
        expr_stmt = statements[2]
        
        if hasattr(expr_stmt, 'children') and expr_stmt.children:
            unary = expr_stmt.children[0]
        else:
            unary = expr_stmt
        
        assert unary.node_type.value == "UnaryOperation"
        assert unary.operator == "--"
        assert unary.is_postfix == False
        assert unary.operand.name == "i"


class TestLogicalOperations:
    """Тесты логических операций."""
    
    @pytest.fixture
    def logical_tokens(self):
        """Токены для: boolean c = a && b;"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "Logic", 1, 14),
            make_token("SEPARATOR", "{", 1, 20),
            make_token("KEYWORD", "public", 2, 5),
            make_token("KEYWORD", "static", 2, 12),
            make_token("KEYWORD", "void", 2, 19),
            make_token("IDENTIFIER", "main", 2, 24),
            make_token("SEPARATOR", "(", 2, 28),
            make_token("IDENTIFIER", "String", 2, 29),
            make_token("SEPARATOR", "[", 2, 35),
            make_token("SEPARATOR", "]", 2, 36),
            make_token("IDENTIFIER", "args", 2, 38),
            make_token("SEPARATOR", ")", 2, 42),
            make_token("SEPARATOR", "{", 2, 44),
            # boolean a = true;
            make_token("KEYWORD", "boolean", 3, 9),
            make_token("IDENTIFIER", "a", 3, 17),
            make_token("OPERATOR", "=", 3, 19),
            make_token("KEYWORD", "true", 3, 21),
            make_token("SEPARATOR", ";", 3, 25),
            # boolean b = false;
            make_token("KEYWORD", "boolean", 4, 9),
            make_token("IDENTIFIER", "b", 4, 17),
            make_token("OPERATOR", "=", 4, 19),
            make_token("KEYWORD", "false", 4, 21),
            make_token("SEPARATOR", ";", 4, 26),
            # boolean c = a && b;
            make_token("KEYWORD", "boolean", 5, 9),
            make_token("IDENTIFIER", "c", 5, 17),
            make_token("OPERATOR", "=", 5, 19),
            make_token("IDENTIFIER", "a", 5, 21),
            make_token("OPERATOR", "&&", 5, 23),
            make_token("IDENTIFIER", "b", 5, 26),
            make_token("SEPARATOR", ";", 5, 27),
            make_token("SEPARATOR", "}", 6, 5),
            make_token("SEPARATOR", "}", 7, 1),
        ]
    
    def test_and_operator(self, parse, logical_tokens):
        """Проверяет оператор &&."""
        ast = parse(logical_tokens)
        statements = ast.classes[0].methods[0].body.statements
        
        # boolean c = a && b;
        c_decl = statements[2]
        expr = c_decl.value
        
        assert expr.node_type.value == "BinaryOperation"
        assert expr.operator == "&&"
        assert expr.left.name == "a"
        assert expr.right.name == "b"
