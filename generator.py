"""
RoboSkill DSL Code Generator - 代码生成器
将 AST 转换为目标语言代码
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set
from src.ast.nodes import *


class CodeGenerator(ABC):
    """代码生成器基类"""

    def __init__(self):
        self.indent_level = 0
        self.output = []

    def generate(self, program: Program) -> str:
        """生成目标代码"""
        self.output = []
        program.accept(self)
        return '\n'.join(self.output)

    def indent(self):
        """增加缩进"""
        self.indent_level += 1

    def dedent(self):
        """减少缩进"""
        self.indent_level -= 1

    def write(self, line: str = ""):
        """写入代码行"""
        indent = "    " * self.indent_level
        self.output.append(indent + line)

    def newline(self):
        """写入空行"""
        self.output.append("")

    @abstractmethod
    def visit_program(self, node: Program):
        pass

    @abstractmethod
    def visit_skill(self, node: Skill):
        pass

    @abstractmethod
    def visit_function(self, node: Function):
        pass

    @abstractmethod
    def visit_identifier(self, node: Identifier):
        pass

    @abstractmethod
    def visit_literal(self, node: Literal):
        pass

    @abstractmethod
    def visit_binary(self, node: Binary):
        pass

    @abstractmethod
    def visit_unary(self, node: Unary):
        pass

    @abstractmethod
    def visit_call(self, node: Call):
        pass

    @abstractmethod
    def visit_member(self, node: MemberAccess):
        pass

    @abstractmethod
    def visit_assignment(self, node: Assignment):
        pass

    @abstractmethod
    def visit_return(self, node: Return):
        pass

    @abstractmethod
    def visit_if(self, node: If):
        pass

    @abstractmethod
    def visit_for(self, node: For):
        pass

    @abstractmethod
    def visit_while(self, node: While):
        pass

    @abstractmethod
    def visit_event_handler(self, node: EventHandler):
        pass

    @abstractmethod
    def visit_parallel(self, node: Parallel):
        pass


class PythonGenerator(CodeGenerator):
    """Python 代码生成器"""

    def __init__(self):
        super().__init__()
        self.imports: Set[str] = set()
        self.class_stack: List[str] = []

    def generate(self, program: Program) -> str:
        """生成 Python 代码"""
        self.output = []

        # 添加文件头
        self.output.append("#!/usr/bin/env python3")
        self.output.append("# -*- coding: utf-8 -*-")
        self.output.append('"""')
        self.output.append("RoboSkill DSL - Generated Python Code")
        self.output.append('自动生成，请勿手动编辑')
        self.output.append('"""')
        self.newline()

        # 导入
        self.output.append("import time")
        self.output.append("import math")
        self.output.append("from typing import Any, List, Dict, Optional, Callable")
        self.newline()

        # 导入机器人 SDK
        self.output.append("# RoboSkill Runtime")
        self.output.append("from robokit import Robot, Sensor, AI, Action")
        self.output.append("from robokit.stdlib import *")
        self.newline()

        # 生成程序
        program.accept(self)

        return '\n'.join(self.output)

    def visit_program(self, node: Program):
        """访问程序节点"""
        for skill in node.skills:
            skill.accept(self)

        for func in node.functions:
            func.accept(self)

    def visit_skill(self, node: Skill):
        """访问技能包"""
        self.newline()
        self.write(f"class {self.to_class_name(node.name)}(Robot):")

        # 元数据
        if node.version:
            self.indent()
            self.write(f'"""')
            if node.description:
                self.write(f"{node.description}")
            self.write(f'Version: {node.version}')
            if node.author:
                self.write(f"Author: {node.author}")
            self.write(f'"""')
            self.dedent()

        self.class_stack.append(node.name)

        self.indent()
        self.write("def __init__(self):")
        self.indent()
        self.write("super().__init__()")
        self.write("# 初始化传感器")
        self.write("self.ultrasonic = Sensor('ultrasonic')")
        self.write("self.camera = Sensor('camera')")
        self.write("self.mic = Sensor('microphone')")
        self.write("# 初始化动作")
        self.write("self.motor = Action('motor')")
        self.write("self.gripper = Action('gripper')")
        self.write("self.speaker = Action('speaker')")
        self.dedent()

        # 生成函数和方法
        for stmt in node.statements:
            if isinstance(stmt, Function):
                stmt.accept(self)
            elif isinstance(stmt, EventHandler):
                self.write(f"self.on_{stmt.event} = self._handler_{stmt.event}")
                self.write(f"def _handler_{stmt.event}(self):")
                self.indent()
                for s in stmt.body:
                    s.accept(self)
                self.dedent()
            elif isinstance(stmt, Assignment) and isinstance(stmt.target, Identifier):
                # 元数据属性
                self.write(f"self.{stmt.target.name} = {self.expression_to_string(stmt.value)}")

        self.dedent()
        self.class_stack.pop()

    def visit_function(self, node: Function):
        """访问函数"""
        self.newline()
        params = ', '.join(p.name for p in node.parameters)
        if self.class_stack:
            params = 'self' + (', ' + params if params else '')
        else:
            pass  # 全局函数处理

        self.write(f"def {node.name}({params}):")

        if node.body:
            self.indent()
            for stmt in node.body:
                stmt.accept(self)
            self.dedent()

    def visit_identifier(self, node: Identifier):
        """访问标识符"""
        self.write(node.name)

    def visit_expression_statement(self, node):
        """访问表达式语句"""
        expr_str = self.expression_to_string(node.expression)
        self.write(expr_str)

    def visit_literal(self, node: Literal):
        """访问字面量"""
        if node.literal_type == "string":
            self.write(f'"{node.value}"')
        elif node.literal_type == "bool":
            self.write("True" if node.value else "False")
        else:
            self.write(str(node.value))

    def visit_binary(self, node: Binary):
        """访问二元表达式"""
        left = self.expression_to_string(node.left)
        right = self.expression_to_string(node.right)

        op_map = {
            '+': '+',
            '-': '-',
            '*': '*',
            '/': '/',
            '%': '%',
            '^': '**',
            '==': '==',
            '!=': '!=',
            '<': '<',
            '>': '>',
            '<=': '<=',
            '>=': '>=',
            'and': 'and',
            'or': 'or',
        }
        op = op_map.get(node.operator, node.operator)
        self.write(f"{left} {op} {right}")

    def visit_unary(self, node: Unary):
        """访问一元表达式"""
        operand = self.expression_to_string(node.operand)
        if node.operator == '-':
            self.write(f"-{operand}")
        elif node.operator == 'not':
            self.write(f"not {operand}")
        else:
            self.write(f"{node.operator}{operand}")

    def visit_call(self, node: Call):
        """访问函数调用"""
        callee_str = self.expression_to_string(node.callee)
        args_str = ', '.join(self.expression_to_string(arg) for arg in node.arguments)
        self.write(f"{callee_str}({args_str})")

    def visit_member(self, node: MemberAccess):
        """访问成员访问"""
        obj_str = self.expression_to_string(node.object)
        self.write(f"{obj_str}.{node.property}")

    def visit_assignment(self, node: Assignment):
        """访问赋值语句"""
        target = self.expression_to_string(node.target)
        value = self.expression_to_string(node.value)
        self.write(f"{target} = {value}")

    def visit_return(self, node: Return):
        """访问返回语句"""
        if node.value:
            value = self.expression_to_string(node.value)
            self.write(f"return {value}")
        else:
            self.write("return")

    def visit_if(self, node: If):
        """访问 if 语句"""
        cond = self.expression_to_string(node.condition)
        self.write(f"if {cond}:")
        self.indent()
        for stmt in node.then_branch:
            stmt.accept(self)
        self.dedent()

        if node.else_branch:
            if len(node.else_branch) == 1 and isinstance(node.else_branch[0], If):
                self.write("elif ")
                node.else_branch[0].accept(self)
            else:
                self.write("else:")
                self.indent()
                for stmt in node.else_branch:
                    stmt.accept(stmt)
                self.dedent()

    def visit_for(self, node: For):
        """访问 for 循环"""
        iterable = self.expression_to_string(node.iterable)
        self.write(f"for {node.variable} in {iterable}:")
        self.indent()
        for stmt in node.body:
            stmt.accept(self)
        self.dedent()

    def visit_while(self, node: While):
        """访问 while 循环"""
        cond = self.expression_to_string(node.condition)
        self.write(f"while {cond}:")
        self.indent()
        for stmt in node.body:
            stmt.accept(stmt)
        self.dedent()

    def visit_event_handler(self, node: EventHandler):
        """访问事件处理器"""
        pass  # 在 skill 中处理

    def visit_parallel(self, node: Parallel):
        """访问并行语句"""
        for stmt in node.statements:
            stmt.accept(self)

    def expression_to_string(self, expr) -> str:
        """将表达式转换为字符串"""
        if isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, Literal):
            if expr.literal_type == "string":
                return f'"{expr.value}"'
            elif expr.literal_type == "bool":
                return "True" if expr.value else "False"
            else:
                return str(expr.value)
        elif isinstance(expr, Binary):
            left = self.expression_to_string(expr.left)
            right = self.expression_to_string(expr.right)
            return f"{left} {expr.operator} {right}"
        elif isinstance(expr, Unary):
            operand = self.expression_to_string(expr.operand)
            return f"-{operand}" if expr.operator == '-' else f"not {operand}"
        elif isinstance(expr, Call):
            callee = self.expression_to_string(expr.callee)
            args = ', '.join(self.expression_to_string(a) for a in expr.arguments)
            return f"{callee}({args})"
        elif isinstance(expr, MemberAccess):
            obj = self.expression_to_string(expr.object)
            return f"{obj}.{expr.property}"
        elif isinstance(expr, IndexAccess):
            obj = self.expression_to_string(expr.object)
            idx = self.expression_to_string(expr.index)
            return f"{obj}[{idx}]"
        elif isinstance(expr, ListLiteral):
            elements = ', '.join(self.expression_to_string(e) for e in expr.elements)
            return f"[{elements}]"
        elif isinstance(expr, MapLiteral):
            pairs = ', '.join(f'"{k}": {self.expression_to_string(v)}' for k, v in expr.pairs.items())
            return f"{{{pairs}}}"
        else:
            return str(expr)

    def to_class_name(self, name: str) -> str:
        """将 snake_case 转换为 CamelCase"""
        return ''.join(word.capitalize() for word in name.split('_'))


