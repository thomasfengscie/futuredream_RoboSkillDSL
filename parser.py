"""
RoboSkill DSL Parser - 语法分析器
将 Token 流转换为 AST
"""

from typing import List, Optional, Dict
from src.lexer.lexer import Lexer, Token, TokenType
from src.ast.nodes import *


class ParseError(Exception):
    def __init__(self, message, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"Parse error at {token.line}:{token.column}: {message}")


class Parser:
    """RoboSkill DSL 语法分析器"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors: List[ParseError] = []

    def skip_newlines(self):
        """跳过换行符"""
        while self.match(TokenType.NEWLINE):
            pass

    def parse(self) -> Program:
        """解析整个程序"""
        program = Program()
        self.skip_newlines()

        while not self.is_at_end():
            try:
                if self.match(TokenType.IMPORT):
                    program.imports.append(self.parse_import())
                elif self.check(TokenType.SKILL):
                    program.skills.append(self.parse_skill())
                elif self.check(TokenType.FN):
                    program.functions.append(self.parse_function())
                elif self.check(TokenType.EXPORT):
                    self.advance()  # consume 'export'
                    # export 应用于后续声明
                else:
                    # 跳过无法识别的语句
                    self.advance()
                self.skip_newlines()
            except ParseError as e:
                self.errors.append(e)
                self.synchronize()

        return program

    # ==================== 辅助方法 ====================

    def is_at_end(self) -> bool:
        """检查是否到达末尾"""
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        """查看当前 token"""
        return self.tokens[self.current]

    def previous(self) -> Token:
        """返回上一个 token"""
        return self.tokens[self.current - 1]

    def check(self, token_type: TokenType) -> bool:
        """检查当前 token 是否为指定类型"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def check_next(self, token_type: TokenType) -> bool:
        """检查下一个 token 是否为指定类型"""
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type == token_type

    def advance(self) -> Token:
        """消费当前 token 并返回"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *types: TokenType) -> bool:
        """检查当前 token 是否匹配给定类型"""
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, token_type: TokenType, message: str) -> Token:
        """消费指定类型的 token"""
        if self.check(token_type):
            return self.advance()
        raise ParseError(message, self.peek())

    # ==================== 导入导出 ====================

    def parse_import(self) -> Import:
        """解析 import 语句"""
        module = self.consume(TokenType.IDENTIFIER, "Expected module name")

        import_node = Import()
        import_node.module = module.lexeme

        if self.match(TokenType.AS):
            alias = self.consume(TokenType.IDENTIFIER, "Expected alias")
            import_node.alias = alias.lexeme

        self.consume(TokenType.SEMICOLON, "Expected ';' after import")
        return import_node

    # ==================== 技能包 ====================

    def parse_skill(self) -> Skill:
        """解析 skill 定义"""
        self.consume(TokenType.SKILL, "Expected 'skill'")

        name = self.consume(TokenType.IDENTIFIER, "Expected skill name")
        self.consume(TokenType.LBRACE, "Expected '{' after skill name")

        skill = Skill()
        skill.name = name.lexeme

        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            self.parse_skill_member(skill)

        self.consume(TokenType.RBRACE, "Expected '}' after skill body")
        return skill

    def parse_skill_member(self, skill: Skill):
        """解析技能包成员"""
        self.skip_newlines()
        if self.check(TokenType.IDENTIFIER):
            # 可能是元数据赋值
            name = self.peek()
            if self.check_next(TokenType.ASSIGN):
                self.advance()  # consume IDENTIFIER
                self.advance()  # consume ASSIGN
                value = self.expression()
                self.consume(TokenType.SEMICOLON, "Expected ';' after assignment")

                if name.lexeme == 'version':
                    skill.version = value.value if isinstance(value, Literal) else None
                elif name.lexeme == 'author':
                    skill.author = value.value if isinstance(value, Literal) else None
                elif name.lexeme == 'description':
                    skill.description = value.value if isinstance(value, Literal) else None
            else:
                # 作为语句处理
                stmt = self.parse_statement()
                skill.statements.append(stmt)
        elif self.check(TokenType.FN):
            self.advance()  # consume FN
            func = self.parse_function()
            skill.statements.append(func)
        elif self.check(TokenType.ON):
            self.advance()  # consume ON
            handler = self.parse_event_handler()
            skill.statements.append(handler)
        else:
            stmt = self.parse_statement()
            skill.statements.append(stmt)

    # ==================== 函数 ====================

    def parse_function(self) -> Function:
        """解析函数定义"""
        # Note: FN token was consumed by parse_skill_member
        name = self.consume(TokenType.IDENTIFIER, "Expected function name")
        self.consume(TokenType.LPAREN, "Expected '(' after function name")

        func = Function()
        func.name = name.lexeme

        # 参数列表
        if not self.check(TokenType.RPAREN):
            while True:
                param = self.parse_parameter()
                func.parameters.append(param)
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RPAREN, "Expected ')' after parameters")

        # 返回类型
        if self.match(TokenType.ARROW):
            return_type = self.consume(TokenType.IDENTIFIER, "Expected return type")
            func.return_type = return_type.lexeme

        # 函数体
        self.consume(TokenType.LBRACE, "Expected '{' before function body")
        func.body = self.parse_block()

        return func

    def parse_parameter(self) -> Parameter:
        """解析函数参数"""
        name = self.consume(TokenType.IDENTIFIER, "Expected parameter name")

        param = Parameter()
        param.name = name.lexeme

        # 类型注解
        if self.match(TokenType.COLON):
            param_type = self.consume(TokenType.IDENTIFIER, "Expected type name")
            param.param_type = param_type.lexeme

        # 默认值
        if self.match(TokenType.ASSIGN):
            param.default_value = self.expression()

        return param

    # ==================== 语句 ====================

    def parse_statement(self) -> Statement:
        """解析语句"""
        if self.match(TokenType.RETURN):
            return self.parse_return()
        if self.match(TokenType.IF):
            return self.parse_if()
        if self.match(TokenType.FOR):
            return self.parse_for()
        if self.match(TokenType.WHILE):
            return self.parse_while()
        if self.match(TokenType.PARALLEL):
            return self.parse_parallel()
        if self.match(TokenType.LET) or self.match(TokenType.IDENTIFIER):
            # 可能是 let 语句或赋值
            if self.previous().type == TokenType.LET:
                return self.parse_variable_declaration()
            else:
                # 回退一个 token，当作赋值处理
                self.current -= 1
                return self.parse_assignment_or_expression()
        if self.match(TokenType.LBRACE):
            # 代码块
            stmts = self.parse_block()
            # 返回第一个语句或块语句
            if len(stmts) == 1:
                return stmts[0]
            else:
                block = Parallel()
                block.statements = stmts
                return block

        return self.parse_expression_statement()

    def parse_return(self) -> Return:
        """解析 return 语句"""
        ret = Return()
        if not self.check(TokenType.SEMICOLON) and not self.check(TokenType.RBRACE):
            ret.value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after return")
        return ret

    def parse_if(self) -> If:
        """解析 if 语句"""
        if_stmt = If()
        if_stmt.condition = self.expression()
        self.consume(TokenType.LBRACE, "Expected '{' after if condition")

        if_stmt.then_branch = self.parse_block()

        if self.match(TokenType.ELSE):
            if self.check(TokenType.IF):
                self.advance()
                if_stmt.else_branch = [self.parse_if()]
            else:
                self.consume(TokenType.LBRACE, "Expected '{' after else")
                if_stmt.else_branch = self.parse_block()

        return if_stmt

    def parse_for(self) -> For:
        """解析 for 循环"""
        for_stmt = For()

        # 变量名
        var = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        for_stmt.variable = var.lexeme

        self.consume(TokenType.IN, "Expected 'in' after variable")
        for_stmt.iterable = self.expression()

        self.consume(TokenType.LBRACE, "Expected '{' after for")
        for_stmt.body = self.parse_block()

        return for_stmt

    def parse_while(self) -> While:
        """解析 while 循环"""
        while_stmt = While()
        while_stmt.condition = self.expression()
        self.consume(TokenType.LBRACE, "Expected '{' after while condition")
        while_stmt.body = self.parse_block()
        return while_stmt

    def parse_parallel(self) -> Parallel:
        """解析 parallel 语句"""
        self.consume(TokenType.LBRACE, "Expected '{' after parallel")
        parallel = Parallel()
        parallel.statements = self.parse_block()
        return parallel

    def parse_event_handler(self) -> EventHandler:
        """解析事件处理器"""
        handler = EventHandler()

        # 事件名称
        event = self.consume(TokenType.IDENTIFIER, "Expected event name")
        handler.event = event.lexeme

        # 事件参数
        if self.match(TokenType.LPAREN):
            if not self.check(TokenType.RPAREN):
                while True:
                    arg = self.expression()
                    handler.event_params.append(arg)
                    if not self.match(TokenType.COMMA):
                        break
            self.consume(TokenType.RPAREN, "Expected ')' after event params")

        self.consume(TokenType.LBRACE, "Expected '{' after event name")
        handler.body = self.parse_block()

        return handler

    def parse_variable_declaration(self) -> Assignment:
        """解析变量声明 let x = value"""
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name")

        assign = Assignment()
        assign.is_local = True

        ident = Identifier()
        ident.name = name.lexeme
        assign.target = ident

        if self.match(TokenType.ASSIGN):
            assign.value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ';' after variable declaration")
        return assign

    def parse_assignment_or_expression(self) -> Statement:
        """解析赋值或表达式"""
        expr = self.expression()

        if self.match(TokenType.ASSIGN):
            value = self.expression()
            self.consume(TokenType.SEMICOLON, "Expected ';' after assignment")

            assign = Assignment()
            if isinstance(expr, Identifier):
                assign.target = expr
            elif isinstance(expr, MemberAccess):
                ident = Identifier()
                ident.name = expr.object.name + "." + expr.property
                assign.target = ident
            else:
                assign.target = expr
            assign.value = value
            return assign

        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExpressionStatement(expr)

    def parse_expression_statement(self) -> ExpressionStatement:
        """解析表达式语句"""
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expected ';' after expression")
        return ExpressionStatement(expr)

    def parse_block(self) -> List[Statement]:
        """解析代码块"""
        self.skip_newlines()
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            stmt = self.parse_statement()
            statements.append(stmt)
            self.skip_newlines()
        self.consume(TokenType.RBRACE, "Expected '}' after block")
        return statements

    # ==================== 表达式 ====================

    def expression(self) -> Expression:
        """解析表达式"""
        return self.parse_or()

    def parse_or(self) -> Expression:
        """解析 or 表达式"""
        expr = self.parse_and()

        while self.match(TokenType.OR):
            binary = Binary()
            binary.left = expr
            binary.operator = "or"
            binary.right = self.parse_and()
            expr = binary

        return expr

    def parse_and(self) -> Expression:
        """解析 and 表达式"""
        expr = self.parse_equality()

        while self.match(TokenType.AND):
            binary = Binary()
            binary.left = expr
            binary.operator = "and"
            binary.right = self.parse_equality()
            expr = binary

        return expr

    def parse_equality(self) -> Expression:
        """解析相等性比较"""
        expr = self.parse_comparison()

        while self.match(TokenType.EQ, TokenType.NE):
            binary = Binary()
            binary.left = expr
            binary.operator = self.previous().lexeme
            binary.right = self.parse_comparison()
            expr = binary

        return expr

    def parse_comparison(self) -> Expression:
        """解析比较运算"""
        expr = self.parse_term()

        while self.match(TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            binary = Binary()
            binary.left = expr
            binary.operator = self.previous().lexeme
            binary.right = self.parse_term()
            expr = binary

        return expr

    def parse_term(self) -> Expression:
        """解析加减运算"""
        expr = self.parse_factor()

        while self.match(TokenType.PLUS, TokenType.MINUS):
            binary = Binary()
            binary.left = expr
            binary.operator = self.previous().lexeme
            binary.right = self.parse_factor()
            expr = binary

        return expr

    def parse_factor(self) -> Expression:
        """解析乘除模运算"""
        expr = self.parse_unary()

        while self.match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            binary = Binary()
            binary.left = expr
            binary.operator = self.previous().lexeme
            binary.right = self.parse_unary()
            expr = binary

        return expr

    def parse_unary(self) -> Expression:
        """解析一元运算"""
        if self.match(TokenType.MINUS):
            unary = Unary()
            unary.operator = "-"
            unary.operand = self.parse_unary()
            return unary

        if self.match(TokenType.NOT):
            unary = Unary()
            unary.operator = "not"
            unary.operand = self.parse_unary()
            return unary

        return self.parse_power()

    def parse_power(self) -> Expression:
        """解析幂运算"""
        expr = self.parse_call()

        if self.match(TokenType.CARET):
            binary = Binary()
            binary.left = expr
            binary.operator = "^"
            binary.right = self.parse_unary()
            return binary

        return expr

    def parse_call(self) -> Expression:
        """解析函数调用"""
        expr = self.parse_primary()

        while True:
            if self.match(TokenType.LPAREN):
                expr = self.finish_call(expr)
            elif self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expected property name")
                member = MemberAccess()
                member.object = expr
                member.property = name.lexeme
                expr = member
            elif self.match(TokenType.LBRACKET):
                index = self.expression()
                self.consume(TokenType.RBRACKET, "Expected ']' after index")
                idx = IndexAccess()
                idx.object = expr
                idx.index = index
                expr = idx
            else:
                break

        return expr

    def finish_call(self, callee: Expression) -> Call:
        """完成函数调用"""
        call = Call()
        call.callee = callee
        call.arguments = []

        if not self.check(TokenType.RPAREN):
            while True:
                call.arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RPAREN, "Expected ')' after arguments")
        return call

    def parse_primary(self) -> Expression:
        """解析基本表达式"""
        # 布尔字面量
        if self.match(TokenType.BOOLEAN):
            literal = Literal()
            literal.value = self.previous().value
            literal.literal_type = "bool"
            return literal

        # 数字字面量
        if self.match(TokenType.NUMBER):
            literal = Literal()
            literal.value = self.previous().value
            literal.literal_type = "number"
            return literal

        # 字符串字面量
        if self.match(TokenType.STRING):
            literal = Literal()
            literal.value = self.previous().value
            literal.literal_type = "string"
            return literal

        # 列表字面量
        if self.match(TokenType.LIST_START):
            return self.parse_list_literal()

        # 映射字面量
        if self.match(TokenType.LBRACE):
            return self.parse_map_literal()

        # 标识符
        if self.match(TokenType.IDENTIFIER):
            ident = Identifier()
            ident.name = self.previous().lexeme
            return ident

        # 括号表达式
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        # 特殊关键字作为标识符
        if self.match(TokenType.MOVE, TokenType.ROTATE, TokenType.GRAB, TokenType.RELEASE,
                      TokenType.SPEAK, TokenType.LIGHT, TokenType.SENSE, TokenType.VISION,
                      TokenType.VOICE, TokenType.AI, TokenType.DETECT, TokenType.RECOGNIZE,
                      TokenType.PLAN, TokenType.PREDICT, TokenType.FOLLOW):
            ident = Identifier()
            ident.name = self.previous().lexeme
            return ident

        raise ParseError("Expected expression", self.peek())

    def parse_list_literal(self) -> ListLiteral:
        """解析列表字面量"""
        lst = ListLiteral()

        if not self.check(TokenType.LIST_END):
            while True:
                lst.elements.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.LIST_END, "Expected ']' after list elements")
        return lst

    def parse_map_literal(self) -> MapLiteral:
        """解析映射字面量"""
        m = MapLiteral()

        if not self.check(TokenType.RBRACE):
            while True:
                key = self.consume(TokenType.IDENTIFIER, "Expected key")
                self.consume(TokenType.COLON, "Expected ':' after key")
                value = self.expression()
                m.pairs[key.lexeme] = value
                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RBRACE, "Expected '}' after map literal")
        return m

    # ==================== 辅助方法 ====================

    def match(self, *types: TokenType) -> bool:
        """检查当前 token 是否匹配给定类型"""
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def check(self, token_type: TokenType) -> bool:
        """检查当前 token 是否为指定类型"""
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self) -> Token:
        """消费当前 token 并返回"""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        """检查是否到达末尾"""
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        """查看当前 token"""
        return self.tokens[self.current]

    def previous(self) -> Token:
        """返回上一个 token"""
        return self.tokens[self.current - 1]

    def consume(self, token_type: TokenType, message: str) -> Token:
        """消费指定类型的 token"""
        if self.check(token_type):
            return self.advance()
        raise ParseError(message, self.peek())

    def synchronize(self):
        """同步到下一个语句边界"""
        self.advance()

        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return

            if self.check(TokenType.SKILL) or self.check(TokenType.FN) or \
               self.check(TokenType.IF) or self.check(TokenType.FOR) or \
               self.check(TokenType.WHILE) or self.check(TokenType.RETURN):
                return

            self.advance()


def parse(source: str) -> Program:
    """便捷函数：解析源代码"""
    from src.lexer.lexer import tokenize
    tokens = tokenize(source)
    parser = Parser(tokens)
    return parser.parse()


if __name__ == "__main__":
    # 测试
    test_code = '''
    skill cleaning_robot {
        version = "1.0.0"

        fn setup() {
            move.init()
        }

        fn loop() {
            let battery = power.battery()
            if battery < 20 {
                speak("Low battery")
            } else {
                move.forward(0.5)
            }
        }
    }
    '''

    program = parse(test_code)
    print("Program parsed successfully!")
    print(f"Skills: {[s.name for s in program.skills]}")
    for skill in program.skills:
        for stmt in skill.statements:
            print(f"  - {type(stmt).__name__}")
