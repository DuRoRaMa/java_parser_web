
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.javaparser.parser import Parser

def test_parser_final():
    print("ФИНАЛЬНЫЙ ТЕСТ ПАРСЕРА")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "1. Пустой класс",
            "tokens": [
                {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 1},
                {"type": "IDENTIFIER", "lexeme": "Empty", "line": 1, "column": 7},
                {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 13},
                {"type": "SEPARATOR", "lexeme": "}", "line": 1, "column": 14},
                {"type": "EOF", "lexeme": "", "line": 1, "column": 15}
            ]
        },
        {
            "name": "2. Класс с полями",
            "tokens": [
                {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 1},
                {"type": "IDENTIFIER", "lexeme": "Person", "line": 1, "column": 7},
                {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 14},
                {"type": "KEYWORD", "lexeme": "String", "line": 2, "column": 5},
                {"type": "IDENTIFIER", "lexeme": "name", "line": 2, "column": 12},
                {"type": "SEPARATOR", "lexeme": ";", "line": 2, "column": 16},
                {"type": "KEYWORD", "lexeme": "int", "line": 3, "column": 5},
                {"type": "IDENTIFIER", "lexeme": "age", "line": 3, "column": 9},
                {"type": "SEPARATOR", "lexeme": ";", "line": 3, "column": 12},
                {"type": "SEPARATOR", "lexeme": "}", "line": 4, "column": 1},
                {"type": "EOF", "lexeme": "", "line": 4, "column": 2}
            ]
        },
        {
            "name": "3. Простой метод",
            "tokens": [
                {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 1},
                {"type": "IDENTIFIER", "lexeme": "Test", "line": 1, "column": 7},
                {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 12},
                {"type": "KEYWORD", "lexeme": "void", "line": 2, "column": 5},
                {"type": "IDENTIFIER", "lexeme": "method", "line": 2, "column": 10},
                {"type": "SEPARATOR", "lexeme": "(", "line": 2, "column": 16},
                {"type": "SEPARATOR", "lexeme": ")", "line": 2, "column": 17},
                {"type": "SEPARATOR", "lexeme": "{", "line": 2, "column": 19},
                {"type": "SEPARATOR", "lexeme": "}", "line": 2, "column": 20},
                {"type": "SEPARATOR", "lexeme": "}", "line": 3, "column": 1},
                {"type": "EOF", "lexeme": "", "line": 3, "column": 2}
            ]
        },
        {
            "name": "4. Метод с параметрами",
            "tokens": [
                {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 1},
                {"type": "IDENTIFIER", "lexeme": "Calculator", "line": 1, "column": 7},
                {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 18},
                {"type": "KEYWORD", "lexeme": "int", "line": 2, "column": 5},
                {"type": "IDENTIFIER", "lexeme": "add", "line": 2, "column": 9},
                {"type": "SEPARATOR", "lexeme": "(", "line": 2, "column": 12},
                {"type": "KEYWORD", "lexeme": "int", "line": 2, "column": 13},
                {"type": "IDENTIFIER", "lexeme": "a", "line": 2, "column": 17},
                {"type": "SEPARATOR", "lexeme": ",", "line": 2, "column": 18},
                {"type": "KEYWORD", "lexeme": "int", "line": 2, "column": 20},
                {"type": "IDENTIFIER", "lexeme": "b", "line": 2, "column": 24},
                {"type": "SEPARATOR", "lexeme": ")", "line": 2, "column": 25},
                {"type": "SEPARATOR", "lexeme": "{", "line": 2, "column": 27},
                {"type": "SEPARATOR", "lexeme": "}", "line": 2, "column": 28},
                {"type": "SEPARATOR", "lexeme": "}", "line": 3, "column": 1},
                {"type": "EOF", "lexeme": "", "line": 3, "column": 2}
            ]
        },
        {
            "name": "5. Метод с модификаторами",
            "tokens": [
                {"type": "KEYWORD", "lexeme": "class", "line": 1, "column": 1},
                {"type": "IDENTIFIER", "lexeme": "Main", "line": 1, "column": 7},
                {"type": "SEPARATOR", "lexeme": "{", "line": 1, "column": 12},
                {"type": "KEYWORD", "lexeme": "public", "line": 2, "column": 5},
                {"type": "KEYWORD", "lexeme": "static", "line": 2, "column": 12},
                {"type": "KEYWORD", "lexeme": "void", "line": 2, "column": 19},
                {"type": "IDENTIFIER", "lexeme": "main", "line": 2, "column": 24},
                {"type": "SEPARATOR", "lexeme": "(", "line": 2, "column": 28},
                {"type": "SEPARATOR", "lexeme": ")", "line": 2, "column": 29},
                {"type": "SEPARATOR", "lexeme": "{", "line": 2, "column": 31},
                {"type": "SEPARATOR", "lexeme": "}", "line": 2, "column": 32},
                {"type": "SEPARATOR", "lexeme": "}", "line": 3, "column": 1},
                {"type": "EOF", "lexeme": "", "line": 3, "column": 2}
            ]
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        print(f"\n{test_case['name']}")
        print("-" * 40)
        
        try:
            parser = Parser(test_case["tokens"])
            ast = parser.parse()
            
            print("   SUCCESS: Parsing completed")
            print(f"   Program: {len(ast.classes)} classes")
            
            for i, cls in enumerate(ast.classes):
                print(f"      Class {i+1}: {cls.name}")
                print(f"         Modifiers: {cls.modifiers}")
                print(f"         Fields: {len(cls.fields)}")
                print(f"         Methods: {len(cls.methods)}")
                
                for field in cls.fields:
                    print(f"           Field: {field.field_type.name} {field.name}")
                
                for method in cls.methods:
                    print(f"           Method: {method.return_type.name} {method.name}()")
                    print(f"              Modifiers: {method.modifiers}")
                    print(f"              Parameters: {len(method.parameters)}")
            
            passed += 1
                    
        except Exception as e:
            print(f"   ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print(f"\n" + "=" * 50)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 50)
    
    if failed == 0:
        print("ALL TESTS PASSED! Parser is working correctly.")
    else:
        print(f"{failed} tests failed. Parser needs fixes.")

if __name__ == "__main__":
    test_parser_final()