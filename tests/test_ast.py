import pytest
from app.javaparser.ast import *


class TestASTNodes:
    """Тесты для AST узлов"""
    
    def test_program_node(self):
        """Тест узла Program"""
        pos = Position(1, 1)
        program = Program(NodeType.PROGRAM, pos)
        
        assert program.node_type == NodeType.PROGRAM
        assert program.position == pos
        assert program.classes == []
        assert program.imports == []
        
        # Тест добавления классов
        class_node = ClassDeclaration(NodeType.CLASS_DECLARATION, pos, name="Test")
        program.classes.append(class_node)
        assert len(program.classes) == 1
        assert program.classes[0].name == "Test"
    
    def test_class_declaration(self):
        """Тест узла ClassDeclaration"""
        pos = Position(1, 1)
        class_decl = ClassDeclaration(
            NodeType.CLASS_DECLARATION, 
            pos, 
            name="Calculator",
            modifiers=["public"]
        )
        
        assert class_decl.name == "Calculator"
        assert "public" in class_decl.modifiers
        assert class_decl.fields == []
        assert class_decl.methods == []
    
    def test_method_declaration(self):
        """Тест узла MethodDeclaration"""
        pos = Position(2, 5)
        return_type = Type(NodeType.TYPE, pos, name="int")
        
        method = MethodDeclaration(
            NodeType.METHOD_DECLARATION,
            pos,
            name="calculate",
            return_type=return_type,
            modifiers=["public", "static"]
        )
        
        assert method.name == "calculate"
        assert method.return_type.name == "int"
        assert "public" in method.modifiers
        assert "static" in method.modifiers
        assert method.parameters == []
    
    def test_field_declaration(self):
        """Тест узла FieldDeclaration"""
        pos = Position(3, 5)
        field_type = Type(NodeType.TYPE, pos, name="String")
        
        field = FieldDeclaration(
            NodeType.FIELD_DECLARATION,
            pos,
            name="username",
            field_type=field_type,
            modifiers=["private"]
        )
        
        assert field.name == "username"
        assert field.field_type.name == "String"
        assert "private" in field.modifiers
        assert field.value is None
    
    def test_type_node(self):
        """Тест узла Type"""
        pos = Position(1, 1)
        
        # Простой тип
        simple_type = Type(NodeType.TYPE, pos, name="int")
        assert simple_type.name == "int"
        assert not simple_type.is_array
        
        # Массив
        array_type = Type(NodeType.TYPE, pos, name="String", is_array=True)
        assert array_type.name == "String"
        assert array_type.is_array
    
    def test_identifier_node(self):
        """Тест узла Identifier"""
        pos = Position(1, 1)
        identifier = Identifier(NodeType.IDENTIFIER, pos, name="variableName")
        
        assert identifier.name == "variableName"
        assert identifier.node_type == NodeType.IDENTIFIER
    
    def test_literal_node(self):
        """Тест узла Literal"""
        pos = Position(1, 1)
        
        # Строковый литерал
        string_literal = Literal(NodeType.LITERAL, pos, value="Hello", literal_type="string")
        assert string_literal.value == "Hello"
        assert string_literal.literal_type == "string"
        
        # Числовой литерал
        int_literal = Literal(NodeType.LITERAL, pos, value="42", literal_type="int")
        assert int_literal.value == "42"
        assert int_literal.literal_type == "int"
    
    def test_binary_operation(self):
        """Тест узла BinaryOperation"""
        pos = Position(1, 1)
        left = Identifier(NodeType.IDENTIFIER, pos, name="a")
        right = Identifier(NodeType.IDENTIFIER, pos, name="b")
        
        bin_op = BinaryOperation(
            NodeType.BINARY_OPERATION,
            pos,
            operator="+",
            left=left,
            right=right
        )
        
        assert bin_op.operator == "+"
        assert bin_op.left.name == "a"
        assert bin_op.right.name == "b"
    
    def test_method_call(self):
        """Тест узла MethodCall"""
        pos = Position(1, 1)
        arg1 = Literal(NodeType.LITERAL, pos, value="test", literal_type="string")
        
        method_call = MethodCall(
            NodeType.METHOD_CALL,
            pos,
            method_name="println",
            arguments=[arg1]
        )
        
        assert method_call.method_name == "println"
        assert len(method_call.arguments) == 1
        assert method_call.arguments[0].value == "test"
    
    def test_node_children(self):
        """Тест иерархии детей узлов"""
        pos = Position(1, 1)
        parent = ASTNode(NodeType.BLOCK, pos)
        
        child1 = Identifier(NodeType.IDENTIFIER, pos, name="x")
        child2 = Literal(NodeType.LITERAL, pos, value="10", literal_type="int")
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        assert len(parent.children) == 2
        assert parent.children[0].name == "x"
        assert parent.children[1].value == "10"