"""(english version in the bask)
RoboSkill DSL Lexer - 词法分析器
将 DSL 源代码转换为 Token 流
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # 标识符和字面量
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    LIST_START = auto()
    LIST_END = auto()
    MAP_START = auto()
    MAP_END = auto()
    MAP_COLON = auto()

    # 关键字
    SKILL = auto()
    FN = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    ON = auto()
    IN = auto()
    WITH = auto()
    IMPORT = auto()
    EXPORT = auto()
    PARALLEL = auto()
    AS = auto()
    LET = auto()
    NIL = auto()

    # 动作关键字
    MOVE = auto()
    ROTATE = auto()
    GRAB = auto()
    RELEASE = auto()
    SPEAK = auto()
    LIGHT = auto()
    WAIT = auto()
    SLEEP = auto()

    # 感知关键字
    SENSE = auto()
    VISION = auto()
    VOICE = auto()
    AI = auto()
    DETECT = auto()
    RECOGNIZE = auto()
    PLAN = auto()
    PREDICT = auto()
    FOLLOW = auto()

    # 运算符
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    CARET = auto()

    # 比较运算符
    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()

    # 逻辑运算符
    AND = auto()
    OR = auto()
    NOT = auto()

    # 赋值
    ASSIGN = auto()
    ARROW = auto()

    # 分隔符
    COMMA = auto()
    DOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    NEWLINE = auto()
    COLON = auto()
    LBRACKET = auto()
    RBRACKET = auto()

    # 特殊
    COMMENT = auto()
    EOF = auto()
    ERROR = auto()


@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

    @property
    def lexeme(self):
        """兼容属性 - 返回 token 的文本表示"""
        return self.value if self.value is not None else ""

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"


class LexerError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at {line}:{column}: {message}")


class Lexer:
    """RoboSkill DSL 词法分析器"""

    KEYWORDS = {
        # 核心关键字
        'skill': TokenType.SKILL,
        'fn': TokenType.FN,
        'return': TokenType.RETURN,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'for': TokenType.FOR,
        'while': TokenType.WHILE,
        'on': TokenType.ON,
        'let': TokenType.LET,
        'in': TokenType.IN,
        'with': TokenType.WITH,
        'import': TokenType.IMPORT,
        'export': TokenType.EXPORT,
        'parallel': TokenType.PARALLEL,
        'as': TokenType.AS,
        'true': TokenType.BOOLEAN,
        'false': TokenType.BOOLEAN,
        'nil': TokenType.NIL,

        # 动作关键字
        'move': TokenType.MOVE,
        'rotate': TokenType.ROTATE,
        'grab': TokenType.GRAB,
        'release': TokenType.RELEASE,
        'speak': TokenType.SPEAK,
        'light': TokenType.LIGHT,
        'wait': TokenType.WAIT,
        'sleep': TokenType.SLEEP,

        # 感知关键字
        'sense': TokenType.SENSE,
        'vision': TokenType.VISION,
        'voice': TokenType.VOICE,
        'ai': TokenType.AI,
        'detect': TokenType.DETECT,
        'recognize': TokenType.RECOGNIZE,
        'plan': TokenType.PLAN,
        'predict': TokenType.PREDICT,
        'follow': TokenType.FOLLOW,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_column = 1

    def tokenize(self) -> List[Token]:
        """执行词法分析，返回 Token 列表"""
        while not self.is_at_end():
            self.start = self.current
            self.start_column = self.column
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def scan_token(self):
        """扫描单个 Token"""
        c = self.advance()

        # 单字符 tokens
        token_map = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.PERCENT,
            '^': TokenType.CARET,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LIST_START,
            ']': TokenType.LIST_END,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            ':': TokenType.MAP_COLON,
            '.': TokenType.DOT,
        }

        if c in token_map:
            # 检查是否为箭头 (-->)
            if c == '-' and self.check('>'):
                self.advance()
                self.add_token(TokenType.ARROW)
            else:
                self.add_token(token_map[c])
            return

        # 比较运算符
        if c == '=':
            self.add_token(TokenType.ASSIGN if not self.check('=') else TokenType.EQ)
            if not self.is_at_end() and self.peek() == '=':
                self.advance()
        elif c == '!':
            self.add_token(TokenType.NOT)
        elif c == '<':
            self.add_token(TokenType.LT if not self.check('=') else TokenType.LE)
            if not self.is_at_end() and self.peek() == '=':
                self.advance()
        elif c == '>':
            self.add_token(TokenType.GT if not self.check('=') else TokenType.GE)
            if not self.is_at_end() and self.peek() == '=':
                self.advance()

        # 逻辑运算符
        elif c == 'a' and self.check_next('n') and self.check_next2('d'):
            self.advance()
            self.advance()
            self.advance()
            self.add_token(TokenType.AND)
        elif c == 'o' and self.check_next('r'):
            self.advance()
            self.advance()
            self.add_token(TokenType.OR)

        # 字符串
        elif c == '"' or c == "'":
            self.string(c)

        # 数字
        elif c.isdigit():
            self.number()

        # 标识符或关键字
        elif c.isalpha() or c == '_':
            self.identifier()

        # 换行
        elif c == '\n':
            self.add_token(TokenType.NEWLINE)
            self.line += 1
            self.column = 1

        # 空格和制表符
        elif c in ' \t\r':
            pass

        # 注释
        elif c == '#':
            if self.check('#'):
                # 多行注释
                self.multi_line_comment()
            else:
                # 单行注释
                self.single_line_comment()

        else:
            raise LexerError(f"Unexpected character: '{c}'", self.line, self.start_column)

    def string(self, quote_char: str):
        """解析字符串字面量"""
        while not self.is_at_end() and self.peek() != quote_char:
            if self.peek() == '\n':
                self.line += 1
                self.column = 0
            self.advance()

        if self.is_at_end():
            raise LexerError("Unterminated string", self.line, self.start_column)

        # closing quote
        self.advance()

        # 去除引号，添加 token
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        """解析数字字面量"""
        while not self.is_at_end() and self.peek().isdigit():
            self.advance()

        # 小数部分
        if not self.is_at_end() and self.peek() == '.' and self.peek_next().isdigit():
            self.advance()  # consume '.'
            while not self.is_at_end() and self.peek().isdigit():
                self.advance()

        value = self.source[self.start:self.current]
        if '.' in value:
            self.add_token(TokenType.NUMBER, float(value))
        else:
            self.add_token(TokenType.NUMBER, int(value))

    def identifier(self):
        """解析标识符或关键字"""
        while not self.is_at_end() and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()

        text = self.source[self.start:self.current]

        # 检查是否为关键字
        token_type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)

        # 布尔值
        if token_type == TokenType.BOOLEAN:
            self.add_token(TokenType.BOOLEAN, text == 'true')
        else:
            self.add_token(token_type)

    def single_line_comment(self):
        """单行注释"""
        while not self.is_at_end() and self.peek() != '\n':
            self.advance()

    def multi_line_comment(self):
        """多行注释"""
        self.advance()  # consume second '#'
        depth = 1
        while not self.is_at_end() and depth > 0:
            if self.peek() == '#' and self.peek_next() == '#':
                self.advance()
                self.advance()
                depth -= 1
            else:
                if self.peek() == '\n':
                    self.line += 1
                    self.column = 0
                self.advance()

    def advance(self) -> str:
        """消费一个字符并返回"""
        c = self.source[self.current]
        self.current += 1
        self.column += 1
        return c

    def peek(self) -> str:
        """查看当前字符但不消费"""
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        """查看下一个字符"""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def check(self, expected: str) -> bool:
        """检查当前字符是否匹配"""
        if self.is_at_end():
            return False
        return self.source[self.current] == expected

    def check_next(self, expected: str) -> bool:
        """检查下一个字符是否匹配"""
        if self.current + 1 >= len(self.source):
            return False
        return self.source[self.current + 1] == expected

    def check_next2(self, expected: str) -> bool:
        """检查再下一个字符是否匹配"""
        if self.current + 2 >= len(self.source):
            return False
        return self.source[self.current + 2] == expected

    def is_at_end(self) -> bool:
        """检查是否到达末尾"""
        return self.current >= len(self.source)

    def add_token(self, token_type: TokenType, value=None):
        """添加 Token"""
        if value is None:
            value = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, value, self.line, self.start_column))


def tokenize(source: str) -> List[Token]:
    """便捷函数：对源代码进行词法分析"""
    lexer = Lexer(source)
    return lexer.tokenize()


if __name__ == "__main__":
    # 测试
    test_code = '''
    skill cleaning_robot {
        fn setup() {
            move.init()
            sense.ultrasonic.init()
        }

        fn loop() {
            if power.battery() < 20 {
                speak("Low battery")
            } else {
                move.forward(0.5)
            }
        }
    }
    '''

    tokens = tokenize(test_code)
    for token in tokens:
        print(token)


"""
RoboSkill DSL Lexer
Converts DSL source code into a token stream
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    # Identifiers and literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    LIST_START = auto()
    LIST_END = auto()
    MAP_START = auto()
    MAP_END = auto()
    MAP_COLON = auto()

    # Keywords
    SKILL = auto()
    FN = auto()
    RETURN = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    WHILE = auto()
    ON = auto()
    IN = auto()
    WITH = auto()
    IMPORT = auto()
    EXPORT = auto()
    PARALLEL = auto()
    AS = auto()
    LET = auto()
    NIL = auto()

    # Action keywords
    MOVE = auto()
    ROTATE = auto()
    GRAB = auto()
    RELEASE = auto()
    SPEAK = auto()
    LIGHT = auto()
    WAIT = auto()
    SLEEP = auto()

    # Perception keywords
    SENSE = auto()
    VISION = auto()
    VOICE = auto()
    AI = auto()
    DETECT = auto()
    RECOGNIZE = auto()
    PLAN = auto()
    PREDICT = auto()
    FOLLOW = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    PERCENT = auto()
    CARET = auto()

    # Comparison operators
    EQ = auto()
    NE = auto()
    LT = auto()
    GT = auto()
    LE = auto()
    GE = auto()

    # Logical operators
    AND = auto()
    OR = auto()
    NOT = auto()

    # Assignment
    ASSIGN = auto()
    ARROW = auto()

    # Separators
    COMMA = auto()
    DOT = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    NEWLINE = auto()
    COLON = auto()
    LBRACKET = auto()
    RBRACKET = auto()

    # Special
    COMMENT = auto()
    EOF = auto()
    ERROR = auto()


