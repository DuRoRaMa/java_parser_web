"""Тесты парсера для классов: поля, методы, модификаторы."""
import pytest
from tests.conftest import make_token


class TestClassWithFields:
    """Тесты для класса с полями."""
    
    @pytest.fixture
    def class_with_fields_tokens(self):
        """Токены для класса с полями."""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "Person", 1, 14),
            make_token("SEPARATOR", "{", 1, 21),
            # private String name;
            make_token("KEYWORD", "private", 2, 5),
            make_token("IDENTIFIER", "String", 2, 13),
            make_token("IDENTIFIER", "name", 2, 20),
            make_token("SEPARATOR", ";", 2, 24),
            # private int age;
            make_token("KEYWORD", "private", 3, 5),
            make_token("KEYWORD", "int", 3, 13),
            make_token("IDENTIFIER", "age", 3, 17),
            make_token("SEPARATOR", ";", 3, 20),
            # public static final int MAX_AGE = 150;
            make_token("KEYWORD", "public", 4, 5),
            make_token("KEYWORD", "static", 4, 12),
            make_token("KEYWORD", "final", 4, 19),
            make_token("KEYWORD", "int", 4, 25),
            make_token("IDENTIFIER", "MAX_AGE", 4, 29),
            make_token("OPERATOR", "=", 4, 37),
            make_token("INT_LITERAL", "150", 4, 39),  # <-- ИСПРАВЛЕНО
            make_token("SEPARATOR", ";", 4, 42),
            make_token("SEPARATOR", "}", 5, 1),
        ]
    
    def test_class_has_fields(self, parse, class_with_fields_tokens):
        """Проверяет наличие полей."""
        ast = parse(class_with_fields_tokens)
        cls = ast.classes[0]
        assert len(cls.fields) == 3
    
    def test_field_name(self, parse, class_with_fields_tokens):
        """Проверяет имя поля."""
        ast = parse(class_with_fields_tokens)
        fields = ast.classes[0].fields
        
        assert fields[0].name == "name"
        assert fields[1].name == "age"
        assert fields[2].name == "MAX_AGE"
    
    def test_field_type(self, parse, class_with_fields_tokens):
        """Проверяет тип поля."""
        ast = parse(class_with_fields_tokens)
        fields = ast.classes[0].fields
        
        assert fields[0].field_type.name == "String"
        assert fields[1].field_type.name == "int"
    
    def test_field_modifiers(self, parse, class_with_fields_tokens):
        """Проверяет модификаторы полей."""
        ast = parse(class_with_fields_tokens)
        fields = ast.classes[0].fields
        
        assert "private" in fields[0].modifiers
        assert "private" in fields[1].modifiers
        assert "public" in fields[2].modifiers
        assert "static" in fields[2].modifiers
        assert "final" in fields[2].modifiers
    
    def test_field_with_value(self, parse, class_with_fields_tokens):
        """Проверяет поле с начальным значением."""
        ast = parse(class_with_fields_tokens)
        max_age = ast.classes[0].fields[2]
        
        assert max_age.value is not None
        assert max_age.value.value == "150"