class CppGenerator(CodeGenerator):
    """C++ 代码生成器"""

    def __init__(self):
        super().__init__()
        self.includes: Set[str] = {"<iostream>", "<vector>", "<string>", "<memory>", "<optional>"}

    def generate(self, program: Program) -> str:
        """生成 C++ 代码"""
        self.output = []

        # 文件头
        self.output.append("// RoboSkill DSL - Generated C++ Code")
        self.output.append("// 自动生成，请勿手动编辑")
        self.newline()

        # 包含头文件
        for inc in sorted(self.includes):
            self.output.append(f"#include {inc}")
        self.newline()

        # Robokit 命名空间
        self.output.append("namespace robokit {")
        self.newline()

        # 生成代码
        program.accept(self)

        self.output.append("} // namespace robokit")
        return '\n'.join(self.output)

    def visit_program(self, node: Program):
        for skill in node.skills:
            skill.accept(self)

    def visit_skill(self, node: Skill):
        """访问技能包"""
        self.write(f"class {self.to_class_name(node.name)} {{")
        self.indent()
        self.write("public:")
        self.indent()

        # 构造函数
        self.write(f"{self.to_class_name(node.name)}() {{")
        self.indent()
        self.write("// 初始化")
        self.dedent()
        self.write("}")
        self.newline()

        # 方法
        for stmt in node.statements:
            if isinstance(stmt, Function):
                self.write(f"void {stmt.name}() {{")
                self.indent()
                for s in stmt.body:
                    self.generate_statement(s)
                self.dedent()
                self.write("}")
                self.newline()

        self.dedent()
        self.dedent()
        self.write("};")
        self.newline()

    def visit_function(self, node: Function):
        pass  # 在 skill 中处理

    def visit_identifier(self, node: Identifier):
        self.write(node.name)

    def visit_literal(self, node: Literal):
        if node.literal_type == "string":
            self.write(f'"{node.value}"')
        elif node.literal_type == "bool":
            self.write("true" if node.value else "false")
        else:
            self.write(str(node.value))

    def visit_binary(self, node: Binary):
        left = self.expression_to_string(node.left)
        right = self.expression_to_string(node.right)
        self.write(f"{left} {node.operator} {right}")

    def visit_unary(self, node: Unary):
        operand = self.expression_to_string(node.operand)
        if node.operator == '-':
            self.write(f"-{operand}")
        elif node.operator == 'not':
            self.write(f"!{operand}")

    def visit_call(self, node: Call):
        callee_str = self.expression_to_string(node.callee)
        args_str = ', '.join(self.expression_to_string(arg) for arg in node.arguments)
        self.write(f"{callee_str}({args_str});")

    def visit_member(self, node: MemberAccess):
        obj_str = self.expression_to_string(node.object)
        self.write(f"{obj_str}.{node.property}")

    def visit_assignment(self, node: Assignment):
        target = self.expression_to_string(node.target)
        value = self.expression_to_string(node.value)
        self.write(f"{target} = {value};")

    def visit_return(self, node: Return):
        if node.value:
            value = self.expression_to_string(node.value)
            self.write(f"return {value};")
        else:
            self.write("return;")

    def visit_if(self, node: If):
        cond = self.expression_to_string(node.condition)
        self.write(f"if ({cond}) {{")
        self.indent()
        for stmt in node.then_branch:
            self.generate_statement(stmt)
        self.dedent()
        self.write("}")

    def visit_for(self, node: For):
        iterable = self.expression_to_string(node.iterable)
        self.write(f"for (auto {node.variable} : {iterable}) {{")
        self.indent()
        for stmt in node.body:
            self.generate_statement(stmt)
        self.dedent()
        self.write("}")

    def visit_while(self, node: While):
        cond = self.expression_to_string(node.condition)
        self.write(f"while ({cond}) {{")
        self.indent()
        for stmt in node.body:
            self.generate_statement(stmt)
        self.dedent()
        self.write("}")

    def visit_event_handler(self, node: EventHandler):
        pass

    def visit_parallel(self, node: Parallel):
        for stmt in node.statements:
            self.generate_statement(stmt)

    def generate_statement(self, stmt):
        """生成语句"""
        if isinstance(stmt, ExpressionStatement):
            expr_str = self.expression_to_string(stmt.expression)
            self.write(f"{expr_str};")
        elif isinstance(stmt, Assignment):
            target = self.expression_to_string(stmt.target)
            value = self.expression_to_string(stmt.value)
            self.write(f"{target} = {value};")
        elif isinstance(stmt, If):
            self.visit_if(stmt)
        elif isinstance(stmt, For):
            self.visit_for(stmt)
        elif isinstance(stmt, While):
            self.visit_while(stmt)
        elif isinstance(stmt, Return):
            self.visit_return(stmt)

    def expression_to_string(self, expr) -> str:
        """将表达式转换为字符串"""
        if isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, Literal):
            if expr.literal_type == "string":
                return f'"{expr.value}"'
            elif expr.literal_type == "bool":
                return "true" if expr.value else "false"
            else:
                return str(expr)
        elif isinstance(expr, Binary):
            left = self.expression_to_string(expr.left)
            right = self.expression_to_string(expr.right)
            return f"({left} {expr.operator} {right})"
        elif isinstance(expr, Unary):
            operand = self.expression_to_string(expr.operand)
            return f"-{operand}" if expr.operator == '-' else f"!{operand}"
        elif isinstance(expr, Call):
            callee = self.expression_to_string(expr.callee)
            args = ', '.join(self.expression_to_string(a) for a in expr.arguments)
            return f"{callee}({args})"
        elif isinstance(expr, MemberAccess):
            obj = self.expression_to_string(expr.object)
            return f"{obj}.{expr.property}"
        elif isinstance(expr, IndexAccess):
            obj = self.expression_to_string(expr.object)
            idx = self.expression_to_string(expr.index)
            return f"{obj}[{idx}]"
        return str(expr)

    def to_class_name(self, name: str) -> str:
        return ''.join(word.capitalize() for word in name.split('_'))


