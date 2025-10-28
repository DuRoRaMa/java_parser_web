class ParseError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"[{line}:{column}] {message}")
        self.line = line
        self.column = column
        self.message = message

class UnexpectedTokenError(ParseError):
    def __init__(self, expected: str, actual: str, line: int, column: int):
        super().__init__(f"Ожидался {expected}, но получен {actual}", line, column)
        self.expected = expected
        self.actual = actual