class TestClassWithMethods:
    """Тесты для класса с методами."""
    
    @pytest.fixture
    def class_with_methods_tokens(self):
        """Токены для класса с getter и setter."""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "Person", 1, 14),
            make_token("SEPARATOR", "{", 1, 21),
            # private String name;
            make_token("KEYWORD", "private", 2, 5),
            make_token("IDENTIFIER", "String", 2, 13),
            make_token("IDENTIFIER", "name", 2, 20),
            make_token("SEPARATOR", ";", 2, 24),
            # public String getName() { return name; }
            make_token("KEYWORD", "public", 4, 5),
            make_token("IDENTIFIER", "String", 4, 12),
            make_token("IDENTIFIER", "getName", 4, 19),
            make_token("SEPARATOR", "(", 4, 26),
            make_token("SEPARATOR", ")", 4, 27),
            make_token("SEPARATOR", "{", 4, 29),
            make_token("KEYWORD", "return", 5, 9),
            make_token("IDENTIFIER", "name", 5, 16),
            make_token("SEPARATOR", ";", 5, 20),
            make_token("SEPARATOR", "}", 6, 5),
            # public void setName(String name) { this.name = name; }
            make_token("KEYWORD", "public", 8, 5),
            make_token("KEYWORD", "void", 8, 12),
            make_token("IDENTIFIER", "setName", 8, 17),
            make_token("SEPARATOR", "(", 8, 24),
            make_token("IDENTIFIER", "String", 8, 25),
            make_token("IDENTIFIER", "name", 8, 32),
            make_token("SEPARATOR", ")", 8, 36),
            make_token("SEPARATOR", "{", 8, 38),
            make_token("KEYWORD", "this", 9, 9),
            make_token("SEPARATOR", ".", 9, 13),
            make_token("IDENTIFIER", "name", 9, 14),
            make_token("OPERATOR", "=", 9, 19),
            make_token("IDENTIFIER", "name", 9, 21),
            make_token("SEPARATOR", ";", 9, 25),
            make_token("SEPARATOR", "}", 10, 5),
            # public int calculate(int a, int b) { return a + b; }
            make_token("KEYWORD", "public", 12, 5),
            make_token("KEYWORD", "int", 12, 12),
            make_token("IDENTIFIER", "calculate", 12, 16),
            make_token("SEPARATOR", "(", 12, 25),
            make_token("KEYWORD", "int", 12, 26),
            make_token("IDENTIFIER", "a", 12, 30),
            make_token("SEPARATOR", ",", 12, 31),
            make_token("KEYWORD", "int", 12, 33),
            make_token("IDENTIFIER", "b", 12, 37),
            make_token("SEPARATOR", ")", 12, 38),
            make_token("SEPARATOR", "{", 12, 40),
            make_token("KEYWORD", "return", 13, 9),
            make_token("IDENTIFIER", "a", 13, 16),
            make_token("OPERATOR", "+", 13, 18),
            make_token("IDENTIFIER", "b", 13, 20),
            make_token("SEPARATOR", ";", 13, 21),
            make_token("SEPARATOR", "}", 14, 5),
            make_token("SEPARATOR", "}", 15, 1),
        ]
    
    def test_class_has_methods(self, parse, class_with_methods_tokens):
        """Проверяет наличие методов."""
        ast = parse(class_with_methods_tokens)
        cls = ast.classes[0]
        assert len(cls.methods) == 3
    
    def test_getter_method(self, parse, class_with_methods_tokens):
        """Проверяет getter метод."""
        ast = parse(class_with_methods_tokens)
        methods = ast.classes[0].methods
        
        getter = methods[0]
        assert getter.name == "getName"
        assert getter.return_type.name == "String"
        assert len(getter.parameters) == 0
        assert "public" in getter.modifiers
    
    def test_setter_method(self, parse, class_with_methods_tokens):
        """Проверяет setter метод."""
        ast = parse(class_with_methods_tokens)
        methods = ast.classes[0].methods
        
        setter = methods[1]
        assert setter.name == "setName"
        assert setter.return_type.name == "void"
        assert len(setter.parameters) == 1
        assert setter.parameters[0].name == "name"
        assert setter.parameters[0].param_type.name == "String"
    
    def test_method_with_multiple_params(self, parse, class_with_methods_tokens):
        """Проверяет метод с несколькими параметрами."""
        ast = parse(class_with_methods_tokens)
        methods = ast.classes[0].methods
        
        calc = methods[2]
        assert calc.name == "calculate"
        assert len(calc.parameters) == 2
        assert calc.parameters[0].name == "a"
        assert calc.parameters[0].param_type.name == "int"
        assert calc.parameters[1].name == "b"
        assert calc.parameters[1].param_type.name == "int"
    
    def test_method_return_statement(self, parse, class_with_methods_tokens):
        """Проверяет return statement в методе."""
        ast = parse(class_with_methods_tokens)
        getter = ast.classes[0].methods[0]
        
        assert getter.body is not None
        assert len(getter.body.statements) >= 1
        
        return_stmt = getter.body.statements[0]
        assert return_stmt.node_type.value == "ReturnStatement"
    
    def test_method_return_expression(self, parse, class_with_methods_tokens):
        """Проверяет выражение в return a + b."""
        ast = parse(class_with_methods_tokens)
        calc = ast.classes[0].methods[2]
        
        return_stmt = calc.body.statements[0]
        # return a + b; - должен быть BinaryOperation в children
        assert len(return_stmt.children) >= 1
        
        expr = return_stmt.children[0]
        assert expr.node_type.value == "BinaryOperation"
        assert expr.operator == "+"


