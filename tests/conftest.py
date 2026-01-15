import pytest
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.javaparser import Parser
from app.javaparser.ast import (
    Program, ClassDeclaration, MethodDeclaration, FieldDeclaration,
    VariableDeclaration, BinaryOperation, UnaryOperation, Assignment,
    Literal, Identifier, MethodCall, Block, Parameter, Type, NodeType
)


@pytest.fixture
def parser():
    """Фабрика для создания парсера с токенами."""
    def _parser(tokens):
        return Parser(tokens)
    return _parser


@pytest.fixture
def parse(parser):
    """Парсит токены и возвращает AST."""
    def _parse(tokens):
        p = parser(tokens)
        return p.parse()
    return _parse


def make_token(type_: str, lexeme: str, line: int = 1, column: int = 1):
    """Хелпер для создания токена.
    
    Автоматически конвертирует сокращённые типы в полные:
    - INTEGER -> INT_LITERAL
    - FLOAT -> FLOAT_LITERAL  
    - STRING -> STRING_LITERAL
    - CHAR -> CHAR_LITERAL
    - BOOLEAN -> BOOLEAN_LITERAL
    """
    # Маппинг сокращённых типов в полные
    type_mapping = {
        "INTEGER": "INT_LITERAL",
        "FLOAT": "FLOAT_LITERAL",
        "STRING": "STRING_LITERAL",
        "CHAR": "CHAR_LITERAL",
        "BOOLEAN": "BOOLEAN_LITERAL",
        "NULL": "NULL_LITERAL",
        "NUMBER": "INT_LITERAL",
    }
    
    # Конвертируем если нужно
    actual_type = type_mapping.get(type_, type_)
    
    return {"type": actual_type, "lexeme": lexeme, "line": line, "column": column}


# Экспортируем хелпер
pytest.make_token = make_token
