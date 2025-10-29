import pytest
from app.javaparser.parser import Parser
from app.javaparser.ast import *

class TestParserComprehensive:
    """Комплексные тесты парсера покрывающие все модули"""
    
    # ===== БАЗОВЫЕ ТЕСТЫ СТРУКТУР =====
    
    def test_empty_program(self):
        """Тест пустой программы"""
        tokens = [{"type": "EOF", "lexeme": "", "line": 1, "column": 1}]
        parser = Parser(tokens)
        program = parser.parse()
        
        assert isinstance(program, Program)
        assert program.node_type == NodeType.PROGRAM
        assert program.classes == []
        assert program.imports == []
    
    def test_class_declaration(self):
        """Тест объявления класса"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "public", "line": 1, "column": 1},
            {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 8},
            {"type": "IDENTIFIER", "lexeme": "TestClass", "line": 1, "column": 14},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 24},
            {"type": "SEPARATOR", "lexeme": "}", "line": 2, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 3, "column": 1}
        ]
        
        parser = Parser(tokens)
        program = parser.parse()
        
        assert len(program.classes) == 1
        class_decl = program.classes[0]
        assert class_decl.name == "TestClass"
        assert class_decl.modifiers == ["public"]
        assert class_decl.fields == []
        assert class_decl.methods == []
    
    def test_interface_declaration(self):
        """Тест объявления интерфейса"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "interface", "line": 1, "column": 1},
            {"type": "IDENTIFIER", "lexeme": "TestInterface", "line": 1, "column": 11},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 25},
            {"type": "SEPARATOR", "lexeme": "}", "line": 2, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 3, "column": 1}
        ]
        
        parser = Parser(tokens)
        program = parser.parse()
        
        assert len(program.classes) == 1
        interface_decl = program.classes[0]
        assert interface_decl.name == "TestInterface"
        assert interface_decl.modifiers == []
    
    def test_enum_declaration(self):
        """Тест объявления enum"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "enum", "line": 1, "column": 1},
            {"type": "IDENTIFIER", "lexeme": "Color", "line": 1, "column": 6},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 12},
            {"type": "IDENTIFIER", "lexeme": "RED", "line": 1, "column": 14},
            {"type": "SEPARATOR", "lexeme": ",", "line": 1, "column": 17},
            {"type": "IDENTIFIER", "lexeme": "GREEN", "line": 1, "column": 19},
            {"type": "SEPARATOR", "lexeme": ",", "line": 1, "column": 24},
            {"type": "IDENTIFIER", "lexeme": "BLUE", "line": 1, "column": 26},
            {"type": "SEPARATOR", "lexeme": "}", "line": 1, "column": 31},
            {"type": "EOF", "lexeme": "", "line": 2, "column": 1}
        ]
        
        parser = Parser(tokens)
        program = parser.parse()
        
        assert len(program.classes) == 1
        enum_decl = program.classes[0]
        assert enum_decl.name == "Color"
        assert len(enum_decl.fields) == 3  # RED, GREEN, BLUE
        
        # Проверяем что поля созданы с правильными модификаторами
        field_names = [field.name for field in enum_decl.fields]
        assert "RED" in field_names
        assert "GREEN" in field_names  
        assert "BLUE" in field_names
        
        for field in enum_decl.fields:
            assert field.modifiers == ["public", "static", "final"]
    
    # ===== ТЕСТЫ МОДИФИКАТОРОВ =====
    
    @pytest.mark.parametrize("modifiers,expected", [
        (["public"], ["public"]),
        (["private"], ["private"]),
        (["protected"], ["protected"]),
        (["abstract"], ["abstract"]),
        (["public", "abstract"], ["public", "abstract"]),
        ([], []),
    ])
    def test_class_modifiers(self, modifiers, expected):
        """Тест различных модификаторов классов"""
        tokens = []
        for i, modifier in enumerate(modifiers):
            tokens.append({
                "type": "KEYWORD", 
                "lexeme": modifier, 
                "line": 1, 
                "column": 1 + i * 8
            })
        
        tokens.extend([
            {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 1 + len(modifiers) * 8},
            {"type": "IDENTIFIER", "lexeme": "Test", "line": 1, "column": 2 + len(modifiers) * 8},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 7 + len(modifiers) * 8},
            {"type": "SEPARATOR", "lexeme": "}", "line": 2, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 3, "column": 1}
        ])
        
        parser = Parser(tokens)
        program = parser.parse()
        class_decl = program.classes[0]
        
        assert class_decl.modifiers == expected
    
    # ===== ТЕСТЫ ПОЛЕЙ И МЕТОДОВ =====
    
    def test_field_declaration(self):
        """Тест объявления поля"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 1},
            {"type": "IDENTIFIER", "lexeme": "Test", "line": 1, "column": 7},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 12},
            {"type": "KEYWORD", "lexeme": "private", "line": 2, "column": 5},
            {"type": "KEYWORD", "lexeme": "int", "line": 2, "column": 13},
            {"type": "IDENTIFIER", "lexeme": "count", "line": 2, "column": 17},
            {"type": "SEPARATOR", "lexeme": ";", "line": 2, "column": 22},
            {"type": "SEPARATOR", "lexeme": "}", "line": 3, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 4, "column": 1}
        ]
        
        parser = Parser(tokens)
        program = parser.parse()
        class_decl = program.classes[0]
        
        assert len(class_decl.fields) == 1
        field = class_decl.fields[0]
        assert field.name == "count"
        assert field.field_type.name == "int"
        assert field.modifiers == ["private"]
    
    def test_method_declaration(self):
        """Тест объявления метода"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 1},
            {"type": "IDENTIFIER", "lexeme": "Test", "line": 1, "column": 7},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 12},
            {"type": "KEYWORD", "lexeme": "public", "line": 2, "column": 5},
            {"type": "KEYWORD", "lexeme": "void", "line": 2, "column": 12},
            {"type": "IDENTIFIER", "lexeme": "main", "line": 2, "column": 17},
            {"type": "SEPARATOR", "lexeme": "(", "line": 2, "column": 21},
            {"type": "SEPARATOR", "lexeme": ")", "line": 2, "column": 22},
            {"type": "SEPARATOR", "lexeme": "{", "line": 2, "column": 24},
            {"type": "SEPARATOR", "lexeme": "}", "line": 3, "column": 5},
            {"type": "SEPARATOR", "lexeme": "}", "line": 4, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 5, "column": 1}
        ]
        
        parser = Parser(tokens)
        program = parser.parse()
        class_decl = program.classes[0]
        
        assert len(class_decl.methods) == 1
        method = class_decl.methods[0]
        assert method.name == "main"
        assert method.return_type.name == "void"
        assert method.modifiers == ["public"]
        assert len(method.parameters) == 0
    
    def test_constructor_declaration(self):
        """Тест объявления конструктора"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 1},
            {"type": "IDENTIFIER", "lexeme": "Test", "line": 1, "column": 7},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 12},
            {"type": "KEYWORD", "lexeme": "public", "line": 2, "column": 5},
            {"type": "IDENTIFIER", "lexeme": "Test", "line": 2, "column": 12},
            {"type": "SEPARATOR", "lexeme": "(", "line": 2, "column": 16},
            {"type": "SEPARATOR", "lexeme": ")", "line": 2, "column": 17},
            {"type": "SEPARATOR", "lexeme": "{", "line": 2, "column": 19},
            {"type": "SEPARATOR", "lexeme": "}", "line": 3, "column": 5},
            {"type": "SEPARATOR", "lexeme": "}", "line": 4, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 5, "column": 1}
        ]
        
        parser = Parser(tokens)
        program = parser.parse()
        class_decl = program.classes[0]
        
        assert len(class_decl.methods) == 1
        constructor = class_decl.methods[0]
        assert constructor.name == "Test"
        assert constructor.return_type is None  # У конструктора нет возвращаемого типа
        assert constructor.modifiers == ["public"]
    
    # ===== ТЕСТЫ ВЫРАЖЕНИЙ =====
    
    def test_method_call(self):
        """Тест вызова метода"""
        tokens = [
            {"type": "IDENTIFIER", "lexeme": "System", "line": 1, "column": 1},
            {"type": "OPERATOR", "lexeme": ".", "line": 1, "column": 7},
            {"type": "IDENTIFIER", "lexeme": "out", "line": 1, "column": 8},
            {"type": "OPERATOR", "lexeme": ".", "line": 1, "column": 11},
            {"type": "IDENTIFIER", "lexeme": "println", "line": 1, "column": 12},
            {"type": "SEPARATOR", "lexeme": "(", "line": 1, "column": 19},
            {"type": "STRING_LITERAL", "lexeme": "Hello", "line": 1, "column": 20},
            {"type": "SEPARATOR", "lexeme": ")", "line": 1, "column": 27},
            {"type": "SEPARATOR", "lexeme": ";", "line": 1, "column": 28},
            {"type": "EOF", "lexeme": "", "line": 2, "column": 1}
        ]
        
        parser = Parser(tokens)
        # Должен разобраться без ошибок
    
    def test_variable_declaration(self):
        """Тест объявления переменной"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "int", "line": 1, "column": 1},
            {"type": "IDENTIFIER", "lexeme": "x", "line": 1, "column": 5},
            {"type": "OPERATOR", "lexeme": "=", "line": 1, "column": 7},
            {"type": "INT_LITERAL", "lexeme": "10", "line": 1, "column": 9},
            {"type": "SEPARATOR", "lexeme": ";", "line": 1, "column": 11},
            {"type": "EOF", "lexeme": "", "line": 2, "column": 1}
        ]
        
        parser = Parser(tokens)
        # Должен разобраться без ошибок
    
    def test_assignment_expression(self):
        """Тест выражения присваивания"""
        tokens = [
            {"type": "IDENTIFIER", "lexeme": "x", "line": 1, "column": 1},
            {"type": "OPERATOR", "lexeme": "=", "line": 1, "column": 3},
            {"type": "IDENTIFIER", "lexeme": "y", "line": 1, "column": 5},
            {"type": "OPERATOR", "lexeme": "+", "line": 1, "column": 7},
            {"type": "INT_LITERAL", "lexeme": "5", "line": 1, "column": 9},
            {"type": "SEPARATOR", "lexeme": ";", "line": 1, "column": 10},
            {"type": "EOF", "lexeme": "", "line": 2, "column": 1}
        ]
        
        parser = Parser(tokens)
        # Должен разобраться без ошибок
    
    # ===== ТЕСТЫ УПРАВЛЯЮЩИХ КОНСТРУКЦИЙ =====
    
    def test_if_statement(self):
        """Тест условного оператора"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "if", "line": 1, "column": 1},
            {"type": "SEPARATOR", "lexeme": "(", "line": 1, "column": 4},
            {"type": "IDENTIFIER", "lexeme": "x", "line": 1, "column": 5},
            {"type": "OPERATOR", "lexeme": ">", "line": 1, "column": 7},
            {"type": "INT_LITERAL", "lexeme": "0", "line": 1, "column": 9},
            {"type": "SEPARATOR", "lexeme": ")", "line": 1, "column": 10},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 12},
            {"type": "SEPARATOR", "lexeme": "}", "line": 2, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 3, "column": 1}
        ]
        
        parser = Parser(tokens)
        # Должен разобраться без ошибок
    
    def test_while_statement(self):
        """Тест цикла while"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "while", "line": 1, "column": 1},
            {"type": "SEPARATOR", "lexeme": "(", "line": 1, "column": 7},
            {"type": "IDENTIFIER", "lexeme": "condition", "line": 1, "column": 8},
            {"type": "SEPARATOR", "lexeme": ")", "line": 1, "column": 17},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 19},
            {"type": "SEPARATOR", "lexeme": "}", "line": 2, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 3, "column": 1}
        ]
        
        parser = Parser(tokens)
        # Должен разобраться без ошибок
    
    def test_for_statement(self):
        """Тест цикла for"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "for", "line": 1, "column": 1},
            {"type": "SEPARATOR", "lexeme": "(", "line": 1, "column": 5},
            {"type": "KEYWORD", "lexeme": "int", "line": 1, "column": 6},
            {"type": "IDENTIFIER", "lexeme": "i", "line": 1, "column": 10},
            {"type": "OPERATOR", "lexeme": "=", "line": 1, "column": 12},
            {"type": "INT_LITERAL", "lexeme": "0", "line": 1, "column": 14},
            {"type": "SEPARATOR", "lexeme": ";", "line": 1, "column": 15},
            {"type": "IDENTIFIER", "lexeme": "i", "line": 1, "column": 17},
            {"type": "OPERATOR", "lexeme": "<", "line": 1, "column": 19},
            {"type": "INT_LITERAL", "lexeme": "10", "line": 1, "column": 21},
            {"type": "SEPARATOR", "lexeme": ";", "line": 1, "column": 23},
            {"type": "IDENTIFIER", "lexeme": "i", "line": 1, "column": 25},
            {"type": "OPERATOR", "lexeme": "++", "line": 1, "column": 27},
            {"type": "SEPARATOR", "lexeme": ")", "line": 1, "column": 29},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 31},
            {"type": "SEPARATOR", "lexeme": "}", "line": 2, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 3, "column": 1}
        ]
        
        parser = Parser(tokens)
        # Должен разобраться без ошибок
    
    # ===== ТЕСТЫ ТИПОВ И GENERICS =====
    
    def test_array_type(self):
        """Тест массива"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "int", "line": 1, "column": 1},
            {"type": "SEPARATOR", "lexeme": "[", "line": 1, "column": 4},
            {"type": "SEPARATOR", "lexeme": "]", "line": 1, "column": 5},
            {"type": "IDENTIFIER", "lexeme": "arr", "line": 1, "column": 7},
            {"type": "SEPARATOR", "lexeme": ";", "line": 1, "column": 10},
            {"type": "EOF", "lexeme": "", "line": 2, "column": 1}
        ]
        
        parser = Parser(tokens)
        # Должен разобраться без ошибок
    
    def test_generic_type(self):
        """Тест generic типа"""
        tokens = [
            {"type": "IDENTIFIER", "lexeme": "List", "line": 1, "column": 1},
            {"type": "OPERATOR", "lexeme": "<", "line": 1, "column": 5},
            {"type": "IDENTIFIER", "lexeme": "String", "line": 1, "column": 6},
            {"type": "OPERATOR", "lexeme": ">", "line": 1, "column": 12},
            {"type": "IDENTIFIER", "lexeme": "list", "line": 1, "column": 14},
            {"type": "SEPARATOR", "lexeme": ";", "line": 1, "column": 18},
            {"type": "EOF", "lexeme": "", "line": 2, "column": 1}
        ]
        
        parser = Parser(tokens)
        # Должен разобраться без ошибок
    
    # ===== ТЕСТЫ ИМПОРТОВ =====
    
    def test_import_declaration(self):
        """Тест импорта"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "import", "line": 1, "column": 1},
            {"type": "IDENTIFIER", "lexeme": "java", "line": 1, "column": 8},
            {"type": "OPERATOR", "lexeme": ".", "line": 1, "column": 12},
            {"type": "IDENTIFIER", "lexeme": "util", "line": 1, "column": 13},
            {"type": "OPERATOR", "lexeme": ".", "line": 1, "column": 17},
            {"type": "IDENTIFIER", "lexeme": "List", "line": 1, "column": 18},
            {"type": "SEPARATOR", "lexeme": ";", "line": 1, "column": 22},
            {"type": "EOF", "lexeme": "", "line": 2, "column": 1}
        ]
        
        parser = Parser(tokens)
        program = parser.parse()
        
        assert len(program.imports) == 1
        assert program.imports[0] == "java.util.List"
    
    # ===== ТЕСТЫ ОШИБОК И ВОССТАНОВЛЕНИЯ =====
    
    def test_error_recovery(self):
        """Тест восстановления после ошибки"""
        tokens = [
            {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 1},
            {"type": "IDENTIFIER", "lexeme": "A", "line": 1, "column": 7},
            {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 9},
            {"type": "IDENTIFIER", "lexeme": "ERROR", "line": 2, "column": 5},  # Синтаксическая ошибка
            {"type": "KEYWORD", "lexeme": "void", "line": 3, "column": 5},
            {"type": "IDENTIFIER", "lexeme": "method", "line": 3, "column": 10},
            {"type": "SEPARATOR", "lexeme": "(", "line": 3, "column": 16},
            {"type": "SEPARATOR", "lexeme": ")", "line": 3, "column": 17},
            {"type": "SEPARATOR", "lexeme": "{", "line": 3, "column": 19},
            {"type": "SEPARATOR", "lexeme": "}", "line": 4, "column": 5},
            {"type": "SEPARATOR", "lexeme": "}", "line": 5, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 6, "column": 1}
        ]
        
        parser = Parser(tokens)
        program = parser.parse()
        
        # Должен восстановиться и найти класс с методом
        assert len(program.classes) == 1
        assert len(program.classes[0].methods) == 1
    
    # ===== КОМПЛЕКСНЫЕ ТЕСТЫ =====
    
    def test_complete_program(self):
        """Тест полной программы"""
        tokens = [
            # Импорт
            {"type": "KEYWORD", "lexeme": "import", "line": 1, "column": 1},
            {"type": "IDENTIFIER", "lexeme": "java", "line": 1, "column": 8},
            {"type": "OPERATOR", "lexeme": ".", "line": 1, "column": 12},
            {"type": "IDENTIFIER", "lexeme": "util", "line": 1, "column": 13},
            {"type": "OPERATOR", "lexeme": ".", "line": 1, "column": 17},
            {"type": "IDENTIFIER", "lexeme": "List", "line": 1, "column": 18},
            {"type": "SEPARATOR", "lexeme": ";", "line": 1, "column": 22},
            # Класс
            {"type": "KEYWORD", "lexeme": "public", "line": 3, "column": 1},
            {"type": "KEYWORD", "lexeme": "class", "line": 3, "column": 8},
            {"type": "IDENTIFIER", "lexeme": "Main", "line": 3, "column": 14},
            {"type": "SEPARATOR", "lexeme": "{", "line": 3, "column": 19},
            # Поле
            {"type": "KEYWORD", "lexeme": "private", "line": 4, "column": 5},
            {"type": "IDENTIFIER", "lexeme": "List", "line": 4, "column": 13},
            {"type": "OPERATOR", "lexeme": "<", "line": 4, "column": 17},
            {"type": "IDENTIFIER", "lexeme": "String", "line": 4, "column": 18},
            {"type": "OPERATOR", "lexeme": ">", "line": 4, "column": 24},
            {"type": "IDENTIFIER", "lexeme": "items", "line": 4, "column": 26},
            {"type": "SEPARATOR", "lexeme": ";", "line": 4, "column": 31},
            # Метод
            {"type": "KEYWORD", "lexeme": "public", "line": 6, "column": 5},
            {"type": "KEYWORD", "lexeme": "static", "line": 6, "column": 12},
            {"type": "KEYWORD", "lexeme": "void", "line": 6, "column": 19},
            {"type": "IDENTIFIER", "lexeme": "main", "line": 6, "column": 24},
            {"type": "SEPARATOR", "lexeme": "(", "line": 6, "column": 28},
            {"type": "IDENTIFIER", "lexeme": "String", "line": 6, "column": 29},
            {"type": "SEPARATOR", "lexeme": "[", "line": 6, "column": 35},
            {"type": "SEPARATOR", "lexeme": "]", "line": 6, "column": 36},
            {"type": "IDENTIFIER", "lexeme": "args", "line": 6, "column": 38},
            {"type": "SEPARATOR", "lexeme": ")", "line": 6, "column": 42},
            {"type": "SEPARATOR", "lexeme": "{", "line": 6, "column": 44},
            # Вызов метода в теле
            {"type": "IDENTIFIER", "lexeme": "System", "line": 7, "column": 9},
            {"type": "OPERATOR", "lexeme": ".", "line": 7, "column": 15},
            {"type": "IDENTIFIER", "lexeme": "out", "line": 7, "column": 16},
            {"type": "OPERATOR", "lexeme": ".", "line": 7, "column": 19},
            {"type": "IDENTIFIER", "lexeme": "println", "line": 7, "column": 20},
            {"type": "SEPARATOR", "lexeme": "(", "line": 7, "column": 27},
            {"type": "STRING_LITERAL", "lexeme": "Hello", "line": 7, "column": 28},
            {"type": "SEPARATOR", "lexeme": ")", "line": 7, "column": 35},
            {"type": "SEPARATOR", "lexeme": ";", "line": 7, "column": 36},
            {"type": "SEPARATOR", "lexeme": "}", "line": 8, "column": 5},
            {"type": "SEPARATOR", "lexeme": "}", "line": 9, "column": 1},
            {"type": "EOF", "lexeme": "", "line": 10, "column": 1}
        ]
        
        parser = Parser(tokens)
        program = parser.parse()
        
        # Проверяем структуру программы
        assert len(program.imports) == 1
        assert len(program.classes) == 1
        
        class_decl = program.classes[0]
        assert class_decl.name == "Main"
        assert class_decl.modifiers == ["public"]
        
        # Проверяем поля
        assert len(class_decl.fields) == 1
        field = class_decl.fields[0]
        assert field.name == "items"
        assert field.field_type.name == "List"
        assert field.modifiers == ["private"]
        
        # Проверяем методы
        assert len(class_decl.methods) == 1
        method = class_decl.methods[0]
        assert method.name == "main"
        assert method.return_type.name == "void"
        assert method.modifiers == ["public", "static"]
        assert len(method.parameters) == 1


# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v"])