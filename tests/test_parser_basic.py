"""Базовые тесты парсера: Hello World, простые классы."""
import pytest
from tests.conftest import make_token


class TestHelloWorld:
    """Тесты для простого Hello World."""
    
    @pytest.fixture
    def hello_world_tokens(self):
        """Токены для: public class HelloWorld { public static void main(String[] args) { System.out.println("Hello"); } }"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "HelloWorld", 1, 14),
            make_token("SEPARATOR", "{", 1, 25),
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
            make_token("IDENTIFIER", "System", 3, 9),
            make_token("SEPARATOR", ".", 3, 15),
            make_token("IDENTIFIER", "out", 3, 16),
            make_token("SEPARATOR", ".", 3, 19),
            make_token("IDENTIFIER", "println", 3, 20),
            make_token("SEPARATOR", "(", 3, 27),
            make_token("STRING_LITERAL", "Hello, World!", 3, 28),  # Исправлено!
            make_token("SEPARATOR", ")", 3, 43),
            make_token("SEPARATOR", ";", 3, 44),
            make_token("SEPARATOR", "}", 4, 5),
            make_token("SEPARATOR", "}", 5, 1),
        ]
    
    def test_program_parsed(self, parse, hello_world_tokens):
        """Проверяет что парсер возвращает Program."""
        ast = parse(hello_world_tokens)
        assert ast is not None
        assert ast.node_type.value == "Program"
    
    def test_class_name(self, parse, hello_world_tokens):
        """Проверяет имя класса."""
        ast = parse(hello_world_tokens)
        assert len(ast.classes) == 1
        assert ast.classes[0].name == "HelloWorld"
    
    def test_class_is_public(self, parse, hello_world_tokens):
        """Проверяет модификатор public."""
        ast = parse(hello_world_tokens)
        assert "public" in ast.classes[0].modifiers
    
    def test_main_method_exists(self, parse, hello_world_tokens):
        """Проверяет наличие метода main."""
        ast = parse(hello_world_tokens)
        cls = ast.classes[0]
        assert len(cls.methods) == 1
        assert cls.methods[0].name == "main"
    
    def test_main_method_modifiers(self, parse, hello_world_tokens):
        """Проверяет модификаторы метода main."""
        ast = parse(hello_world_tokens)
        method = ast.classes[0].methods[0]
        assert "public" in method.modifiers
        assert "static" in method.modifiers
    
    def test_main_method_return_type(self, parse, hello_world_tokens):
        """Проверяет тип возврата void."""
        ast = parse(hello_world_tokens)
        method = ast.classes[0].methods[0]
        assert method.return_type is not None
        assert method.return_type.name == "void"
    
    def test_main_method_parameters(self, parse, hello_world_tokens):
        """Проверяет параметр String[] args."""
        ast = parse(hello_world_tokens)
        method = ast.classes[0].methods[0]
        assert len(method.parameters) == 1
        param = method.parameters[0]
        assert param.name == "args"
        assert param.param_type.name == "String"
        assert param.param_type.is_array == True
    
    def test_method_has_body(self, parse, hello_world_tokens):
        """Проверяет что метод имеет тело."""
        ast = parse(hello_world_tokens)
        method = ast.classes[0].methods[0]
        assert method.body is not None
        assert method.body.node_type.value == "Block"


class TestEmptyClass:
    """Тесты для пустого класса."""
    
    @pytest.fixture
    def empty_class_tokens(self):
        """Токены для: public class Empty { }"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "Empty", 1, 14),
            make_token("SEPARATOR", "{", 1, 20),
            make_token("SEPARATOR", "}", 1, 21),
        ]
    
    def test_empty_class_parsed(self, parse, empty_class_tokens):
        """Парсит пустой класс."""
        ast = parse(empty_class_tokens)
        assert ast is not None
        assert len(ast.classes) == 1
        assert ast.classes[0].name == "Empty"
    
    def test_empty_class_no_methods(self, parse, empty_class_tokens):
        """Пустой класс не имеет методов."""
        ast = parse(empty_class_tokens)
        assert len(ast.classes[0].methods) == 0
    
    def test_empty_class_no_fields(self, parse, empty_class_tokens):
        """Пустой класс не имеет полей."""
        ast = parse(empty_class_tokens)
        assert len(ast.classes[0].fields) == 0
