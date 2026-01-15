"""Фикстуры для тестов парсера."""
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

import pytest
from app.javaparser import Parser
from app.javaparser.ast import (
    Program, ClassDeclaration, MethodDeclaration, FieldDeclaration,
    VariableDeclaration, Parameter, Block, Type, Identifier, Literal,
    BinaryOperation, UnaryOperation, Assignment, MethodCall,
    ConstructorDeclaration, ThisCall, SuperCall,
    BreakStatement, ContinueStatement,
    TryStatement, CatchClause, ThrowStatement,
    TernaryOperation, InstanceofExpression, CastExpression,
    ArrayCreation, ObjectCreation, ArrayAccess, 
    SwitchStatement, SwitchCase,
    ForEachStatement, DoWhileStatement,
    NodeType
)


@pytest.fixture
def parse():
    """Фабрика для парсинга токенов."""
    def _parse(tokens: list) -> Program:
        parser = Parser(tokens)
        return parser.parse()
    return _parse


@pytest.fixture
def make_token():
    """Фабрика для создания токенов."""
    def _make(type: str, lexeme: str, line: int = 1, column: int = 1) -> dict:
        return {"type": type, "lexeme": lexeme, "line": line, "column": column}
    return _make


@pytest.fixture
def class_wrapper(make_token):
    """Оборачивает токены в класс и метод для тестирования statements."""
    def _wrap(statement_tokens: list, method_name: str = "test") -> list:
        tokens = [
            make_token("KEYWORD", "class", 1, 1),
            make_token("IDENTIFIER", "Test", 1, 7),
            make_token("SEPARATOR", "{", 1, 12),
            make_token("KEYWORD", "void", 2, 5),
            make_token("IDENTIFIER", method_name, 2, 10),
            make_token("SEPARATOR", "(", 2, 14),
            make_token("SEPARATOR", ")", 2, 15),
            make_token("SEPARATOR", "{", 2, 17),
        ]
        tokens.extend(statement_tokens)
        tokens.extend([
            make_token("SEPARATOR", "}", 100, 5),
            make_token("SEPARATOR", "}", 101, 1),
        ])
        return tokens
    return _wrap


@pytest.fixture
def expr_wrapper(make_token, class_wrapper):
    """Оборачивает выражение в return statement для тестирования."""
    def _wrap(expr_tokens: list) -> list:
        statement_tokens = [
            make_token("KEYWORD", "return", 3, 9),
        ]
        statement_tokens.extend(expr_tokens)
        statement_tokens.append(make_token("SEPARATOR", ";", 3, 50))
        return class_wrapper(statement_tokens)
    return _wrap
