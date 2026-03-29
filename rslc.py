#!/usr/bin/env python3
"""
RoboSkill DSL Compiler - RSL 编译器
===================================

用法:
    python rslc.py <input.rsl> [options]

选项:
    -o, --output <file>     输出文件路径
    -t, --target <platform> 目标平台 (python, cpp, ros, home_assistant)
    -I, --interpret         直接解释执行
    -v, --verbose           详细输出
    --ast                   输出 AST（调试用）

示例:
    python rslc.py cleaning_robot.rsl -t python -o output.py
    python rslc.py skill.rsl -I  # 直接运行
    python rslc.py skill.rsl -t cpp -o skill.cpp
"""

import sys
import argparse
import os
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.lexer.lexer import tokenize, LexerError
from src.parser.parser import parse, ParseError
from src.codegen.generator import generate_code, PythonGenerator, CppGenerator, ROSGenerator, HomeAssistantGenerator
from src.interpreter import interpret, InterpreterError


class Colors:
    """终端颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_error(msg: str):
    print(f"{Colors.RED}Error: {msg}{Colors.RESET}", file=sys.stderr)


def print_success(msg: str):
    print(f"{Colors.GREEN}Success: {msg}{Colors.RESET}")


def print_info(msg: str):
    print(f"{Colors.BLUE}Info: {msg}{Colors.RESET}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}Warning: {msg}{Colors.RESET}")


def compile_file(input_file: str, target: str, output_file: str = None, verbose: bool = False):
    """编译 RSL 文件"""
    try:
        # 读取源文件
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()

        if verbose:
            print_info(f"Reading file: {input_file}")
            print_info(f"Target platform: {target}")

        # 词法分析
        if verbose:
            print_info("Lexing...")
        tokens = tokenize(source)

        if verbose:
            print_success(f"Lexed {len(tokens)} tokens")

        # 语法分析
        if verbose:
            print_info("Parsing...")
        program = parse(source)

        if verbose:
            print_success(f"Parsed {len(program.skills)} skill(s), {len(program.functions)} function(s)")

        # 代码生成
        if verbose:
            print_info(f"Generating {target} code...")

        code = generate_code(program, target)

        if verbose:
            print_success(f"Generated {len(code)} characters")

        # 输出
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(code)
            print_success(f"Output written to: {output_file}")
        else:
            print(code)

        return True

    except LexerError as e:
        print_error(f"Lexer error: {e}")
        return False
    except ParseError as e:
        print_error(f"Parse error: {e}")
        return False
    except Exception as e:
        print_error(f"Compilation failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def interpret_file(input_file: str, platform: str = "python", verbose: bool = False):
    """解释执行 RSL 文件"""
    try:
        # 读取源文件
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()

        if verbose:
            print_info(f"Reading file: {input_file}")
            print_info("Starting interpreter...")

        # 解释执行
        interpreter = interpret(source, platform)

        if verbose:
            print_success("Execution completed")

        return True

    except LexerError as e:
        print_error(f"Lexer error: {e}")
        return False
    except ParseError as e:
        print_error(f"Parse error: {e}")
        return False
    except InterpreterError as e:
        print_error(f"Runtime error: {e}")
        return False
    except KeyboardInterrupt:
        print_info("Interrupted by user")
        return False
    except Exception as e:
        print_error(f"Execution failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def show_ast(input_file: str):
    """显示 AST"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()

        program = parse(source)

        print("=" * 60)
        print("Abstract Syntax Tree")
        print("=" * 60)

        for skill in program.skills:
            print(f"\nSkill: {skill.name}")
            print("-" * 40)
            for stmt in skill.statements:
                print(f"  {type(stmt).__name__}")

        print("\n" + "=" * 60)

    except Exception as e:
        print_error(f"Failed to show AST: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='RoboSkill DSL Compiler',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('input', nargs='?', help='Input RSL file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-t', '--target', choices=['python', 'cpp', 'ros', 'home_assistant'],
                        default='python', help='Target platform (default: python)')
    parser.add_argument('-I', '--interpret', action='store_true',
                        help='Interpret and execute directly')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    parser.add_argument('--ast', action='store_true',
                        help='Show AST and exit')
    parser.add_argument('--platform', choices=['python', 'ros'],
                        default='python', help='Runtime platform for interpretation')

    args = parser.parse_args()

    # 检查输入文件
    if not args.input:
        parser.print_help()
        print("\n" + "=" * 60)
        print("RoboSkill DSL Compiler v1.0.0")
        print("=" * 60)
        print("\nQuick Examples:")
        print("  python rslc.py skill.rsl -t python -o output.py")
        print("  python rslc.py skill.rsl -I")
        print("  python rslc.py skill.rsl -t cpp -o skill.cpp")
        return 1

    if not os.path.exists(args.input):
        print_error(f"Input file not found: {args.input}")
        return 1

    # 确定输出文件名
    output_file = args.output
    if not output_file:
        if args.target == 'python':
            output_file = args.input.replace('.rsl', '.py')
        elif args.target == 'cpp':
            output_file = args.input.replace('.rsl', '.cpp')
        elif args.target == 'ros':
            output_file = args.input.replace('.rsl', '_node.cpp')
        elif args.target == 'home_assistant':
            output_file = args.input.replace('.rsl', '.yaml')

    # 显示 AST
    if args.ast:
        show_ast(args.input)
        return 0

    # 解释执行
    if args.interpret:
        return 0 if interpret_file(args.input, args.platform, args.verbose) else 1

    # 编译
    return 0 if compile_file(args.input, args.target, output_file, args.verbose) else 1


if __name__ == "__main__":
    sys.exit(main())
