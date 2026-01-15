"""Тесты парсера для циклов: for, while."""
import pytest
from tests.conftest import make_token


class TestForLoop:
    """Тесты для цикла for."""
    
    @pytest.fixture
    def for_loop_tokens(self):
        """Токены для: for (int i = 1; i <= 10; i++) { ... }"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "ForLoop", 1, 14),
            make_token("SEPARATOR", "{", 1, 22),
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
            # for (int i = 1; i <= 10; i++)
            make_token("KEYWORD", "for", 3, 9),
            make_token("SEPARATOR", "(", 3, 13),
            make_token("KEYWORD", "int", 3, 14),
            make_token("IDENTIFIER", "i", 3, 18),
            make_token("OPERATOR", "=", 3, 20),
            make_token("INT_LITERAL", "1", 3, 22),  # Исправлено!
            make_token("SEPARATOR", ";", 3, 23),
            make_token("IDENTIFIER", "i", 3, 25),
            make_token("OPERATOR", "<=", 3, 27),
            make_token("INT_LITERAL", "10", 3, 30),  # Исправлено!
            make_token("SEPARATOR", ";", 3, 32),
            make_token("IDENTIFIER", "i", 3, 34),
            make_token("OPERATOR", "++", 3, 35),
            make_token("SEPARATOR", ")", 3, 37),
            make_token("SEPARATOR", "{", 3, 39),
            # System.out.println(i);
            make_token("IDENTIFIER", "System", 4, 13),
            make_token("SEPARATOR", ".", 4, 19),
            make_token("IDENTIFIER", "out", 4, 20),
            make_token("SEPARATOR", ".", 4, 23),
            make_token("IDENTIFIER", "println", 4, 24),
            make_token("SEPARATOR", "(", 4, 31),
            make_token("IDENTIFIER", "i", 4, 32),
            make_token("SEPARATOR", ")", 4, 33),
            make_token("SEPARATOR", ";", 4, 34),
            make_token("SEPARATOR", "}", 5, 9),
            make_token("SEPARATOR", "}", 6, 5),
            make_token("SEPARATOR", "}", 7, 1),
        ]
    
    def test_for_statement_exists(self, parse, for_loop_tokens):
        """Проверяет наличие ForStatement."""
        ast = parse(for_loop_tokens)
        method = ast.classes[0].methods[0]
        statements = method.body.statements
        assert len(statements) >= 1
        
        for_stmt = statements[0]
        assert for_stmt.node_type.value == "ForStatement"
    
    def test_for_init_variable(self, parse, for_loop_tokens):
        """Проверяет инициализацию: int i = 1."""
        ast = parse(for_loop_tokens)
        for_stmt = ast.classes[0].methods[0].body.statements[0]
        
        # Инициализация в children[0]
        init = for_stmt.children[0]
        assert init.node_type.value == "VariableDeclaration"
        assert init.name == "i"
    
    def test_for_condition(self, parse, for_loop_tokens):
        """Проверяет условие: i <= 10."""
        ast = parse(for_loop_tokens)
        for_stmt = ast.classes[0].methods[0].body.statements[0]
        
        # Условие в children[1]
        condition = for_stmt.children[1]
        assert condition.node_type.value == "BinaryOperation"
        assert condition.operator == "<="
        assert condition.left is not None
        assert condition.left.name == "i"
        assert condition.right is not None
        assert condition.right.value == "10"
    
    def test_for_update(self, parse, for_loop_tokens):
        """Проверяет обновление: i++."""
        ast = parse(for_loop_tokens)
        for_stmt = ast.classes[0].methods[0].body.statements[0]
        
        # Обновление в children[2]
        update = for_stmt.children[2]
        assert update.node_type.value == "UnaryOperation"
        assert update.operator == "++"
        assert update.operand is not None
        assert update.operand.name == "i"
        assert update.is_postfix == True
    
    def test_for_body(self, parse, for_loop_tokens):
        """Проверяет тело цикла."""
        ast = parse(for_loop_tokens)
        for_stmt = ast.classes[0].methods[0].body.statements[0]
        
        # Тело в children[3]
        body = for_stmt.children[3]
        assert body.node_type.value == "Block"
        assert len(body.statements) >= 1


class TestWhileLoop:
    """Тесты для цикла while."""
    
    @pytest.fixture
    def while_loop_tokens(self):
        """Токены для: while (count < 5) { count++; }"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "WhileLoop", 1, 14),
            make_token("SEPARATOR", "{", 1, 24),
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
            # int count = 0;
            make_token("KEYWORD", "int", 3, 9),
            make_token("IDENTIFIER", "count", 3, 13),
            make_token("OPERATOR", "=", 3, 19),
            make_token("INT_LITERAL", "0", 3, 21),  # Исправлено!
            make_token("SEPARATOR", ";", 3, 22),
            # while (count < 5)
            make_token("KEYWORD", "while", 4, 9),
            make_token("SEPARATOR", "(", 4, 15),
            make_token("IDENTIFIER", "count", 4, 16),
            make_token("OPERATOR", "<", 4, 22),
            make_token("INT_LITERAL", "5", 4, 24),  # Исправлено!
            make_token("SEPARATOR", ")", 4, 25),
            make_token("SEPARATOR", "{", 4, 27),
            # count++;
            make_token("IDENTIFIER", "count", 5, 13),
            make_token("OPERATOR", "++", 5, 18),
            make_token("SEPARATOR", ";", 5, 20),
            make_token("SEPARATOR", "}", 6, 9),
            make_token("SEPARATOR", "}", 7, 5),
            make_token("SEPARATOR", "}", 8, 1),
        ]
    
    def test_while_statement_exists(self, parse, while_loop_tokens):
        """Проверяет наличие WhileStatement."""
        ast = parse(while_loop_tokens)
        statements = ast.classes[0].methods[0].body.statements
        
        # Первый - VariableDeclaration, второй - WhileStatement
        while_stmt = statements[1]
        assert while_stmt.node_type.value == "WhileStatement"
    
    def test_while_condition(self, parse, while_loop_tokens):
        """Проверяет условие: count < 5."""
        ast = parse(while_loop_tokens)
        while_stmt = ast.classes[0].methods[0].body.statements[1]
        
        # Условие в children[0]
        condition = while_stmt.children[0]
        assert condition.node_type.value == "BinaryOperation"
        assert condition.operator == "<"
        assert condition.left.name == "count"
        assert condition.right.value == "5"
    
    def test_while_body(self, parse, while_loop_tokens):
        """Проверяет тело while."""
        ast = parse(while_loop_tokens)
        while_stmt = ast.classes[0].methods[0].body.statements[1]
        
        # Тело в children[1]
        body = while_stmt.children[1]
        assert body.node_type.value == "Block"