class TestClassModifiers:
    """Тесты для модификаторов класса."""
    
    @pytest.fixture
    def abstract_class_tokens(self):
        """Токены для: public abstract class Animal { }"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "abstract", 1, 8),
            make_token("KEYWORD", "class", 1, 17),
            make_token("IDENTIFIER", "Animal", 1, 23),
            make_token("SEPARATOR", "{", 1, 30),
            make_token("SEPARATOR", "}", 1, 31),
        ]
    
    @pytest.fixture
    def final_class_tokens(self):
        """Токены для: public final class Constants { }"""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "final", 1, 8),
            make_token("KEYWORD", "class", 1, 14),
            make_token("IDENTIFIER", "Constants", 1, 20),
            make_token("SEPARATOR", "{", 1, 30),
            make_token("SEPARATOR", "}", 1, 31),
        ]
    
    def test_abstract_modifier(self, parse, abstract_class_tokens):
        """Проверяет модификатор abstract."""
        ast = parse(abstract_class_tokens)
        cls = ast.classes[0]
        
        assert "public" in cls.modifiers
        assert "abstract" in cls.modifiers
    
    def test_final_modifier(self, parse, final_class_tokens):
        """Проверяет модификатор final."""
        ast = parse(final_class_tokens)
        cls = ast.classes[0]
        
        assert "public" in cls.modifiers
        assert "final" in cls.modifiers


class TestMethodModifiers:
    """Тесты для модификаторов методов."""
    
    @pytest.fixture
    def static_method_tokens(self):
        """Токены для статического метода."""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "Utils", 1, 14),
            make_token("SEPARATOR", "{", 1, 20),
            # public static int add(int a, int b) { return a + b; }
            make_token("KEYWORD", "public", 2, 5),
            make_token("KEYWORD", "static", 2, 12),
            make_token("KEYWORD", "int", 2, 19),
            make_token("IDENTIFIER", "add", 2, 23),
            make_token("SEPARATOR", "(", 2, 26),
            make_token("KEYWORD", "int", 2, 27),
            make_token("IDENTIFIER", "a", 2, 31),
            make_token("SEPARATOR", ",", 2, 32),
            make_token("KEYWORD", "int", 2, 34),
            make_token("IDENTIFIER", "b", 2, 38),
            make_token("SEPARATOR", ")", 2, 39),
            make_token("SEPARATOR", "{", 2, 41),
            make_token("KEYWORD", "return", 3, 9),
            make_token("IDENTIFIER", "a", 3, 16),
            make_token("OPERATOR", "+", 3, 18),
            make_token("IDENTIFIER", "b", 3, 20),
            make_token("SEPARATOR", ";", 3, 21),
            make_token("SEPARATOR", "}", 4, 5),
            # private final void helper() { }
            make_token("KEYWORD", "private", 6, 5),
            make_token("KEYWORD", "final", 6, 13),
            make_token("KEYWORD", "void", 6, 19),
            make_token("IDENTIFIER", "helper", 6, 24),
            make_token("SEPARATOR", "(", 6, 30),
            make_token("SEPARATOR", ")", 6, 31),
            make_token("SEPARATOR", "{", 6, 33),
            make_token("SEPARATOR", "}", 6, 34),
            make_token("SEPARATOR", "}", 7, 1),
        ]
    
    def test_static_method(self, parse, static_method_tokens):
        """Проверяет статический метод."""
        ast = parse(static_method_tokens)
        methods = ast.classes[0].methods
        
        add_method = methods[0]
        assert "public" in add_method.modifiers
        assert "static" in add_method.modifiers
    
    def test_private_final_method(self, parse, static_method_tokens):
        """Проверяет private final метод."""
        ast = parse(static_method_tokens)
        methods = ast.classes[0].methods
        
        helper = methods[1]
        assert "private" in helper.modifiers
        assert "final" in helper.modifiers


class TestReturnTypes:
    """Тесты для типов возврата методов."""
    
    @pytest.fixture
    def various_return_types_tokens(self):
        """Токены для методов с разными типами возврата."""
        return [
            make_token("KEYWORD", "public", 1, 1),
            make_token("KEYWORD", "class", 1, 8),
            make_token("IDENTIFIER", "Types", 1, 14),
            make_token("SEPARATOR", "{", 1, 20),
            # void doNothing() { }
            make_token("KEYWORD", "void", 2, 5),
            make_token("IDENTIFIER", "doNothing", 2, 10),
            make_token("SEPARATOR", "(", 2, 19),
            make_token("SEPARATOR", ")", 2, 20),
            make_token("SEPARATOR", "{", 2, 22),
            make_token("SEPARATOR", "}", 2, 23),
            # int getInt() { return 0; }
            make_token("KEYWORD", "int", 3, 5),
            make_token("IDENTIFIER", "getInt", 3, 9),
            make_token("SEPARATOR", "(", 3, 15),
            make_token("SEPARATOR", ")", 3, 16),
            make_token("SEPARATOR", "{", 3, 18),
            make_token("KEYWORD", "return", 3, 20),
            make_token("INT_LITERAL", "0", 3, 27),  # <-- ИСПРАВЛЕНО
            make_token("SEPARATOR", ";", 3, 28),
            make_token("SEPARATOR", "}", 3, 30),
            # String getString() { return ""; }
            make_token("IDENTIFIER", "String", 4, 5),
            make_token("IDENTIFIER", "getString", 4, 12),
            make_token("SEPARATOR", "(", 4, 21),
            make_token("SEPARATOR", ")", 4, 22),
            make_token("SEPARATOR", "{", 4, 24),
            make_token("KEYWORD", "return", 4, 26),
            make_token("STRING_LITERAL", "", 4, 33),  # <-- ИСПРАВЛЕНО
            make_token("SEPARATOR", ";", 4, 35),
            make_token("SEPARATOR", "}", 4, 37),
            # boolean isTrue() { return true; }
            make_token("KEYWORD", "boolean", 5, 5),
            make_token("IDENTIFIER", "isTrue", 5, 13),
            make_token("SEPARATOR", "(", 5, 19),
            make_token("SEPARATOR", ")", 5, 20),
            make_token("SEPARATOR", "{", 5, 22),
            make_token("KEYWORD", "return", 5, 24),
            make_token("KEYWORD", "true", 5, 31),
            make_token("SEPARATOR", ";", 5, 35),
            make_token("SEPARATOR", "}", 5, 37),
            make_token("SEPARATOR", "}", 6, 1),
        ]
    
    def test_void_return_type(self, parse, various_return_types_tokens):
        """Проверяет тип возврата void."""
        ast = parse(various_return_types_tokens)
        method = ast.classes[0].methods[0]
        
        assert method.return_type.name == "void"
    
    def test_int_return_type(self, parse, various_return_types_tokens):
        """Проверяет тип возврата int."""
        ast = parse(various_return_types_tokens)
        method = ast.classes[0].methods[1]
        
        assert method.return_type.name == "int"
    
    def test_string_return_type(self, parse, various_return_types_tokens):
        """Проверяет тип возврата String."""
        ast = parse(various_return_types_tokens)
        method = ast.classes[0].methods[2]
        
        assert method.return_type.name == "String"
    
    def test_boolean_return_type(self, parse, various_return_types_tokens):
        """Проверяет тип возврата boolean."""
        ast = parse(various_return_types_tokens)
        method = ast.classes[0].methods[3]
        
        assert method.return_type.name == "boolean"
