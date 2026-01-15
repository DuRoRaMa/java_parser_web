"""Тесты управляющих конструкций."""
import pytest
from app.javaparser.ast import NodeType


class TestVariableDeclaration:
    """Тесты объявления переменных."""
    
    def test_simple_declaration(self, parse, class_wrapper, make_token):
        """int x;"""
        tokens = class_wrapper([
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "x"),
            make_token("SEPARATOR", ";"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.VARIABLE_DECLARATION
        assert stmt.name == "x"
        assert stmt.var_type.name == "int"
    
    def test_declaration_with_init(self, parse, class_wrapper, make_token):
        """int x = 5;"""
        tokens = class_wrapper([
            make_token("KEYWORD", "int"),
            make_token("IDENTIFIER", "x"),
            make_token("OPERATOR", "="),
            make_token("INT_LITERAL", "5"),
            make_token("SEPARATOR", ";"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.value is not None
        assert stmt.value.value == "5"


class TestIfStatement:
    """Тесты if-else."""
    
    def test_simple_if(self, parse, class_wrapper, make_token):
        """if (true) {}"""
        tokens = class_wrapper([
            make_token("KEYWORD", "if"),
            make_token("SEPARATOR", "("),
            make_token("KEYWORD", "true"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.IF_STATEMENT
        assert len(stmt.children) >= 2  # condition + then
    
    def test_if_else(self, parse, class_wrapper, make_token):
        """if (true) {} else {}"""
        tokens = class_wrapper([
            make_token("KEYWORD", "if"),
            make_token("SEPARATOR", "("),
            make_token("KEYWORD", "true"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("KEYWORD", "else"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert len(stmt.children) == 3  # condition + then + else


class TestWhileStatement:
    """Тесты while."""
    
    def test_while(self, parse, class_wrapper, make_token):
        """while (true) {}"""
        tokens = class_wrapper([
            make_token("KEYWORD", "while"),
            make_token("SEPARATOR", "("),
            make_token("KEYWORD", "true"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.WHILE_STATEMENT


class TestDoWhileStatement:
    """Тесты do-while."""
    
    def test_do_while(self, parse, class_wrapper, make_token):
        """do {} while (true);"""
        tokens = class_wrapper([
            make_token("KEYWORD", "do"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("KEYWORD", "while"),
            make_token("SEPARATOR", "("),
            make_token("KEYWORD", "true"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", ";"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.DO_WHILE_STATEMENT


class TestForStatement:
    """Тесты for."""
    
    def test_basic_for(self, parse, class_wrapper, make_token):
        """for (int i = 0; i < 10; i++) {}"""
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
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.FOR_STATEMENT


class TestForEachStatement:
    """Тесты for-each."""
    
    def test_for_each(self, parse, class_wrapper, make_token):
        """for (String s : list) {}"""
        tokens = class_wrapper([
            make_token("KEYWORD", "for"),
            make_token("SEPARATOR", "("),
            make_token("IDENTIFIER", "String"),
            make_token("IDENTIFIER", "s"),
            make_token("OPERATOR", ":"),
            make_token("IDENTIFIER", "list"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.FOR_EACH_STATEMENT
        assert stmt.var_name == "s"
        assert stmt.var_type.name == "String"
        assert stmt.iterable.name == "list"


class TestSwitchStatement:
    """Тесты switch/case."""
    
    def test_switch(self, parse, class_wrapper, make_token):
        """switch (x) { case 1: break; default: break; }"""
        tokens = class_wrapper([
            make_token("KEYWORD", "switch"),
            make_token("SEPARATOR", "("),
            make_token("IDENTIFIER", "x"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("KEYWORD", "case"),
            make_token("INT_LITERAL", "1"),
            make_token("OPERATOR", ":"),
            make_token("KEYWORD", "break"),
            make_token("SEPARATOR", ";"),
            make_token("KEYWORD", "default"),
            make_token("OPERATOR", ":"),
            make_token("KEYWORD", "break"),
            make_token("SEPARATOR", ";"),
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.SWITCH_STATEMENT
        assert len(stmt.cases) == 2
        assert stmt.cases[0].is_default == False
        assert stmt.cases[1].is_default == True


class TestBreakContinue:
    """Тесты break и continue."""
    
    def test_break(self, parse, class_wrapper, make_token):
        """break;"""
        tokens = class_wrapper([
            make_token("KEYWORD", "break"),
            make_token("SEPARATOR", ";"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.BREAK_STATEMENT
    
    def test_continue(self, parse, class_wrapper, make_token):
        """continue;"""
        tokens = class_wrapper([
            make_token("KEYWORD", "continue"),
            make_token("SEPARATOR", ";"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.CONTINUE_STATEMENT
    
    def test_break_with_label(self, parse, class_wrapper, make_token):
        """break outer;"""
        tokens = class_wrapper([
            make_token("KEYWORD", "break"),
            make_token("IDENTIFIER", "outer"),
            make_token("SEPARATOR", ";"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.label == "outer"


class TestReturnStatement:
    """Тесты return."""
    
    def test_return_void(self, parse, class_wrapper, make_token):
        """return;"""
        tokens = class_wrapper([
            make_token("KEYWORD", "return"),
            make_token("SEPARATOR", ";"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.RETURN_STATEMENT
        assert stmt.children == []
    
    def test_return_value(self, parse, class_wrapper, make_token):
        """return 42;"""
        tokens = class_wrapper([
            make_token("KEYWORD", "return"),
            make_token("INT_LITERAL", "42"),
            make_token("SEPARATOR", ";"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert len(stmt.children) == 1


class TestTryCatch:
    """Тесты try-catch-finally."""
    
    def test_try_catch(self, parse, class_wrapper, make_token):
        """try {} catch (Exception e) {}"""
        tokens = class_wrapper([
            make_token("KEYWORD", "try"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("KEYWORD", "catch"),
            make_token("SEPARATOR", "("),
            make_token("IDENTIFIER", "Exception"),
            make_token("IDENTIFIER", "e"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.TRY_STATEMENT
        assert len(stmt.catch_clauses) == 1
        assert stmt.catch_clauses[0].exception_type.name == "Exception"
        assert stmt.catch_clauses[0].exception_name == "e"
    
    def test_try_finally(self, parse, class_wrapper, make_token):
        """try {} finally {}"""
        tokens = class_wrapper([
            make_token("KEYWORD", "try"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("KEYWORD", "finally"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.finally_block is not None
    
    def test_try_catch_finally(self, parse, class_wrapper, make_token):
        """try {} catch (E e) {} finally {}"""
        tokens = class_wrapper([
            make_token("KEYWORD", "try"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("KEYWORD", "catch"),
            make_token("SEPARATOR", "("),
            make_token("IDENTIFIER", "E"),
            make_token("IDENTIFIER", "e"),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
            make_token("KEYWORD", "finally"),
            make_token("SEPARATOR", "{"),
            make_token("SEPARATOR", "}"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert len(stmt.catch_clauses) == 1
        assert stmt.finally_block is not None


class TestThrowStatement:
    """Тесты throw."""
    
    def test_throw(self, parse, class_wrapper, make_token):
        """throw new Exception();"""
        tokens = class_wrapper([
            make_token("KEYWORD", "throw"),
            make_token("KEYWORD", "new"),
            make_token("IDENTIFIER", "Exception"),
            make_token("SEPARATOR", "("),
            make_token("SEPARATOR", ")"),
            make_token("SEPARATOR", ";"),
        ])
        result = parse(tokens)
        
        stmt = result.classes[0].methods[0].body.statements[0]
        assert stmt.node_type == NodeType.THROW_STATEMENT
        assert stmt.expression.node_type == NodeType.OBJECT_CREATION