class ROSGenerator(CodeGenerator):
    """ROS 2 代码生成器"""

    def generate(self, program: Program) -> str:
        """生成 ROS 2 代码"""
        self.output = []

        self.output.append("// RoboSkill DSL - Generated ROS 2 Code")
        self.output.append("// 自动生成，请勿手动编辑")
        self.newline()

        self.output.append('#include "rclcpp/rclcpp.hpp"')
        self.output.append('#include "geometry_msgs/msg/twist.hpp"')
        self.output.append('#include "sensor_msgs/msg/laser_scan.hpp"')
        self.newline()

        program.accept(self)
        return '\n'.join(self.output)

    def visit_program(self, node: Program):
        for skill in node.skills:
            skill.accept(self)

    def visit_skill(self, node: Skill):
        """访问技能包 - 生成 ROS 节点"""
        class_name = ''.join(word.capitalize() for word in node.name.split('_'))
        self.write(f"class {class_name}Node : public rclcpp::Node {{")
        self.indent()
        self.write("public:")
        self.indent()
        self.write(f"{class_name}Node() : Node(\"{node.name}\") {{")
        self.indent()
        self.write('RCLCPP_INFO(this->get_logger(), "{} initialized");'.format(node.name))
        self.write("// 初始化发布者和订阅者")
        self.write("cmd_vel_pub_ = this->create_publisher<geometry_msgs::msg::Twist>(\"/cmd_vel\", 10);")
        self.write("laser_sub_ = this->create_subscription<sensor_msgs::msg::LaserScan>(\"/scan\", 10,")
        self.indent()
        self.write(f"[this](const sensor_msgs::msg::LaserScan::SharedPtr msg) {{")
        self.indent()
        self.write("laser_data_ = msg;")
        self.write("on_laser_data(msg);")
        self.dedent()
        self.write("});")
        self.dedent()
        self.write("}")
        self.dedent()

        # 成员变量
        self.newline()
        self.write("private:")
        self.indent()
        self.write("rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_pub_;")
        self.write("rclcpp::Subscription<sensor_msgs::msg::LaserScan>::SharedPtr laser_sub_;")
        self.write("sensor_msgs::msg::LaserScan::SharedPtr laser_data_;")
        self.newline()

        # 辅助方法
        self.write("void move_forward(double speed) {")
        self.indent()
        self.write("auto cmd = geometry_msgs::msg::Twist();")
        self.write("cmd.linear.x = speed;")
        self.write("cmd_vel_pub_->publish(cmd);")
        self.dedent()
        self.write("}")
        self.newline()

        self.write("void rotate(double angle) {")
        self.indent()
        self.write("auto cmd = geometry_msgs::msg::Twist();")
        self.write("cmd.angular.z = angle;")
        self.write("cmd_vel_pub_->publish(cmd);")
        self.dedent()
        self.write("}")
        self.newline()

        self.write("void stop() {")
        self.indent()
        self.write("auto cmd = geometry_msgs::msg::Twist();")
        self.write("cmd_vel_pub_->publish(cmd);")
        self.dedent()
        self.write("}")
        self.newline()

        self.write("void on_laser_data(const sensor_msgs::msg::LaserScan::SharedPtr msg) {")
        self.indent()
        self.write("// 处理激光数据")
        self.dedent()
        self.write("}")
        self.newline()

        self.dedent()
        self.dedent()
        self.write("};")
        self.newline()

        self.write(f"int main(int argc, char **argv) {{")
        self.indent()
        self.write("rclcpp::init(argc, argv);")
        self.write(f"rclcpp::spin(std::make_shared<{class_name}Node>());")
        self.write("rclcpp::shutdown();")
        self.write("return 0;")
        self.dedent()
        self.write("}")

    def visit_function(self, node: Function):
        pass

    def visit_identifier(self, node: Identifier):
        self.write(node.name)

    def visit_literal(self, node: Literal):
        self.write(str(node.value))

    def visit_binary(self, node: Binary):
        left = self.expression_to_string(node.left)
        right = self.expression_to_string(node.right)
        self.write(f"{left} {node.operator} {right}")

    def visit_unary(self, node: Unary):
        self.write(f"{node.operator}{self.expression_to_string(node.operand)}")

    def visit_call(self, node: Call):
        pass

    def visit_member(self, node: MemberAccess):
        pass

    def visit_assignment(self, node: Assignment):
        pass

    def visit_return(self, node: Return):
        pass

    def visit_if(self, node: If):
        pass

    def visit_for(self, node: For):
        pass

    def visit_while(self, node: While):
        pass

    def visit_event_handler(self, node: EventHandler):
        pass

    def visit_parallel(self, node: Parallel):
        pass

    def expression_to_string(self, expr) -> str:
        if isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, Literal):
            return str(expr.value)
        elif isinstance(expr, Binary):
            return f"{self.expression_to_string(expr.left)} {expr.operator} {self.expression_to_string(expr.right)}"
        return ""


