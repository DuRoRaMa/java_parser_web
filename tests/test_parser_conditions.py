"""Тесты парсера для условных конструкций: if, if-else."""
import pytest
from tests.conftest import make_token


class TestIfStatement:
    """Тесты для if без else."""
    
    @pytest.fixture
    def if_tokens(self):
        """Токены для: if (x > 5) { ... }"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "IfTest", 1, 14),
            make_token("SEPARATOR", "{", 1, 21),
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
            # int x = 10;
            make_token("KEYWORD", "int", 3, 9),
            make_token("IDENTIFIER", "x", 3, 13),
            make_token("OPERATOR", "=", 3, 15),
            make_token("INTEGER", "10", 3, 17),
            make_token("SEPARATOR", ";", 3, 19),
            # if (x > 5)
            make_token("KEYWORD", "if", 4, 9),
            make_token("SEPARATOR", "(", 4, 12),
            make_token("IDENTIFIER", "x", 4, 13),
            make_token("OPERATOR", ">", 4, 15),
            make_token("INTEGER", "5", 4, 17),
            make_token("SEPARATOR", ")", 4, 18),
            make_token("SEPARATOR", "{", 4, 20),
            # System.out.println("Big");
            make_token("IDENTIFIER", "System", 5, 13),
            make_token("SEPARATOR", ".", 5, 19),
            make_token("IDENTIFIER", "out", 5, 20),
            make_token("SEPARATOR", ".", 5, 23),
            make_token("IDENTIFIER", "println", 5, 24),
            make_token("SEPARATOR", "(", 5, 31),
            make_token("STRING", '"Big"', 5, 32),
            make_token("SEPARATOR", ")", 5, 37),
            make_token("SEPARATOR", ";", 5, 38),
            make_token("SEPARATOR", "}", 6, 9),
            make_token("SEPARATOR", "}", 7, 5),
            make_token("SEPARATOR", "}", 8, 1),
        ]
    
    def test_if_statement_exists(self, parse, if_tokens):
        """Проверяет наличие IfStatement."""
        ast = parse(if_tokens)
        statements = ast.classes[0].methods[0].body.statements
        
        if_stmt = statements[1]  # После int x = 10;
        assert if_stmt.node_type.value == "IfStatement"
    
    def test_if_condition(self, parse, if_tokens):
        """Проверяет условие: x > 5."""
        ast = parse(if_tokens)
        if_stmt = ast.classes[0].methods[0].body.statements[1]
        
        condition = if_stmt.children[0]
        assert condition.node_type.value == "BinaryOperation"
        assert condition.operator == ">"
        assert condition.left.name == "x"
        assert condition.right.value == "5"
    
    def test_if_then_block(self, parse, if_tokens):
        """Проверяет then-блок."""
        ast = parse(if_tokens)
        if_stmt = ast.classes[0].methods[0].body.statements[1]
        
        then_block = if_stmt.children[1]
        assert then_block.node_type.value == "Block"
        assert len(then_block.statements) >= 1


class TestIfElseStatement:
    """Тесты для if-else."""
    
    @pytest.fixture
    def if_else_tokens(self):
        """Токены для: if (x > 5) { ... } else { ... }"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "IfElse", 1, 14),
            make_token("SEPARATOR", "{", 1, 21),
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
            # int x = 10;
            make_token("KEYWORD", "int", 3, 9),
            make_token("IDENTIFIER", "x", 3, 13),
            make_token("OPERATOR", "=", 3, 15),
            make_token("INTEGER", "10", 3, 17),
            make_token("SEPARATOR", ";", 3, 19),
            # if (x > 5)
            make_token("KEYWORD", "if", 4, 9),
            make_token("SEPARATOR", "(", 4, 12),
            make_token("IDENTIFIER", "x", 4, 13),
            make_token("OPERATOR", ">", 4, 15),
            make_token("INTEGER", "5", 4, 17),
            make_token("SEPARATOR", ")", 4, 18),
            make_token("SEPARATOR", "{", 4, 20),
            make_token("IDENTIFIER", "System", 5, 13),
            make_token("SEPARATOR", ".", 5, 19),
            make_token("IDENTIFIER", "out", 5, 20),
            make_token("SEPARATOR", ".", 5, 23),
            make_token("IDENTIFIER", "println", 5, 24),
            make_token("SEPARATOR", "(", 5, 31),
            make_token("STRING", '"Big"', 5, 32),
            make_token("SEPARATOR", ")", 5, 37),
            make_token("SEPARATOR", ";", 5, 38),
            make_token("SEPARATOR", "}", 6, 9),
            # else
            make_token("KEYWORD", "else", 6, 11),
            make_token("SEPARATOR", "{", 6, 16),
            make_token("IDENTIFIER", "System", 7, 13),
            make_token("SEPARATOR", ".", 7, 19),
            make_token("IDENTIFIER", "out", 7, 20),
            make_token("SEPARATOR", ".", 7, 23),
            make_token("IDENTIFIER", "println", 7, 24),
            make_token("SEPARATOR", "(", 7, 31),
            make_token("STRING", '"Small"', 7, 32),
            make_token("SEPARATOR", ")", 7, 39),
            make_token("SEPARATOR", ";", 7, 40),
            make_token("SEPARATOR", "}", 8, 9),
            make_token("SEPARATOR", "}", 9, 5),
            make_token("SEPARATOR", "}", 10, 1),
        ]
    
    def test_if_else_has_else_block(self, parse, if_else_tokens):
        """Проверяет наличие else-блока."""
        ast = parse(if_else_tokens)
        if_stmt = ast.classes[0].methods[0].body.statements[1]
        
        # if имеет 3 children: condition, then, else
        assert len(if_stmt.children) >= 3
        
        else_block = if_stmt.children[2]
        assert else_block.node_type.value == "Block"
