"""
RoboSkill DSL AST - 抽象语法树节点定义
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class ASTNode(ABC):
    """AST 节点基类"""
    @abstractmethod
    def accept(self, visitor):
        pass


class Expression(ASTNode):
    """表达式基类"""
    pass


class Statement(ASTNode):
    """语句基类"""
    pass


class Program(ASTNode):
    """程序节点"""
    def __init__(self):
        self.skills: List[Skill] = []
        self.functions: List[Function] = []
        self.imports: List[Import] = []

    def accept(self, visitor):
        visitor.visit_program(self)


class Import(ASTNode):
    """导入语句"""
    def __init__(self):
        self.module: str = ""
        self.alias: Optional[str] = None

    def accept(self, visitor):
        pass


class Skill(ASTNode):
    """技能包"""
    def __init__(self):
        self.name: str = ""
        self.version: Optional[str] = None
        self.author: Optional[str] = None
        self.description: Optional[str] = None
        self.statements: List[ASTNode] = []

    def accept(self, visitor):
        visitor.visit_skill(self)


class Function(Statement):
    """函数定义"""
    def __init__(self):
        self.name: str = ""
        self.parameters: List['Parameter'] = []
        self.return_type: Optional[str] = None
        self.body: List[Statement] = []

    def accept(self, visitor):
        visitor.visit_function(self)


class Parameter:
    """函数参数"""
    def __init__(self):
        self.name: str = ""
        self.param_type: Optional[str] = None
        self.default_value: Optional[Expression] = None


class Literal(Expression):
    """字面量"""
    def __init__(self):
        self.value: Any = None
        self.literal_type: str = ""  # "number", "string", "bool"

    def accept(self, visitor):
        visitor.visit_literal(self)


class Identifier(Expression):
    """标识符"""
    def __init__(self):
        self.name: str = ""

    def accept(self, visitor):
        visitor.visit_identifier(self)


class Binary(Expression):
    """二元表达式"""
    def __init__(self):
        self.left: Expression = None
        self.operator: str = ""
        self.right: Expression = None

    def accept(self, visitor):
        visitor.visit_binary(self)


class Unary(Expression):
    """一元表达式"""
    def __init__(self):
        self.operator: str = ""
        self.operand: Expression = None

    def accept(self, visitor):
        visitor.visit_unary(self)


class Call(Expression):
    """函数调用"""
    def __init__(self):
        self.callee: Expression = None
        self.arguments: List[Expression] = []

    def accept(self, visitor):
        visitor.visit_call(self)


class MemberAccess(Expression):
    """成员访问"""
    def __init__(self):
        self.object: Expression = None
        self.property: str = ""

    def accept(self, visitor):
        visitor.visit_member(self)


class IndexAccess(Expression):
    """索引访问"""
    def __init__(self):
        self.object: Expression = None
        self.index: Expression = None

    def accept(self, visitor):
        pass


class ListLiteral(Expression):
    """列表字面量"""
    def __init__(self):
        self.elements: List[Expression] = []

    def accept(self, visitor):
        pass


class MapLiteral(Expression):
    """映射字面量"""
    def __init__(self):
        self.pairs: Dict[str, Expression] = {}

    def accept(self, visitor):
        pass


class Assignment(Statement):
    """赋值语句"""
    def __init__(self):
        self.target: Expression = None
        self.value: Expression = None
        self.is_local: bool = False

    def accept(self, visitor):
        visitor.visit_assignment(self)


class ExpressionStatement(Statement):
    """表达式语句"""
    def __init__(self, expr: Expression = None):
        self.expression: Expression = expr

    def accept(self, visitor):
        visitor.visit_expression_statement(self)


class Return(Statement):
    """返回语句"""
    def __init__(self):
        self.value: Optional[Expression] = None

    def accept(self, visitor):
        visitor.visit_return(self)


class If(Statement):
    """条件语句"""
    def __init__(self):
        self.condition: Expression = None
        self.then_branch: List[Statement] = []
        self.else_branch: List[Statement] = []

    def accept(self, visitor):
        visitor.visit_if(self)


class For(Statement):
    """for 循环"""
    def __init__(self):
        self.variable: str = ""
        self.iterable: Expression = None
        self.body: List[Statement] = []

    def accept(self, visitor):
        visitor.visit_for(self)


class While(Statement):
    """while 循环"""
    def __init__(self):
        self.condition: Expression = None
        self.body: List[Statement] = []

    def accept(self, visitor):
        visitor.visit_while(self)


class EventHandler(Statement):
    """事件处理器"""
    def __init__(self):
        self.event: str = ""
        self.event_params: List[Expression] = []
        self.body: List[Statement] = []

    def accept(self, visitor):
        visitor.visit_event_handler(self)


class Parallel(Statement):
    """并行语句"""
    def __init__(self):
        self.statements: List[Statement] = []

    def accept(self, visitor):
        visitor.visit_parallel(self)