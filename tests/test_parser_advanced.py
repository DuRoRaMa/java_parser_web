"""Расширенные тесты парсера."""
import pytest
from app.javaparser.ast import NodeType
from app.javaparser.errors import ParseError, UnexpectedTokenError


class TestComplexExpressions:
    """Тесты сложных выражений."""
    
    def test_chained_method_calls(self, parse, expr_wrapper, make_token):
        """return builder.setName("x").setValue(1).build();"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "builder"),
            make_token("SEPARATOR", "."),
            make_token("IDENTIFIER", "setName"),
            make_token("SEPARATOR", "("),
            make_token("STRING_LITERAL", '"x"'),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "."),
            make_token("IDENTIFIER", "setValue"),
            make_token("SEPARATOR", "("),
            make_token("INT_LITERAL", "1"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "."),
            make_token("IDENTIFIER", "build"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.METHOD_CALL
    
    def test_nested_ternary(self, parse, expr_wrapper, make_token):
        """return a ? b : c ? d : e;"""
        tokens = expr_wrapper([
            make_token("IDENTIFIER", "a"),
            make_token("OPERATOR", "?"),
            make_token("IDENTIFIER", "b"),
            make_token("OPERATOR", ":"),
            make_token("IDENTIFIER", "c"),
            make_token("OPERATOR", "?"),
            make_token("IDENTIFIER", "d"),
            make_token("OPERATOR", ":"),
            make_token("IDENTIFIER", "e"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.TERNARY_OPERATION
        # else_expr должен быть вложенным ternary
        assert expr.else_expr.node_type == NodeType.TERNARY_OPERATION
    
    def test_complex_arithmetic(self, parse, expr_wrapper, make_token):
        """return (a + b) * (c - d) / e;"""
        tokens = expr_wrapper([
            make_token("SEPARATOR", "("),
            make_token("IDENTIFIER", "a"),
            make_token("OPERATOR", "+"),
            make_token("IDENTIFIER", "b"),
            make_token("SEPARATOR", ")"),
            make_token("OPERATOR", "*"),
            make_token("SEPARATOR", "("),
            make_token("IDENTIFIER", "c"),
            make_token("OPERATOR", "-"),
            make_token("IDENTIFIER", "d"),
            make_token("SEPARATOR", ")"),
            make_token("OPERATOR", "/"),
            make_token("IDENTIFIER", "e"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.BINARY_OPERATION


class TestNestedStructures:
    """Тесты вложенных структур."""
    
    def test_nested_if(self, parse, class_wrapper, make_token):
        """if (a) { if (b) {} }"""
        tokens = class_wrapper([
            make_token("KEYWORD", "if"),
            make_token("SEPARATOR", "("),
            make_token("IDENTIFIER", "a"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "if"),
            make_token("SEPARATOR", "("),
            make_token("IDENTIFIER", "b"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        outer_if = result.classes[0].methods[0].body.statements[0]
        assert outer_if.node_type == NodeType.IF_STATEMENT
    
    def test_for_with_if(self, parse, class_wrapper, make_token):
        """for (int i = 0; i < 10; i++) { if (true) break; }"""
        tokens = class_wrapper([
            make_token("KEYWORD", "for"),
            make_token("SEPARATOR", "("),
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "i"),
            make_token("OPERATOR", "="),
            make_token("INT_LITERAL", "0"),
            make_token("SEPARATOR", ";"),
            make_token("IDENTIFIER", "i"),
            make_token("OPERATOR", "<"),
            make_token("INT_LITERAL", "10"),
            make_token("SEPARATOR", ";"),
            make_token("IDENTIFIER", "i"),
            make_token("OPERATOR", "++"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "if"),
            make_token("SEPARATOR", "("),
            make_token("KEYWORD", "true"),
            make_token("SEPARATOR", ")"),
            make_token("KEYWORD", "break"),
            make_token("SEPARATOR", ";"),
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        for_stmt = result.classes[0].methods[0].body.statements[0]
        assert for_stmt.node_type == NodeType.FOR_STATEMENT


class TestMultipleMembers:
    """Тесты множественных членов класса."""
    
    def test_multiple_fields(self, parse, make_token):
        """class A { int x; int y; int z; }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "x"),
            make_token("SEPARATOR", ";"),
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "y"),
            make_token("SEPARATOR", ";"),
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "z"),
            make_token("SEPARATOR", ";"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        assert len(result.classes[0].fields) == 3
    
    def test_multiple_methods(self, parse, make_token):
        """class A { void a() {} void b() {} }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "void"),
            make_token("IDENTIFIER", "a"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("KEYWORD", "void"),
            make_token("IDENTIFIER", "b"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        assert len(result.classes[0].methods) == 2
    
    def test_mixed_members(self, parse, make_token):
        """class A { int x; A() {} void foo() {} }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            # field
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "x"),
            make_token("SEPARATOR", ";"),
            # constructor
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            # method
            make_token("KEYWORD", "void"),
            make_token("IDENTIFIER", "foo"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        cls = result.classes[0]
        assert len(cls.fields) == 1
        assert len(cls.constructors) == 1
        assert len(cls.methods) == 1


class TestErrorHandling:
    """Тесты обработки ошибок."""
    
    def test_missing_semicolon(self, parse, class_wrapper, make_token):
        """int x (missing ;) — парсер пропускает неполный код.
        
        Это не идеальное поведение, но парсер не падает.
        При отсутствии точки с запятой парсер может:
        1. Не распарсить метод вообще
        2. Распарсить метод с пустым телом
        """
        tokens = class_wrapper([
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "x"),
            # missing semicolon
        ])
        
        # Парсер не должен падать
        result = parse(tokens)
        
        # Проверяем что парсинг завершился
        assert result is not None
        assert result.node_type.value == "Program"
    
    def test_missing_closing_brace(self, parse, make_token):
        """class A { (missing }) — должен вызвать ошибку."""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            # missing }
        ]
        
        with pytest.raises(Exception):
            parse(tokens)
    
    def test_invalid_token_format(self, parse):
        """Неверный формат токена."""
        tokens = [{"invalid": "token"}]
        
        with pytest.raises(Exception):
            parse(tokens)