@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

    @property
    def lexeme(self):
        """Compatibility property - returns the text representation of the token"""
        return self.value if self.value is not None else ""

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, {self.line}:{self.column})"


class LexerError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at {line}:{column}: {message}")


class Lexer:
    """RoboSkill DSL Lexical Analyzer"""

    KEYWORDS = {
        # Core keywords
        'skill': TokenType.SKILL,
        'fn': TokenType.FN,
        'return': TokenType.RETURN,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'for': TokenType.FOR,
        'while': TokenType.WHILE,
        'on': TokenType.ON,
        'let': TokenType.LET,
        'in': TokenType.IN,
        'with': TokenType.WITH,
        'import': TokenType.IMPORT,
        'export': TokenType.EXPORT,
        'parallel': TokenType.PARALLEL,
        'as': TokenType.AS,
        'true': TokenType.BOOLEAN,
        'false': TokenType.BOOLEAN,
        'nil': TokenType.NIL,

        # Action keywords
        'move': TokenType.MOVE,
        'rotate': TokenType.ROTATE,
        'grab': TokenType.GRAB,
        'release': TokenType.RELEASE,
        'speak': TokenType.SPEAK,
        'light': TokenType.LIGHT,
        'wait': TokenType.WAIT,
        'sleep': TokenType.SLEEP,

        # Perception keywords
        'sense': TokenType.SENSE,
        'vision': TokenType.VISION,
        'voice': TokenType.VOICE,
        'ai': TokenType.AI,
        'detect': TokenType.DETECT,
        'recognize': TokenType.RECOGNIZE,
        'plan': TokenType.PLAN,
        'predict': TokenType.PREDICT,
        'follow': TokenType.FOLLOW,
    }

    def __init__(self, source: str):
        self.source = source
        self.tokens: List[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_column = 1

    def tokenize(self) -> List[Token]:
        """Perform lexical analysis and return the list of tokens"""
        while not self.is_at_end():
            self.start = self.current
            self.start_column = self.column
            self.scan_token()

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def scan_token(self):
        """Scan a single token"""
        c = self.advance()

        # Single-character tokens
        token_map = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.STAR,
            '/': TokenType.SLASH,
            '%': TokenType.PERCENT,
            '^': TokenType.CARET,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LIST_START,
            ']': TokenType.LIST_END,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            ':': TokenType.MAP_COLON,
            '.': TokenType.DOT,
        }

        if c in token_map:
            # Check for arrow (-->)
            if c == '-' and self.check('>'):
                self.advance()
                self.add_token(TokenType.ARROW)
            else:
                self.add_token(token_map[c])
            return

        # Comparison operators
        elif c == '=':
            self.add_token(TokenType.ASSIGN if not self.check('=') else TokenType.EQ)
            if not self.is_at_end() and self.peek() == '=':
                self.advance()
        elif c == '!':
            self.add_token(TokenType.NOT)
        elif c == '<':
            self.add_token(TokenType.LT if not self.check('=') else TokenType.LE)
            if not self.is_at_end() and self.peek() == '=':
                self.advance()
        elif c == '>':
            self.add_token(TokenType.GT if not self.check('=') else TokenType.GE)
            if not self.is_at_end() and self.peek() == '=':
                self.advance()

        # Logical operators
        elif c == 'a' and self.check_next('n') and self.check_next2('d'):
            self.advance()
            self.advance()
            self.advance()
            self.add_token(TokenType.AND)
        elif c == 'o' and self.check_next('r'):
            self.advance()
            self.advance()
            self.add_token(TokenType.OR)

        # Strings
        elif c == '"' or c == "'":
            self.string(c)

        # Numbers
        elif c.isdigit():
            self.number()

        # Identifiers or keywords
        elif c.isalpha() or c == '_':
            self.identifier()

        # Newlines
        elif c == '\n':
            self.add_token(TokenType.NEWLINE)
            self.line += 1
            self.column = 1

        # Whitespace and tabs
        elif c in ' \t\r':
            pass

        # Comments
        elif c == '#':
            if self.check('#'):
                # Multi-line comment
                self.multi_line_comment()
            else:
                # Single-line comment
                self.single_line_comment()

        else:
            raise LexerError(f"Unexpected character: '{c}'", self.line, self.start_column)

    def string(self, quote_char: str):
        """Parse string literal"""
        while not self.is_at_end() and self.peek() != quote_char:
            if self.peek() == '\n':
                self.line += 1
                self.column = 0
            self.advance()

        if self.is_at_end():
            raise LexerError("Unterminated string", self.line, self.start_column)

        # Consume closing quote
        self.advance()

        # Remove quotes and add token
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        """Parse numeric literal"""
        while not self.is_at_end() and self.peek().isdigit():
            self.advance()

        # Decimal part
        if not self.is_at_end() and self.peek() == '.' and self.peek_next().isdigit():
            self.advance()  # Consume '.'
            while not self.is_at_end() and self.peek().isdigit():
                self.advance()

        value = self.source[self.start:self.current]
        if '.' in value:
            self.add_token(TokenType.NUMBER, float(value))
        else:
            self.add_token(TokenType.NUMBER, int(value))

    def identifier(self):
        """Parse identifier or keyword"""
        while not self.is_at_end() and (self.peek().isalnum() or self.peek() == '_'):
            self.advance()

        text = self.source[self.start:self.current]

        # Check if it's a keyword
        token_type = self.KEYWORDS.get(text, TokenType.IDENTIFIER)

        # Boolean values
        if token_type == TokenType.BOOLEAN:
            self.add_token(TokenType.BOOLEAN, text == 'true')
        else:
            self.add_token(token_type)

    def single_line_comment(self):
        """Skip single-line comment"""
        while not self.is_at_end() and self.peek() != '\n':
            self.advance()

    def multi_line_comment(self):
        """Skip multi-line comment"""
        self.advance()  # Consume second '#'
        depth = 1
        while not self.is_at_end() and depth > 0:
            if self.peek() == '#' and self.peek_next() == '#':
                self.advance()
                self.advance()
                depth -= 1
            else:
                if self.peek() == '\n':
                    self.line += 1
                    self.column = 0
                self.advance()

    def advance(self) -> str:
        """Consume and return the current character"""
        c = self.source[self.current]
        self.current += 1
        self.column += 1
        return c

    def peek(self) -> str:
        """Look at current character without consuming"""
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        """Look at next character without consuming"""
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def check(self, expected: str) -> bool:
        """Check if current character matches expected"""
        if self.is_at_end():
            return False
        return self.source[self.current] == expected

    def check_next(self, expected: str) -> bool:
        """Check if next character matches expected"""
        if self.current + 1 >= len(self.source):
            return False
        return self.source[self.current + 1] == expected

    def check_next2(self, expected: str) -> bool:
        """Check if the character after next matches expected"""
        if self.current + 2 >= len(self.source):
            return False
        return self.source[self.current + 2] == expected

    def is_at_end(self) -> bool:
        """Check if we've reached the end of source"""
        return self.current >= len(self.source)

    def add_token(self, token_type: TokenType, value=None):
        """Add a token to the list"""
        if value is None:
            value = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, value, self.line, self.start_column))


def tokenize(source: str) -> List[Token]:
    """Convenience function: perform lexical analysis on source code"""
    lexer = Lexer(source)
    return lexer.tokenize()


if __name__ == "__main__":
    # Test
    test_code = '''
    skill cleaning_robot {
        fn setup() {
            move.init()
            sense.ultrasonic.init()
        }

        fn loop() {
            if power.battery() < 20 {
                speak("Low battery")
            } else {
                move.forward(0.5)
            }
        }
    }
    '''

    tokens = tokenize(test_code)
    for token in tokens:
        print(token)
