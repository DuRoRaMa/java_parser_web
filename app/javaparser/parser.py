from __future__ import annotations
import logging
from typing import List, Optional
from .ast import (
    ASTNode, Program, ClassDeclaration, MethodDeclaration, FieldDeclaration,
    VariableDeclaration, Type, Identifier, Literal, BinaryOperation, Assignment,
    MethodCall, Block, Parameter, NodeType, Position, UnaryOperation,
    BreakStatement, ContinueStatement, DoWhileStatement, TernaryOperation,
    ForEachStatement, ArrayCreation, ObjectCreation, ArrayAccess,
    ThrowStatement, InstanceofExpression, TryStatement, CatchClause,
    ConstructorDeclaration, ThisCall, SuperCall, CastExpression, 
    SwitchStatement, SwitchCase  # NEW!
)

from .errors import ParseError, UnexpectedTokenError

logger = logging.getLogger(__name__)


class Token:
    def __init__(self, type: str, lexeme: str, line: int, column: int):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.column = int(column)

    def __repr__(self):
        return f"Token({self.type}, '{self.lexeme}', {self.line}:{self.column})"


class Parser:
    """Базовый парсер Java, поддерживающий основные конструкции языка."""
    
    def __init__(self, tokens: List[dict], debug: bool = False):
        """Инициализация парсера.
        
        Args:
            tokens: Список токенов в формате {type, lexeme, line, column}
            debug: Включить отладочный вывод
        """
        try:
            self.tokens = [Token(**t) for t in tokens]
        except (TypeError, KeyError) as e:
            raise ValueError(f"Неверный формат токена: {e}") from e
        
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
        self.debug = debug

    # ==================== Вспомогательные методы ====================

    def _advance(self):
        """Переход к следующему токену."""
        if self.pos >= len(self.tokens) - 1:
            self.pos = len(self.tokens)
            self.current_token = None
        else:
            self.pos += 1
            self.current_token = self.tokens[self.pos]

    def _expect(self, token_type: str, value: str = None) -> Token:
        """Ожидание конкретного токена.
        
        Args:
            token_type: Ожидаемый тип токена
            value: Ожидаемое значение (опционально)
            
        Returns:
            Найденный токен
            
        Raises:
            UnexpectedTokenError: Если токен не соответствует ожиданиям
        """
        if not self.current_token:
            raise UnexpectedTokenError(token_type, "EOF", 1, 1)
        
        if self.current_token.type != token_type:
            raise UnexpectedTokenError(
                token_type, self.current_token.type,
                self.current_token.line, self.current_token.column
            )
        
        if value and self.current_token.lexeme != value:
            raise UnexpectedTokenError(
                f"'{value}'", f"'{self.current_token.lexeme}'",
                self.current_token.line, self.current_token.column
            )
        
        token = self.current_token
        self._advance()
        return token

    def _match(self, token_type: str, value: str = None) -> bool:
        """Проверка текущего токена без продвижения."""
        if not self.current_token:
            return False
        if self.current_token.type != token_type:
            return False
        if value and self.current_token.lexeme != value:
            return False
        return True

    def _current_position(self) -> Position:
        """Получение текущей позиции в исходном коде."""
        if self.current_token:
            return Position(self.current_token.line, self.current_token.column)
        if self.pos > 0 and self.pos <= len(self.tokens):
            last_token = self.tokens[self.pos - 1]
            return Position(last_token.line, last_token.column)
        return Position(1, 1)

    def _save_position(self) -> int:
        """Сохранение текущей позиции для возможного отката."""
        return self.pos

    def _restore_position(self, pos: int):
        """Восстановление позиции парсера."""
        self.pos = pos
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def _log(self, message: str):
        """Отладочный вывод."""
        if self.debug:
            logger.debug(message)

    # ==================== Главный метод парсинга ====================

    def parse(self) -> Program:
        """Парсинг программы.
        
        Grammar: program → import* classDecl*
        
        Returns:
            AST программы
        """
        pos = self._current_position()
        program = Program(NodeType.PROGRAM, pos)
        
        self._log(f"Начало парсинга, токенов: {len(self.tokens)}")
        
        while self.current_token and self.current_token.type != "EOF":
            # Импорты
            if self._match("KEYWORD", "import"):
                import_stmt = self._parse_import()
                program.imports.append(import_stmt)
                self._log(f"Добавлен импорт: {import_stmt}")
            
            # Классы
            elif self._match("KEYWORD") and self.current_token.lexeme in self._get_modifiers_set():
                class_decl = self._parse_class_declaration()
                if class_decl:
                    program.classes.append(class_decl)
                    self._log(f"Добавлен класс: {class_decl.name}")
            
            elif self._match("KEYWORD", "class"):
                class_decl = self._parse_class_declaration()
                if class_decl:
                    program.classes.append(class_decl)
                    self._log(f"Добавлен класс: {class_decl.name}")
            
            else:
                # Пропускаем неизвестные токены
                self._advance()
        
        self._log(f"Парсинг завершён: {len(program.classes)} классов, {len(program.imports)} импортов")
        return program
    def _peek_token(self, offset: int = 1):
        """Посмотреть токен на offset позиций вперёд без продвижения."""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None


    def _parse_arguments(self) -> List[ASTNode]:
        """Парсинг аргументов вызова (без скобок).
        
        Grammar: args → expr (',' expr)*
        """
        arguments = []
        
        if self._match("SEPARATOR", ")"):
            return arguments
        
        while True:
            arg = self._parse_expression()
            if arg:
                arguments.append(arg)
            
            if not self._match("SEPARATOR", ","):
                break
            self._advance()
        
        return arguments

    def _get_modifiers_set(self) -> set:
        """Возвращает набор допустимых модификаторов."""
        return {"public", "private", "protected", "static", "final", "abstract"}

    # ==================== Импорты ====================

    def _parse_import(self) -> str:
        """Парсинг импорта.
        
        Grammar: import → 'import' qualifiedName ';'
                 qualifiedName → IDENTIFIER ('.' IDENTIFIER)* ('.' '*')?
        """
        self._expect("KEYWORD", "import")
        
        parts = []
        
        # Первый идентификатор
        if self._match("IDENTIFIER"):
            parts.append(self.current_token.lexeme)
            self._advance()
        
        # Остальные части через точку
        while self._match("SEPARATOR", "."):
            parts.append(".")
            self._advance()
            
            if self._match("OPERATOR", "*"):
                parts.append("*")
                self._advance()
                break
            elif self._match("IDENTIFIER"):
                parts.append(self.current_token.lexeme)
                self._advance()
            else:
                break
        
        self._expect("SEPARATOR", ";")
        return "".join(parts)

    # ==================== Объявление класса ====================

    def _parse_class_declaration(self) -> ClassDeclaration:
        """Парсинг объявления класса.
        
        Grammar: classDecl → modifier* 'class' IDENTIFIER 
                            ('extends' IDENTIFIER)? 
                            ('implements' IDENTIFIER)?
                            '{' memberDecl* '}'
        """
        pos = self._current_position()
        
        # Модификаторы
        modifiers = self._parse_modifiers()
        
        # class
        self._expect("KEYWORD", "class")
        
        # Имя класса
        class_name = self._expect("IDENTIFIER").lexeme
        
        class_decl = ClassDeclaration(
            node_type=NodeType.CLASS_DECLARATION,
            position=pos,
            name=class_name,
            modifiers=modifiers
        )
        
        # extends
        if self._match("KEYWORD", "extends"):
            self._advance()
            parent_name = self._expect("IDENTIFIER").lexeme
            extends_node = ASTNode(NodeType.IDENTIFIER, self._current_position(), name="extends")
            extends_node.add_child(Type(NodeType.TYPE, self._current_position(), name=parent_name))
            class_decl.add_child(extends_node)
        
        # implements
        if self._match("KEYWORD", "implements"):
            self._advance()
            interface_name = self._expect("IDENTIFIER").lexeme
            implements_node = ASTNode(NodeType.IDENTIFIER, self._current_position(), name="implements")
            implements_node.add_child(Type(NodeType.TYPE, self._current_position(), name=interface_name))
            class_decl.add_child(implements_node)
        
        # Тело класса
        self._expect("SEPARATOR", "{")
        
        while self.current_token and not self._match("SEPARATOR", "}"):
            member = self._parse_class_member(class_name)
            if member:
                if isinstance(member, FieldDeclaration):
                    class_decl.fields.append(member)
                elif isinstance(member, ConstructorDeclaration):  # NEW!
                    class_decl.constructors.append(member)
                elif isinstance(member, MethodDeclaration):
                    class_decl.methods.append(member)
            else:
                # Пропускаем непонятный токен
                if self.current_token:
                    self._advance()
        
        self._expect("SEPARATOR", "}")
        
        self._log(f"Класс {class_name}: {len(class_decl.fields)} полей, {len(class_decl.methods)} методов")
        return class_decl

    def _parse_modifiers(self) -> List[str]:
        """Парсинг модификаторов.
        
        Grammar: modifier* где modifier ∈ {public, private, protected, static, final}
        """
        valid_modifiers = self._get_modifiers_set()
        modifiers = []
        
        while (self.current_token and
               self.current_token.type == "KEYWORD" and
               self.current_token.lexeme in valid_modifiers):
            modifiers.append(self.current_token.lexeme)
            self._advance()
        
        return modifiers

    # ==================== Члены класса ====================

    def _parse_class_member(self, class_name: str):
        """Парсинг члена класса (поле, метод или конструктор).
        
        Grammar: memberDecl → fieldDecl | methodDecl | constructorDecl
        """
        start_pos = self._save_position()
        pos = self._current_position()
        
        try:
            # Модификаторы
            modifiers = self._parse_modifiers()
            
            # Проверка на конструктор: ИмяКласса(
            if self._match("IDENTIFIER", class_name):
                next_pos = self.pos + 1
                if next_pos < len(self.tokens) and self.tokens[next_pos].lexeme == "(":
                    return self._parse_constructor(modifiers, class_name)
            
            # Тип возвращаемого значения / тип поля
            member_type = self._parse_type()
            
            # Имя метода / поля
            if not self.current_token or self.current_token.type != "IDENTIFIER":
                self._restore_position(start_pos)
                return None
            
            name = self.current_token.lexeme
            self._advance()
            
            # Метод: (
            if self._match("SEPARATOR", "("):
                return self._parse_method(pos, modifiers, member_type, name)
            
            # Поле: = или ;
            else:
                return self._parse_field(pos, modifiers, member_type, name)
        
        except ParseError:
            self._restore_position(start_pos)
            return None

    def _parse_constructor(self, modifiers: List[str], class_name: str) -> ConstructorDeclaration:
        """Парсинг конструктора.
        
        Grammar: modifiers? className '(' params? ')' ('throws' typeList)? block
        
        Пример: public Person(String name) throws Exception { ... }
        """
        pos = self._current_position()  # <-- Получаем позицию ЗДЕСЬ
        
        # Имя конструктора (должно совпадать с именем класса)
        name = self._expect("IDENTIFIER").lexeme
        
        # Параметры
        self._expect("SEPARATOR", "(")
        parameters = self._parse_parameters()
        self._expect("SEPARATOR", ")")
        
        # throws clause (опционально)
        throws = []
        if self._match("KEYWORD", "throws"):
            self._advance()
            throws = self._parse_throws_clause()  # <-- Используй _parse_throws_clause
        
        # Тело конструктора
        body = self._parse_block()
        
        return ConstructorDeclaration(
            node_type=NodeType.CONSTRUCTOR_DECLARATION,
            position=pos,
            name=name,
            parameters=parameters,
            body=body,
            modifiers=modifiers,
            throws=throws
        )




    def _parse_field(self, pos: Position, modifiers: List[str],
                     field_type: Type, name: str) -> FieldDeclaration:
        """Парсинг поля.
        
        Grammar: fieldDecl → modifier* type IDENTIFIER ('=' expr)? ';'
        """
        field = FieldDeclaration(
            NodeType.FIELD_DECLARATION,
            pos,
            field_type=field_type,
            name=name,
            modifiers=modifiers
        )
        
        # Инициализация
        if self._match("OPERATOR", "="):
            self._advance()
            field.value = self._parse_expression()
        
        self._expect("SEPARATOR", ";")
        return field

    def _parse_parameters(self) -> List[Parameter]:
        """Парсинг параметров метода.
        
        Grammar: params → param (',' param)*
                 param → type IDENTIFIER
        """
        parameters = []
        
        if self._match("SEPARATOR", ")"):
            return parameters
        
        while True:
            param_type = self._parse_type()
            
            if not self.current_token or self.current_token.type != "IDENTIFIER":
                break
            
            param_name = self.current_token.lexeme
            self._advance()
            
            param = Parameter(
                NodeType.PARAMETER,
                self._current_position(),
                param_type=param_type,
                name=param_name
            )
            parameters.append(param)
            
            if not self._match("SEPARATOR", ","):
                break
            self._advance()
        
        return parameters

    # ==================== Типы ====================

    def _parse_type(self) -> Type:
        """Парсинг типа.
        
        Grammar: type → primitiveType | IDENTIFIER | type '[]'
                 primitiveType → 'int' | 'long' | 'double' | 'float' 
                               | 'boolean' | 'char' | 'byte' | 'short' | 'void'
        """
        pos = self._current_position()
        
        if not self.current_token:
            raise UnexpectedTokenError("тип", "EOF", 1, 1)
        
        # Примитивы или идентификатор
        if self.current_token.type in ["KEYWORD", "IDENTIFIER"]:
            type_name = self.current_token.lexeme
            self._advance()
        else:
            raise UnexpectedTokenError(
                "тип",
                self.current_token.type,
                self.current_token.line,
                self.current_token.column
            )
        
        type_node = Type(NodeType.TYPE, pos, name=type_name)
        
        # Массив []
        if self._match("SEPARATOR", "["):
            self._advance()
            self._expect("SEPARATOR", "]")
            type_node.is_array = True
        
        return type_node

    # ==================== Блок и инструкции ====================

    def _parse_block(self) -> Block:
        """Парсинг блока кода.
        
        Grammar: block → '{' statement* '}'
        """
        pos = self._current_position()
        self._expect("SEPARATOR", "{")
        
        block = Block(NodeType.BLOCK, pos)
        
        while not self._match("SEPARATOR", "}"):
            if not self.current_token:
                raise ParseError("Незакрытый блок", pos.line, pos.column)
            
            stmt = self._parse_statement()
            if stmt:
                block.statements.append(stmt)
        
        self._expect("SEPARATOR", "}")
        return block

    def _parse_statement(self):
        """Парсинг инструкции.
        
        Grammar: statement → varDecl | exprStmt | ifStmt | whileStmt 
                        | doWhileStmt | forStmt | returnStmt 
                        | breakStmt | continueStmt | block
        """
        if not self.current_token:
            return None
        
        # Блок
        if self._match("SEPARATOR", "{"):
            return self._parse_block()
        # this() — вызов другого конструктора
        if (self._match("KEYWORD", "this") and self._peek_token() and self._peek_token().lexeme == "("):
            return self._parse_this_call()
        
        # super() — вызов конструктора родителя  
        if (self._match("KEYWORD", "super") and self._peek_token() and self._peek_token().lexeme == "("):
            return self._parse_super_call()
        # return
        if self._match("KEYWORD", "return"):
            return self._parse_return_statement()
        # throw (NEW!)
        if self._match("KEYWORD", "throw"):
            return self._parse_throw_statement()
        # if
        if self._match("KEYWORD", "if"):
            return self._parse_if_statement()
        # switch
        if self._match("KEYWORD", "switch"):
            return self._parse_switch_statement()
        # try-catch-finally (NEW!)
        if self._match("KEYWORD", "try"):
            return self._parse_try_statement()
        # while
        if self._match("KEYWORD", "while"):
            return self._parse_while_statement()
        
        # do-while (NEW!)
        if self._match("KEYWORD", "do"):
            return self._parse_do_while_statement()
        
        # for
        if self._match("KEYWORD", "for"):
            return self._parse_for_statement()
        
        # break (NEW!)
        if self._match("KEYWORD", "break"):
            return self._parse_break_statement()
        
        # continue (NEW!)
        if self._match("KEYWORD", "continue"):
            return self._parse_continue_statement()
        
        # Объявление переменной или выражение
        if self._is_variable_declaration():
            return self._parse_variable_declaration()
        
        # Выражение
        return self._parse_expression_statement()
    def _parse_switch_statement(self) -> SwitchStatement:
        """Парсинг switch.
        
        Grammar: 
            switchStmt → 'switch' '(' expr ')' '{' switchCase* '}'
            switchCase → 'case' expr ':' statement* 
                    | 'default' ':' statement*
        """
        pos = self._current_position()
        self._expect("KEYWORD", "switch")
        self._expect("SEPARATOR", "(")
        
        # Выражение switch
        expression = self._parse_expression()
        
        self._expect("SEPARATOR", ")")
        self._expect("SEPARATOR", "{")
        
        # Парсим case'ы
        cases = []
        while not self._match("SEPARATOR", "}"):
            if not self.current_token:
                raise ParseError("Незакрытый switch", pos.line, pos.column)
            
            case = self._parse_switch_case()
            if case:
                cases.append(case)
        
        self._expect("SEPARATOR", "}")
        
        return SwitchStatement(
            node_type=NodeType.SWITCH_STATEMENT,
            position=pos,
            expression=expression,
            cases=cases
        )


    def _parse_switch_case(self) -> Optional[SwitchCase]:
        """Парсинг одного case или default."""
        pos = self._current_position()
        
        # default:
        if self._match("KEYWORD", "default"):
            self._advance()
            self._expect("OPERATOR", ":")
            
            statements = self._parse_case_statements()
            
            return SwitchCase(
                node_type=NodeType.SWITCH_CASE,
                position=pos,
                case_label=None,  # ПЕРЕИМЕНОВАНО
                statements=statements,
                is_default=True
            )
        
        # case expr:
        if self._match("KEYWORD", "case"):
            self._advance()
            
            label = self._parse_expression()
            
            self._expect("OPERATOR", ":")
            
            statements = self._parse_case_statements()
            
            return SwitchCase(
                node_type=NodeType.SWITCH_CASE,
                position=pos,
                case_label=label,  # ПЕРЕИМЕНОВАНО
                statements=statements,
                is_default=False
            )
        
        return None



    def _parse_case_statements(self) -> List[ASTNode]:
        """Парсинг statements внутри case до следующего case/default/}."""
        statements = []
        
        while self.current_token:
            # Останавливаемся на case, default или }
            if self._match("KEYWORD", "case"):
                break
            if self._match("KEYWORD", "default"):
                break
            if self._match("SEPARATOR", "}"):
                break
            
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return statements
    def _is_variable_declaration(self) -> bool:
        """Проверка, является ли текущая позиция объявлением переменной."""
        start_pos = self._save_position()
        
        print(f"[DEBUG] _is_variable_declaration: token={self.current_token}")
        
        try:
            # Пробуем распарсить тип
            parsed_type = self._parse_type()
            print(f"[DEBUG] Parsed type: {parsed_type.name}, is_array={parsed_type.is_array}")
            print(f"[DEBUG] After type, token={self.current_token}")
            
            # После типа должен быть идентификатор
            if self.current_token and self.current_token.type == "IDENTIFIER":
                next_pos = self.pos + 1
                if next_pos < len(self.tokens):
                    next_lexeme = self.tokens[next_pos].lexeme
                    print(f"[DEBUG] Identifier={self.current_token.lexeme}, next={next_lexeme}")
                    result = next_lexeme in ["=", ";", ","]
                    print(f"[DEBUG] Is var declaration: {result}")
                    return result
            print(f"[DEBUG] Not a var declaration (no identifier after type)")
            return False
        except Exception as e:
            print(f"[DEBUG] Exception in _is_variable_declaration: {e}")
            return False
        finally:
            self._restore_position(start_pos)

    def _parse_this_call(self) -> ThisCall:
        """Парсинг this(args) — вызов другого конструктора.
        
        Пример: this("default", 0);
        """
        pos = self._current_position()
        self._expect("KEYWORD", "this")
        self._expect("SEPARATOR", "(")
        
        arguments = self._parse_arguments()
        
        self._expect("SEPARATOR", ")")
        self._expect("SEPARATOR", ";")
        
        return ThisCall(
            node_type=NodeType.THIS_CALL,
            position=pos,
            arguments=arguments
        )


    def _parse_super_call(self) -> SuperCall:
        """Парсинг super(args) — вызов конструктора родителя.
        
        Пример: super(x, y);
        """
        pos = self._current_position()
        self._expect("KEYWORD", "super")
        self._expect("SEPARATOR", "(")
        
        arguments = self._parse_arguments()
        
        self._expect("SEPARATOR", ")")
        self._expect("SEPARATOR", ";")
        
        return SuperCall(
            node_type=NodeType.SUPER_CALL,
            position=pos,
            arguments=arguments
        )
    def _parse_variable_declaration(self) -> VariableDeclaration:
        """Парсинг объявления локальной переменной."""
        pos = self._current_position()
        
        print(f"[DEBUG] _parse_variable_declaration START: token={self.current_token}")
        
        var_type = self._parse_type()
        print(f"[DEBUG] Parsed var_type: {var_type.name}, is_array={var_type.is_array}")
        print(f"[DEBUG] After type, token={self.current_token}")
        
        var_name = self._expect("IDENTIFIER").lexeme
        print(f"[DEBUG] var_name={var_name}, token={self.current_token}")
        
        var_decl = VariableDeclaration(
            NodeType.VARIABLE_DECLARATION,
            pos,
            name=var_name
        )
        var_decl.var_type = var_type
        
        if self._match("OPERATOR", "="):
            self._advance()
            print(f"[DEBUG] Parsing initializer, token={self.current_token}")
            var_decl.value = self._parse_expression()
            print(f"[DEBUG] After initializer, token={self.current_token}")
        
        print(f"[DEBUG] Expecting semicolon, token={self.current_token}")
        self._expect("SEPARATOR", ";")
        print(f"[DEBUG] Variable declaration complete: {var_name}")
        
        return var_decl


    def _parse_expression_statement(self):
        """Парсинг выражения как инструкции.
        
        Grammar: exprStmt → expr ';'
        """
        pos = self._current_position()
        expr = self._parse_expression()
        
        if self._match("SEPARATOR", ";"):
            self._advance()
        
        if expr:
            stmt = ASTNode(NodeType.EXPRESSION_STATEMENT, pos)
            stmt.add_child(expr)
            return stmt
        return None

    def _parse_return_statement(self):
        """Парсинг return.
        
        Grammar: returnStmt → 'return' expr? ';'
        """
        pos = self._current_position()
        self._expect("KEYWORD", "return")
        
        return_node = ASTNode(NodeType.RETURN_STATEMENT, pos)
        
        if not self._match("SEPARATOR", ";"):
            expr = self._parse_expression()
            if expr:
                return_node.add_child(expr)
        
        self._expect("SEPARATOR", ";")
        return return_node

    def _parse_if_statement(self):
        """Парсинг if-else.
        
        Grammar: ifStmt → 'if' '(' expr ')' statement ('else' statement)?
        """
        pos = self._current_position()
        self._expect("KEYWORD", "if")
        self._expect("SEPARATOR", "(")
        
        condition = self._parse_expression()
        
        self._expect("SEPARATOR", ")")
        
        then_branch = self._parse_statement()
        
        if_node = ASTNode(NodeType.IF_STATEMENT, pos)
        if_node.add_child(condition)
        if_node.add_child(then_branch)
        
        if self._match("KEYWORD", "else"):
            self._advance()
            else_branch = self._parse_statement()
            if_node.add_child(else_branch)
        
        return if_node

    def _parse_while_statement(self):
        """Парсинг while.
        
        Grammar: whileStmt → 'while' '(' expr ')' statement
        """
        pos = self._current_position()
        self._expect("KEYWORD", "while")
        self._expect("SEPARATOR", "(")
        
        condition = self._parse_expression()
        
        self._expect("SEPARATOR", ")")
        
        body = self._parse_statement()
        
        while_node = ASTNode(NodeType.WHILE_STATEMENT, pos)
        while_node.add_child(condition)
        while_node.add_child(body)
        
        return while_node

    def _parse_for_statement(self):
        """Парсинг for или for-each.
        
        Grammar: 
            forStmt → 'for' '(' forControl ')' statement
            forControl → forInit? ';' expr? ';' expr?    (обычный for)
                    | type IDENTIFIER ':' expr         (for-each)
        """
        pos = self._current_position()
        self._expect("KEYWORD", "for")
        self._expect("SEPARATOR", "(")
    
        # Пробуем определить: это for-each или обычный for?
        if self._is_for_each():
            return self._parse_for_each_body(pos)
        else:
            return self._parse_regular_for_body(pos)
    def _is_for_each(self) -> bool:
        """Проверяет, является ли текущий for циклом for-each.
        
        for-each: for (Type var : iterable)
        regular:  for (init; condition; update)
        
        Отличие: в for-each после "Type var" идёт ":", а не "=" или ";"
        """
        saved_pos = self._save_position()
        
        try:
            # Пробуем прочитать тип
            self._parse_type()
            
            # Должен быть идентификатор
            if not self._match("IDENTIFIER"):
                return False
            self._advance()
            
            # Если после идентификатора ":" — это for-each
            return self._match("OPERATOR", ":")
        except:
            return False
        finally:
            self._restore_position(saved_pos)

    def _parse_for_each_body(self, pos: Position) -> ForEachStatement:
        """Парсинг тела for-each после 'for ('.
        
        Grammar: type IDENTIFIER ':' expr ')' statement
        """
        # Тип переменной
        var_type = self._parse_type()
        
        # Имя переменной
        var_name = self._expect("IDENTIFIER").lexeme
        
        # Двоеточие
        self._expect("OPERATOR", ":")
        
        # Итерируемое выражение
        iterable = self._parse_expression()
        
        # Закрывающая скобка
        self._expect("SEPARATOR", ")")
        
        # Тело цикла
        body = self._parse_statement()
        
        return ForEachStatement(
            node_type=NodeType.FOR_EACH_STATEMENT,
            position=pos,
            var_type=var_type,
            var_name=var_name,
            iterable=iterable,
            body=body
        )

    def _parse_regular_for_body(self, pos: Position):
        """Парсинг тела обычного for после 'for ('.
        
        Grammar: forInit? ';' expr? ';' expr? ')' statement
        """
        for_node = ASTNode(NodeType.FOR_STATEMENT, pos)
        
        # init
        if not self._match("SEPARATOR", ";"):
            if self._is_variable_declaration():
                init = self._parse_for_var_declaration()
            else:
                init = self._parse_expression()
            for_node.add_child(init)
        else:
            for_node.add_child(ASTNode(NodeType.IDENTIFIER, pos, name=""))
        
        self._expect("SEPARATOR", ";")
        
        # condition
        if not self._match("SEPARATOR", ";"):
            condition = self._parse_expression()
            for_node.add_child(condition)
        else:
            for_node.add_child(ASTNode(NodeType.IDENTIFIER, pos, name=""))
        
        self._expect("SEPARATOR", ";")
        
        # update
        if not self._match("SEPARATOR", ")"):
            update = self._parse_expression()
            for_node.add_child(update)
        else:
            for_node.add_child(ASTNode(NodeType.IDENTIFIER, pos, name=""))
        
        self._expect("SEPARATOR", ")")
        
        # body
        body = self._parse_statement()
        for_node.add_child(body)
        
        return for_node

    def _parse_for_var_declaration(self) -> VariableDeclaration:
        """Парсинг объявления переменной в for (без точки с запятой)."""
        pos = self._current_position()
        
        var_type = self._parse_type()
        var_name = self._expect("IDENTIFIER").lexeme
        
        var_decl = VariableDeclaration(
            NodeType.VARIABLE_DECLARATION,
            pos,
            name=var_name
        )
        var_decl.var_type = var_type
        
        if self._match("OPERATOR", "="):
            self._advance()
            var_decl.value = self._parse_expression()
        
        return var_decl

    # ==================== Выражения ====================

    def _parse_expression(self):
        """Парсинг выражения.
        
        Grammar: expr → assignment
        """
        return self._parse_assignment()

    def _parse_assignment(self):
        """Парсинг присваивания.
        
        Grammar: assignment → IDENTIFIER assignOp assignment | logicOr
                 assignOp → '=' | '+=' | '-=' | '*=' | '/='
        """
        pos = self._current_position()
        left = self._parse_ternary()
        
        if left is None:
            return None
        
        assignment_ops = ["=", "+=", "-=", "*=", "/="]
        
        if (self.current_token and 
            self.current_token.type == "OPERATOR" and
            self.current_token.lexeme in assignment_ops):
            
            operator = self.current_token.lexeme
            self._advance()
            right = self._parse_assignment()
            
            if right:
                return Assignment(
                    NodeType.ASSIGNMENT,
                    pos,
                    variable=left,
                    value=right,
                    operator=operator
                )
        
        return left
    def _parse_ternary(self):
        """Парсинг тернарного оператора.
        
        Grammar: ternary → logicOr ('?' expression ':' ternary)?
        
        Пример: a > b ? a : b
        
        Приоритет: тернарный оператор имеет очень низкий приоритет,
        ниже чем логические операции, но выше чем присваивание.
        """
        pos = self._current_position()
        condition = self._parse_logic_or()
        
        if condition is None:
            return None
        
        # Проверяем наличие ?
        if self._match("OPERATOR", "?"):
            self._advance()
            
            # Выражение для true-ветки
            then_expr = self._parse_expression()
            
            # Ожидаем :
            self._expect("OPERATOR", ":")
            
            # Выражение для false-ветки (рекурсивно для правой ассоциативности)
            else_expr = self._parse_ternary()
            
            return TernaryOperation(
                node_type=NodeType.TERNARY_OPERATION,
                position=pos,
                condition=condition,
                then_expr=then_expr,
                else_expr=else_expr
            )
        
        return condition

    def _parse_logic_or(self):
        """Парсинг логического ИЛИ.
        
        Grammar: logicOr → logicAnd ('||' logicAnd)*
        """
        left = self._parse_logic_and()
        
        while (self.current_token and
               self.current_token.type == "OPERATOR" and
               self.current_token.lexeme == "||"):
            
            operator = self.current_token.lexeme
            pos = self._current_position()
            self._advance()
            right = self._parse_logic_and()
            
            if right:
                left = BinaryOperation(
                    NodeType.BINARY_OPERATION,
                    pos,
                    operator=operator,
                    left=left,
                    right=right
                )
        
        return left

    def _parse_logic_and(self):
        """Парсинг логического И.
        
        Grammar: logicAnd → equality ('&&' equality)*
        """
        left = self._parse_equality()
        
        while (self.current_token and
               self.current_token.type == "OPERATOR" and
               self.current_token.lexeme == "&&"):
            
            operator = self.current_token.lexeme
            pos = self._current_position()
            self._advance()
            right = self._parse_equality()
            
            if right:
                left = BinaryOperation(
                    NodeType.BINARY_OPERATION,
                    pos,
                    operator=operator,
                    left=left,
                    right=right
                )
        
        return left

    def _parse_equality(self):
        """Парсинг равенства/неравенства.
        
        Grammar: equality → comparison (('==' | '!=') comparison)*
        """
        left = self._parse_comparison()
        
        while (self.current_token and
               self.current_token.type == "OPERATOR" and
               self.current_token.lexeme in ["==", "!="]):
            
            operator = self.current_token.lexeme
            pos = self._current_position()
            self._advance()
            right = self._parse_comparison()
            
            if right:
                left = BinaryOperation(
                    NodeType.BINARY_OPERATION,
                    pos,
                    operator=operator,
                    left=left,
                    right=right
                )
        
        return left

    def _parse_comparison(self):
        """Парсинг сравнения.
        
        Grammar: comparison → addition (('<' | '>' | '<=' | '>=' | 'instanceof') addition)*
        """
        left = self._parse_addition()
        
        while self.current_token:
            # Обычные операторы сравнения
            if (self.current_token.type == "OPERATOR" and
                self.current_token.lexeme in ["<", ">", "<=", ">="]):
                
                operator = self.current_token.lexeme
                pos = self._current_position()
                self._advance()
                right = self._parse_addition()
                
                if right:
                    left = BinaryOperation(
                        NodeType.BINARY_OPERATION,
                        pos,
                        operator=operator,
                        left=left,
                        right=right
                    )
            
            # instanceof (NEW!)
            elif self._match("KEYWORD", "instanceof"):
                pos = self._current_position()
                self._advance()
                
                # Правая часть — тип (String, Integer, MyClass и т.д.)
                check_type = self._parse_type()
                
                left = InstanceofExpression(
                    node_type=NodeType.INSTANCEOF_EXPRESSION,
                    position=pos,
                    expression=left,
                    check_type=check_type
                )
            
            else:
                break
        
        return left

    def _parse_addition(self):
        """Парсинг сложения/вычитания.
        
        Grammar: addition → multiplication (('+' | '-') multiplication)*
        """
        left = self._parse_multiplication()
        
        while (self.current_token and
               self.current_token.type == "OPERATOR" and
               self.current_token.lexeme in ["+", "-"]):
            
            operator = self.current_token.lexeme
            pos = self._current_position()
            self._advance()
            right = self._parse_multiplication()
            
            if right:
                left = BinaryOperation(
                    NodeType.BINARY_OPERATION,
                    pos,
                    operator=operator,
                    left=left,
                    right=right
                )
        
        return left

    def _parse_multiplication(self):
        """Парсинг умножения/деления.
        
        Grammar: multiplication → unary (('*' | '/' | '%') unary)*
        """
        left = self._parse_unary()
        
        while (self.current_token and
               self.current_token.type == "OPERATOR" and
               self.current_token.lexeme in ["*", "/", "%"]):
            
            operator = self.current_token.lexeme
            pos = self._current_position()
            self._advance()
            right = self._parse_unary()
            
            if right:
                left = BinaryOperation(
                    NodeType.BINARY_OPERATION,
                    pos,
                    operator=operator,
                    left=left,
                    right=right
                )
        
        return left

    def _parse_unary(self):
        """Парсинг унарных операций.
        
        Grammar: unary → ('!' | '-' | '++' | '--') unary | postfix
        """
        pos = self._current_position()
        
        if (self.current_token and
            self.current_token.type == "OPERATOR" and
            self.current_token.lexeme in ["!", "-", "++", "--"]):
            
            operator = self.current_token.lexeme
            self._advance()
            operand = self._parse_unary()
            
            if operand:
                return UnaryOperation(
                    node_type=NodeType.UNARY_OPERATION,
                    position=pos,
                    operator=operator,
                    operand=operand,
                    is_postfix=False
                )
        
        return self._parse_postfix()


    def _parse_postfix(self):
        """Парсинг постфиксных операций.
        
        Grammar: postfix → primary ('++' | '--')?
        """
        pos = self._current_position()
        expr = self._parse_primary()
        
        if expr is None:
            return None
        
        if (self.current_token and
            self.current_token.type == "OPERATOR" and
            self.current_token.lexeme in ["++", "--"]):
            
            operator = self.current_token.lexeme
            self._advance()
            
            return UnaryOperation(
                node_type=NodeType.UNARY_OPERATION,
                position=pos,
                operator=operator,
                operand=expr,
                is_postfix=True
            )
        
        return expr
    def _parse_access_chain(self, node, pos):
        """Парсинг цепочки доступа (вызовы методов, доступ к полям, индексация).
        
        Примеры:
            .field
            obj.method()
            obj.field.method()
            arr[0]
            arr[i].field
        """
        while self.current_token:
            # Вызов метода: node(...)
            if self._match("SEPARATOR", "("):
                node = self._parse_method_call_args(node, pos)
            
            # Доступ к полю: node.field
            elif self._match("SEPARATOR", "."):
                self._advance()
                
                if not self._match("IDENTIFIER"):
                    break
                
                field_name = self.current_token.lexeme
                field_pos = self._current_position()
                self._advance()
                
                # Создаём узел доступа к полю
                field_access = ASTNode(NodeType.FIELD_ACCESS, pos)
                field_access.add_child(node)
                field_access.add_child(Identifier(NodeType.IDENTIFIER, field_pos, name=field_name))
                node = field_access
            
            # Доступ к элементу массива: node[index]
            elif self._match("SEPARATOR", "["):
                self._advance()
                index = self._parse_expression()
                self._expect("SEPARATOR", "]")
                
                node = ArrayAccess(
                    node_type=NodeType.ARRAY_ACCESS,
                    position=pos,
                    array=node,
                    index=index
                )
            
            else:
                break
        
        return node



    def _parse_primary(self):
        """Парсинг первичных выражений."""
        pos = self._current_position()
        
        if not self.current_token:
            return None
        
        # this
        if self._match("KEYWORD", "this"):
            self._advance()
            node = Identifier(NodeType.IDENTIFIER, pos, name="this")
            return self._parse_access_chain(node, pos)
        
        # super
        if self._match("KEYWORD", "super"):
            self._advance()
            node = Identifier(NodeType.IDENTIFIER, pos, name="super")
            return self._parse_access_chain(node, pos)
        
        # new - НЕ ПРОДВИГАЕМСЯ, пусть _parse_new_expression сам съест new
        if self._match("KEYWORD", "new"):
            return self._parse_new_expression()
        
        # Литералы
        if self.current_token.type in ["INT_LITERAL", "FLOAT_LITERAL", 
                                        "STRING_LITERAL", "CHAR_LITERAL",
                                        "BOOLEAN_LITERAL", "NULL_LITERAL"]:
            token = self.current_token
            self._advance()
            literal_type = token.type.lower().replace("_literal", "")
            return Literal(NodeType.LITERAL, pos, value=token.lexeme, literal_type=literal_type)
        
        # true/false/null как ключевые слова
        if self._match("KEYWORD", "true") or self._match("KEYWORD", "false"):
            value = self.current_token.lexeme
            self._advance()
            return Literal(NodeType.LITERAL, pos, value=value, literal_type="boolean")
        
        if self._match("KEYWORD", "null"):
            self._advance()
            return Literal(NodeType.LITERAL, pos, value="null", literal_type="null")
        
        # Идентификатор
        if self._match("IDENTIFIER"):
            name = self.current_token.lexeme
            self._advance()
            node = Identifier(NodeType.IDENTIFIER, pos, name=name)
            return self._parse_access_chain(node, pos)
        
        # Скобки
        if self._match("SEPARATOR", "("):
            return self._parse_parenthesized_or_cast()
        
        return None

    def _parse_parenthesized_or_cast(self):
        """Парсинг скобочного выражения или cast.
        
        Различаем:
        - (Type) expr  → CastExpression
        - (expr)       → группировка
        
        Эвристика: если после '(' идёт тип (IDENTIFIER или примитив),
        а после него ')' — это cast.
        """
        pos = self._current_position()
        self._expect("SEPARATOR", "(")
        
        # Пробуем определить: это cast или группировка?
        if self._is_cast():
            return self._parse_cast(pos)
        else:
            # Обычная группировка
            expr = self._parse_expression()
            self._expect("SEPARATOR", ")")
            return expr


    def _is_cast(self) -> bool:
        """Проверяет, является ли текущая конструкция cast.
        
        Cast: (Type) expr
        Группировка: (expr)
        
        Эвристика: после '(' идёт тип, затем ')'.
        Типы: примитивы (int, long...) или идентификаторы (String, MyClass).
        """
        saved_pos = self._save_position()
        
        try:
            # После '(' должен быть тип
            if not self.current_token:
                return False
            
            # Примитивные типы — точно cast
            primitives = {"int", "long", "double", "float", "boolean", 
                        "char", "byte", "short"}
            
            if (self.current_token.type == "KEYWORD" and 
                self.current_token.lexeme in primitives):
                self._advance()
                # Проверяем [] для массивов
                if self._match("SEPARATOR", "["):
                    self._advance()
                    if not self._match("SEPARATOR", "]"):
                        return False
                    self._advance()
                return self._match("SEPARATOR", ")")
            
            # Идентификатор — может быть cast или переменная
            if self.current_token.type == "IDENTIFIER":
                self._advance()
                # Проверяем [] для массивов
                if self._match("SEPARATOR", "["):
                    self._advance()
                    if not self._match("SEPARATOR", "]"):
                        return False
                    self._advance()
                # Если после идентификатора ')' — это cast
                # Но нужно убедиться, что после ')' идёт выражение, не оператор
                if self._match("SEPARATOR", ")"):
                    # Смотрим что после ')'
                    next_tok = self._peek_token()
                    if next_tok:
                        # Если после ')' идёт идентификатор, литерал, '(' или унарный оператор — cast
                        if next_tok.type in ["IDENTIFIER", "INT_LITERAL", "FLOAT_LITERAL", 
                                            "STRING_LITERAL", "CHAR_LITERAL"]:
                            return True
                        if next_tok.lexeme in ["(", "!", "-", "++", "--", "new", "this", "super"]:
                            return True
                        if next_tok.type == "KEYWORD" and next_tok.lexeme in ["new", "this", "super", "true", "false", "null"]:
                            return True
                    return False
            
            return False
        except:
            return False
        finally:
            self._restore_position(saved_pos)


    def _parse_cast(self, pos: Position) -> CastExpression:
        """Парсинг cast выражения.
        
        Grammar: '(' type ')' unaryExpression
        
        Пример: (String) obj
        """
        # Тип
        target_type = self._parse_type()
        
        # Закрывающая скобка
        self._expect("SEPARATOR", ")")
        
        # Выражение (с высоким приоритетом — unary)
        expression = self._parse_unary()
        
        return CastExpression(
            node_type=NodeType.CAST_EXPRESSION,
            position=pos,
            target_type=target_type,
            expression=expression
        )

    def _parse_method(self, pos: Position, modifiers: List[str],
                    return_type: Type, name: str) -> MethodDeclaration:
        """Парсинг метода.
        
        Grammar: methodDecl → modifier* type IDENTIFIER '(' params? ')' ('throws' type (',' type)*)? block
        """
        method = MethodDeclaration(
            NodeType.METHOD_DECLARATION,
            pos,
            name=name,
            return_type=return_type,
            modifiers=modifiers
        )
        
        self._expect("SEPARATOR", "(")
        method.parameters = self._parse_parameters()
        self._expect("SEPARATOR", ")")
        
        # throws clause (NEW!)
        if self._match("KEYWORD", "throws"):
            self._advance()
            method.throws = self._parse_throws_clause()
        
        method.body = self._parse_block()
        
        return method
    
    def _parse_throws_clause(self) -> List[Type]:
        """Парсинг throws clause.
        
        Grammar: throwsClause → 'throws' type (',' type)*
        
        Пример: throws IOException, SQLException
        """
        exceptions = []
        
        # Первый тип исключения
        exc_type = self._parse_type()
        exceptions.append(exc_type)
        
        # Остальные через запятую
        while self._match("SEPARATOR", ","):
            self._advance()
            exc_type = self._parse_type()
            exceptions.append(exc_type)
        
        return exceptions

    def _parse_method_call_args(self, target, pos) -> MethodCall:
        """Парсинг аргументов вызова метода.
        
        Grammar: methodCall → target '(' args? ')'
                 args → expr (',' expr)*
        """
        # Извлекаем имя метода из target
        if isinstance(target, Identifier):
            method_name = target.name
        elif hasattr(target, 'children') and target.children:
            # Для field_access берём последний child как имя метода
            last_child = target.children[-1]
            if isinstance(last_child, Identifier):
                method_name = last_child.name
            else:
                method_name = "unknown"
        else:
            method_name = "unknown"
        
        method_call = MethodCall(
            NodeType.METHOD_CALL,
            pos,
            method_name=method_name
        )
        
        # Если target - это field_access, добавляем объект как child
        if isinstance(target, ASTNode) and target.node_type == NodeType.FIELD_ACCESS:
            method_call.add_child(target.children[0] if target.children else target)
        
        self._expect("SEPARATOR", "(")
        
        # Аргументы
        if not self._match("SEPARATOR", ")"):
            while True:
                arg = self._parse_expression()
                if arg:
                    method_call.arguments.append(arg)
                
                if not self._match("SEPARATOR", ","):
                    break
                self._advance()
        
        self._expect("SEPARATOR", ")")
        
        return method_call

    def _parse_new_expression(self):
        """Парсинг создания объекта или массива.
        
        Grammar: newExpr → 'new' IDENTIFIER '(' args? ')' 
                        | 'new' type '[' expr ']'
        """
        pos = self._current_position()
        self._expect("KEYWORD", "new")
        
        # Парсим тип (int, String, MyClass и т.д.)
        if not self.current_token:
            raise UnexpectedTokenError("тип", "EOF", pos.line, pos.column)
        
        type_name = self.current_token.lexeme
        type_pos = self._current_position()
        self._advance()
        
        # Создание массива: new int[10]
        if self._match("SEPARATOR", "["):
            self._advance()
            size = self._parse_expression()
            self._expect("SEPARATOR", "]")
            
            # Используем правильный класс ArrayCreation
            element_type = Type(NodeType.TYPE, type_pos, name=type_name)
            return ArrayCreation(
                node_type=NodeType.ARRAY_CREATION,
                position=pos,
                element_type=element_type,
                size=size
            )
        
        # Создание объекта: new MyClass()
        class_type = Type(NodeType.TYPE, type_pos, name=type_name)
        
        self._expect("SEPARATOR", "(")
        
        arguments = []
        if not self._match("SEPARATOR", ")"):
            while True:
                arg = self._parse_expression()
                if arg:
                    arguments.append(arg)
                
                if not self._match("SEPARATOR", ","):
                    break
                self._advance()
        
        self._expect("SEPARATOR", ")")
        
        # Используем правильный класс ObjectCreation
        return ObjectCreation(
            node_type=NodeType.OBJECT_CREATION,
            position=pos,
            class_type=class_type,
            arguments=arguments
        )

    def _parse_throw_statement(self) -> ThrowStatement:
        """Парсинг throw."""
        pos = self._current_position()
        self._expect("KEYWORD", "throw")
        
        print(f"[DEBUG] throw: current_token = {self.current_token}")
        
        # Выражение (обычно new Exception(...) или переменная)
        expression = self._parse_expression()
        
        print(f"[DEBUG] throw: expression = {expression}")
        print(f"[DEBUG] throw: expression type = {type(expression)}")
        
        self._expect("SEPARATOR", ";")
        
        result = ThrowStatement(
            node_type=NodeType.THROW_STATEMENT,
            position=pos,
            expression=expression
        )
        
        print(f"[DEBUG] throw: result.expression = {result.expression}")
        
        return result

    def _parse_do_while_statement(self):
        """Парсинг do-while.
        Grammar: doWhileStmt → 'do' statement 'while' '(' expr ')' ';'
        
        Структура AST:
        - children[0]: Block/Statement - тело цикла
        - children[1]: Expression - условие
        """
        pos = self._current_position()
        self._expect("KEYWORD", "do")
        
        # Тело цикла
        body = self._parse_statement()
        
        # while (condition)
        self._expect("KEYWORD", "while")
        self._expect("SEPARATOR", "(")
        condition = self._parse_expression()
        self._expect("SEPARATOR", ")")
        self._expect("SEPARATOR", ";")
        
        do_while_node = DoWhileStatement(NodeType.DO_WHILE_STATEMENT, pos)
        do_while_node.add_child(body)
        do_while_node.add_child(condition)
        
        return do_while_node
    def _parse_break_statement(self):
        """Парсинг break.
        
        Grammar: breakStmt → 'break' IDENTIFIER? ';'
        
        Поддерживает:
        - break;
        - break label;  (для выхода из помеченного цикла)
        """
        pos = self._current_position()
        self._expect("KEYWORD", "break")
        
        # Опциональная метка
        label = None
        if self._match("IDENTIFIER"):
            label = self.current_token.lexeme
            self._advance()
        
        self._expect("SEPARATOR", ";")
        
        return BreakStatement(NodeType.BREAK_STATEMENT, pos, label=label)
    def _parse_continue_statement(self):
        """Парсинг continue.
        
        Grammar: continueStmt → 'continue' IDENTIFIER? ';'
        
        Поддерживает:
        - continue;
        - continue label;  (для продолжения помеченного цикла)
        """
        pos = self._current_position()
        self._expect("KEYWORD", "continue")
        
        # Опциональная метка
        label = None
        if self._match("IDENTIFIER"):
            label = self.current_token.lexeme
            self._advance()
        
        self._expect("SEPARATOR", ";")
        
        return ContinueStatement(NodeType.CONTINUE_STATEMENT, pos, label=label)
    def _parse_try_statement(self) -> TryStatement:
        """Парсинг try-catch-finally.
        
        Grammar: 
            tryStmt → 'try' block catchClause* ('finally' block)?
            catchClause → 'catch' '(' type IDENTIFIER ')' block
        
        Примеры:
            try { ... } catch (Exception e) { ... }
            try { ... } catch (IOException e) { ... } catch (SQLException e) { ... }
            try { ... } finally { ... }
            try { ... } catch (Exception e) { ... } finally { ... }
        """
        pos = self._current_position()
        self._expect("KEYWORD", "try")
        
        # Блок try
        try_block = self._parse_block()
        
        # Список catch clauses
        catch_clauses = []
        while self._match("KEYWORD", "catch"):
            catch_clause = self._parse_catch_clause()
            catch_clauses.append(catch_clause)
        
        # Опциональный finally
        finally_block = None
        if self._match("KEYWORD", "finally"):
            self._advance()
            finally_block = self._parse_block()
        
        # Проверка: должен быть хотя бы один catch или finally
        if not catch_clauses and not finally_block:
            raise ParseError(
                "try statement must have at least one catch or finally block",
                pos.line, pos.column
            )
        
        return TryStatement(
            node_type=NodeType.TRY_STATEMENT,
            position=pos,
            try_block=try_block,
            catch_clauses=catch_clauses,
            finally_block=finally_block
        )


    def _parse_catch_clause(self) -> CatchClause:
        """Парсинг catch clause.
        
        Grammar: catchClause → 'catch' '(' type IDENTIFIER ')' block
        
        Пример: catch (IOException e) { ... }
        """
        pos = self._current_position()
        self._expect("KEYWORD", "catch")
        self._expect("SEPARATOR", "(")
        
        # Тип исключения
        exception_type = self._parse_type()
        
        # Имя переменной
        exception_name = self._expect("IDENTIFIER").lexeme
        
        self._expect("SEPARATOR", ")")
        
        # Тело catch
        body = self._parse_block()
        
        return CatchClause(
            node_type=NodeType.CATCH_CLAUSE,
            position=pos,
            exception_type=exception_type,
            exception_name=exception_name,
            body=body
        )