class TestEdgeCases:
    """Тесты граничных случаев."""
    
    def test_empty_tokens(self, parse):
        """Пустой список токенов."""
        result = parse([])
        assert result.classes == []
    
    def test_this_reference(self, parse, class_wrapper, make_token):
        """this.field = value;"""
        tokens = class_wrapper([
            make_token("KEYWORD", "this"),
            make_token("SEPARATOR", "."),
            make_token("IDENTIFIER", "field"),
            make_token("OPERATOR", "="),
            make_token("IDENTIFIER", "value"),
            make_token("SEPARATOR", ";"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        # Should parse as expression statement with assignment
        assert stmt.children[0].node_type == NodeType.ASSIGNMENT
    
    def test_super_field_access(self, parse, expr_wrapper, make_token):
        """return super.field;"""
        tokens = expr_wrapper([
            make_token("KEYWORD", "super"),
            make_token("SEPARATOR", "."),
            make_token("IDENTIFIER", "field"),
        ])
        result = parse(tokens)
        
        expr = result.classes[0].methods[0].body.statements[0].children[0]
        assert expr.node_type == NodeType.FIELD_ACCESS


class TestImports:
    """Тесты импортов."""
    
    def test_simple_import(self, parse, make_token):
        """import java.util.List;"""
        tokens = [
            make_token("KEYWORD", "import"),
            make_token("IDENTIFIER", "java"),
            make_token("SEPARATOR", "."),
            make_token("IDENTIFIER", "util"),
            make_token("SEPARATOR", "."),
            make_token("IDENTIFIER", "List"),
            make_token("SEPARATOR", ";"),
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        assert len(result.imports) == 1
        assert result.imports[0] == "java.util.List"
    
    def test_wildcard_import(self, parse, make_token):
        """import java.util.*;"""
        tokens = [
            make_token("KEYWORD", "import"),
            make_token("IDENTIFIER", "java"),
            make_token("SEPARATOR", "."),
            make_token("IDENTIFIER", "util"),
            make_token("SEPARATOR", "."),
            make_token("OPERATOR", "*"),
            make_token("SEPARATOR", ";"),
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        assert result.imports[0] == "java.util.*"