class HomeAssistantGenerator(CodeGenerator):
    """Home Assistant 自动化代码生成器"""

    def generate(self, program: Program) -> str:
        """生成 Home Assistant YAML"""
        self.output = []

        self.output.append("# RoboSkill DSL - Generated Home Assistant Automation")
        self.output.append("# 自动生成，请勿手动编辑")
        self.newline()
        self.output.append("automation:")

        for skill in program.skills:
            skill.accept(self)

        return '\n'.join(self.output)

    def visit_program(self, node: Program):
        pass

    def visit_skill(self, node: Skill):
        """访问技能包"""
        for stmt in node.statements:
            if isinstance(stmt, EventHandler):
                self.write(f"  - alias: {stmt.event}_handler")
                self.indent()
                self.write("trigger:")
                self.indent()
                self.write(f"  - platform: event")
                self.write(f"    event_type: {stmt.event}")
                self.dedent()
                self.write("action:")
                self.indent()
                for s in stmt.body:
                    self.generate_action(s)
                self.dedent()
                self.dedent()
                self.newline()

    def generate_action(self, stmt):
        """生成 Home Assistant action"""
        if isinstance(stmt, ExpressionStatement):
            expr = stmt.expression
            if isinstance(expr, Call):
                callee = self.expression_to_string(expr.callee)
                if callee == "speak":
                    if expr.arguments:
                        msg = self.expression_to_string(expr.arguments[0])
                        self.write(f"  - service: tts.google_say")
                        self.indent()
                        self.write(f"    data:")
                        self.indent()
                        self.write(f"      message: {msg}")
                        self.dedent()
                        self.dedent()

    def visit_function(self, node: Function):
        pass

    def visit_identifier(self, node: Identifier):
        self.write(node.name)

    def visit_literal(self, node: Literal):
        self.write(str(node.value))

    def visit_binary(self, node: Binary):
        left = self.expression_to_string(node.left)
        right = self.expression_to_string(node.right)
        self.write(f"{left} {node.operator} {right}")

    def visit_unary(self, node: Unary):
        self.write(f"{node.operator}{self.expression_to_string(node.operand)}")

    def visit_call(self, node: Call):
        callee_str = self.expression_to_string(node.callee)
        args_str = ', '.join(self.expression_to_string(arg) for arg in node.arguments)
        self.write(f"{callee_str}({args_str})")

    def visit_member(self, node: MemberAccess):
        obj_str = self.expression_to_string(node.object)
        self.write(f"{obj_str}.{node.property}")

    def visit_assignment(self, node: Assignment):
        pass

    def visit_return(self, node: Return):
        pass

    def visit_if(self, node: If):
        pass

    def visit_for(self, node: For):
        pass

    def visit_while(self, node: While):
        pass

    def visit_event_handler(self, node: EventHandler):
        pass

    def visit_parallel(self, node: Parallel):
        pass

    def expression_to_string(self, expr) -> str:
        if isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, Literal):
            if expr.literal_type == "string":
                return f'"{expr.value}"'
            return str(expr.value)
        elif isinstance(expr, Binary):
            return f"{self.expression_to_string(expr.left)} {expr.operator} {self.expression_to_string(expr.right)}"
        elif isinstance(expr, Call):
            callee = self.expression_to_string(expr.callee)
            args = ', '.join(self.expression_to_string(a) for a in expr.arguments)
            return f"{callee}({args})"
        elif isinstance(expr, MemberAccess):
            return f"{self.expression_to_string(expr.object)}.{expr.property}"
        return ""


def generate_code(program: Program, target: str = "python") -> str:
    """生成目标代码的便捷函数"""
    generators = {
        "python": PythonGenerator,
        "cpp": CppGenerator,
        "ros": ROSGenerator,
        "home_assistant": HomeAssistantGenerator,
    }

    generator_class = generators.get(target, PythonGenerator)
    generator = generator_class()
    return generator.generate(program)
