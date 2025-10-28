import pytest
import sys
import os

# Добавляем путь к проекту
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from fastapi.testclient import TestClient  # ← ДОБАВИТЬ ЭТОТ ИМПОРТ
from app.main import app
from app.javaparser.parser import Parser, Token
from app.javaparser.ast import *


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_tokens_simple_class():
    """Фикстура с токенами простого класса"""
    return [
        {"type": "KEYWORD", "lexeme": "public", "line": 1, "column": 1},
        {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 8},
        {"type": "IDENTIFIER", "lexeme": "Test", "line": 1, "column": 14},
        {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 19},
        {"type": "SEPARATOR", "lexeme": "}", "line": 1, "column": 20},
        {"type": "EOF", "lexeme": "", "line": 1, "column": 21}
    ]


@pytest.fixture
def sample_tokens_class_with_method():
    """Фикстура с токенами класса с методом - УПРОЩЕННАЯ ВЕРСИЯ"""
    return [
        {"type": "KEYWORD", "lexeme": "public", "line": 1, "column": 1},
        {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 8},
        {"type": "IDENTIFIER", "lexeme": "Calculator", "line": 1, "column": 14},
        {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 25},
        
        # Упрощенный метод
        {"type": "KEYWORD", "lexeme": "public", "line": 2, "column": 5},
        {"type": "KEYWORD", "lexeme": "int", "line": 2, "column": 12},
        {"type": "IDENTIFIER", "lexeme": "add", "line": 2, "column": 16},
        {"type": "SEPARATOR", "lexeme": "(", "line": 2, "column": 19},
        {"type": "SEPARATOR", "lexeme": ")", "line": 2, "column": 20},
        {"type": "SEPARATOR", "lexeme": "{", "line": 2, "column": 22},
        {"type": "SEPARATOR", "lexeme": "}", "line": 2, "column": 23},
        
        {"type": "SEPARATOR", "lexeme": "}", "line": 3, "column": 1},
        {"type": "EOF", "lexeme": "", "line": 3, "column": 2}
    ]


@pytest.fixture
def sample_tokens_with_fields():
    """Фикстура с токенами класса с полями"""
    return [
        {"type": "KEYWORD", "lexeme": "public", "line": 1, "column": 1},
        {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 8},
        {"type": "IDENTIFIER", "lexeme": "Student", "line": 1, "column": 14},
        {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 22},
        
        {"type": "KEYWORD", "lexeme": "private", "line": 2, "column": 5},
        {"type": "KEYWORD", "lexeme": "String", "line": 2, "column": 13},
        {"type": "IDENTIFIER", "lexeme": "name", "line": 2, "column": 20},
        {"type": "SEPARATOR", "lexeme": ";", "line": 2, "column": 24},
        
        {"type": "KEYWORD", "lexeme": "private", "line": 3, "column": 5},
        {"type": "KEYWORD", "lexeme": "int", "line": 3, "column": 13},
        {"type": "IDENTIFIER", "lexeme": "age", "line": 3, "column": 17},
        {"type": "SEPARATOR", "lexeme": ";", "line": 3, "column": 20},
        
        {"type": "SEPARATOR", "lexeme": "}", "line": 4, "column": 1},
        {"type": "EOF", "lexeme": "", "line": 4, "column": 2}
    ]


def create_parser(tokens):
    """Утилита для создания парсера"""
    return Parser(tokens)


def assert_node_type(node, expected_type):
    """Проверка типа узла"""
    assert node is not None
    assert node.node_type == expected_type


def assert_node_has_field(node, field_name, expected_value=None):
    """Проверка наличия поля у узла"""
    assert hasattr(node, field_name), f"Узел не имеет поля {field_name}"
    if expected_value is not None:
        actual_value = getattr(node, field_name)
        assert actual_value == expected_value, f"Поле {field_name}: ожидалось {expected_value}, получено {actual_value}"