"""Базовые тесты парсера: классы, поля, методы."""
import pytest
from app.javaparser.ast import NodeType


class TestEmptyClass:
    """Тесты пустого класса."""
    
    def test_empty_class(self, parse, make_token):
        """class Empty {}"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "Empty"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        assert result.node_type == NodeType.PROGRAM
        assert len(result.classes) == 1
        assert result.classes[0].name == "Empty"
        assert result.classes[0].fields == []
        assert result.classes[0].methods == []
        assert result.classes[0].constructors == []
    
    def test_class_with_modifiers(self, parse, make_token):
        """public abstract class MyClass {}"""
        tokens = [
            make_token("KEYWORD", "public"),
            make_token("KEYWORD", "abstract"),
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "MyClass"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        cls = result.classes[0]
        assert cls.name == "MyClass"
        assert "public" in cls.modifiers
        assert "abstract" in cls.modifiers


class TestFields:
    """Тесты полей класса."""
    
    def test_simple_field(self, parse, make_token):
        """class A { int x; }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "x"),
            make_token("SEPARATOR", ";"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        assert len(result.classes[0].fields) == 1
        field = result.classes[0].fields[0]
        assert field.name == "x"
        assert field.field_type.name == "int"
    
    def test_field_with_modifiers(self, parse, make_token):
        """class A { private static final int MAX = 100; }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "private"),
            make_token("KEYWORD", "static"),
            make_token("KEYWORD", "final"),
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "MAX"),
            make_token("OPERATOR", "="),
            make_token("INT_LITERAL", "100"),
            make_token("SEPARATOR", ";"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        field = result.classes[0].fields[0]
        assert field.name == "MAX"
        assert "private" in field.modifiers
        assert "static" in field.modifiers
        assert "final" in field.modifiers
        assert field.value is not None
        assert field.value.value == "100"
    
    def test_field_with_string_init(self, parse, make_token):
        """class A { String name = "test"; }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("IDENTIFIER", "String"),
            make_token("IDENTIFIER", "name"),
            make_token("OPERATOR", "="),
            make_token("STRING_LITERAL", '"test"'),
            make_token("SEPARATOR", ";"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        field = result.classes[0].fields[0]
        assert field.name == "name"
        assert field.field_type.name == "String"
        assert field.value.literal_type == "string"
    
    def test_array_field(self, parse, make_token):
        """class A { int[] arr; }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "int"),
            make_token("SEPARATOR", "["),
            make_token("SEPARATOR", "]"),
            make_token("IDENTIFIER", "arr"),
            make_token("SEPARATOR", ";"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        field = result.classes[0].fields[0]
        assert field.name == "arr"
        assert field.field_type.name == "int"
        assert field.field_type.is_array == True


class TestMethods:
    """Тесты методов."""
    
    def test_void_method(self, parse, make_token):
        """class A { void test() {} }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "void"),
            make_token("IDENTIFIER", "test"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        assert len(result.classes[0].methods) == 1
        method = result.classes[0].methods[0]
        assert method.name == "test"
        assert method.return_type.name == "void"
        assert method.parameters == []
    
    def test_method_with_parameters(self, parse, make_token):
        """class A { int add(int a, int b) {} }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "add"),
            make_token("SEPARATOR", "("),
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "a"),
            make_token("SEPARATOR", ","),
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "b"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        method = result.classes[0].methods[0]
        assert method.name == "add"
        assert method.return_type.name == "int"
        assert len(method.parameters) == 2
        assert method.parameters[0].name == "a"
        assert method.parameters[1].name == "b"
    
    def test_method_with_throws(self, parse, make_token):
        """class A { void read() throws IOException {} }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "void"),
            make_token("IDENTIFIER", "read"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("KEYWORD", "throws"),
            make_token("IDENTIFIER", "IOException"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        method = result.classes[0].methods[0]
        assert len(method.throws) == 1
        assert method.throws[0].name == "IOException"


class TestConstructors:
    """Тесты конструкторов."""
    
    def test_simple_constructor(self, parse, make_token):
        """class A { A() {} }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        assert len(result.classes[0].constructors) == 1
        ctor = result.classes[0].constructors[0]
        assert ctor.name == "A"
    
    def test_constructor_with_params(self, parse, make_token):
        """class Person { public Person(String name) {} }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "Person"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "public"),
            make_token("IDENTIFIER", "Person"),
            make_token("SEPARATOR", "("),
            make_token("IDENTIFIER", "String"),
            make_token("IDENTIFIER", "name"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        ctor = result.classes[0].constructors[0]
        assert ctor.name == "Person"
        assert "public" in ctor.modifiers
        assert len(ctor.parameters) == 1
        assert ctor.parameters[0].name == "name"
    
    def test_this_call(self, parse, make_token):
        """class A { A() { this(0); } }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "{"),
            make_token("IDENTIFIER", "A"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "this"),
            make_token("SEPARATOR", "("),
            make_token("INT_LITERAL", "0"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", ";"),
            make_token("SEPARATOR", "}"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        ctor = result.classes[0].constructors[0]
        assert len(ctor.body.statements) == 1
        this_call = ctor.body.statements[0]
        assert this_call.node_type == NodeType.THIS_CALL
        assert len(this_call.arguments) == 1
    
    def test_super_call(self, parse, make_token):
        """class B { B() { super(); } }"""
        tokens = [
            make_token("KEYWORD", "class"),
            make_token("IDENTIFIER", "B"),
            make_token("SEPARATOR", "{"),
            make_token("IDENTIFIER", "B"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "super"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", ";"),
            make_token("SEPARATOR", "}"),
            make_token("SEPARATOR", "}"),
        ]
        result = parse(tokens)
        
        ctor = result.classes[0].constructors[0]
        super_call = ctor.body.statements[0]
        assert super_call.node_type == NodeType.SUPER_CALL
