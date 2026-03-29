# RoboSkill DSL (RSL)

**面向机器人技能的领域专用语言**

[English](./README.md) | 中文

---

## 概述

RoboSkill DSL 是一款专为机器人技能开发设计的领域专用语言，提供：

- 🚀 **极简语法** - 类似自然语言的声明式语法
- 🤖 **AI 友好** - 语法结构清晰，便于 AI 模型自动生成合法代码
- 🌐 **跨平台** - 支持 Python、C++、ROS 2、Home Assistant 等平台
- 🔧 **模块化** - 支持技能包、函数、事件处理
- 📦 **标准库** - 提供动作、感知、AI 功能的统一接口

---

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/roboteam/roboskill-dsl.git
cd roboskill-dsl

# 安装依赖
pip install -e .
```

### 编写你的第一个技能

创建一个文件 `hello_robot.rsl`:

```rsl
skill hello_robot {
    fn setup() {
        speak("Hello! I'm RoboSkill!")
        light.on("blue")
    }

    fn loop() {
        move.forward(1.0)
        wait(1000)
        rotate.left(90)
        wait(1000)
    }
}
```

### 编译并运行

```bash
# 编译为 Python
python rslc.py hello_robot.rsl -t python -o hello_robot.py
python hello_robot.py

# 或直接解释执行
python rslc.py hello_robot.rsl -I
```

---

## 语言规范

### 基础数据类型

```rsl
# 数值
let speed = 1.5
let angle = 90

# 布尔
let is_active = true
let has_obstacle = false

# 字符串
let name = "Robot-001"
let greeting = "Hello!"

# 列表
let path = [1.0, 2.0, 3.0]
let colors = ["red", "green", "blue"]

# 映射
let point = {x: 1.0, y: 2.0}
let config = {speed: 0.5, color: "blue"}
```

### 动作指令

```rsl
# 移动
move.forward(speed: 1.0)
move.backward(speed: 0.5)
move.stop()

# 旋转
rotate.left(degrees: 90)
rotate.right(degrees: 45)
rotate.to(angle: 180)

# 抓取
grab()
grab.with_force(0.8)
release()

# 语音
speak("Hello, world!")
speak("Warning!", priority: "high")

# 灯光
light.on(color: "red")
light.off()
light.blink(color: "yellow", frequency: 2)
```

### 感知指令

```rsl
# 距离传感器
let distance = sense.ultrasonic()
let dist_left = sense.ultrasonic(direction: "left")

# 触碰
if sense.touch() {
    speak("Touched!")
}

# 电池
let battery = power.battery()
if battery < 20 {
    speak("Low battery!")
}

# 位置
let pos = position.current()
let x = pos.x
```

### AI 功能

```rsl
# 目标检测
let result = ai.detect("person")
if result.found {
    speak("I see a person!")
}

# 手势识别
let gesture = ai.gesture()
if gesture == "wave" {
    speak("Hello!")
}

# 语音识别
let cmd = ai.voice_recognize()
if cmd == "stop" {
    move.stop()
}

# 路径规划
let path = ai.path_plan(start: pos, goal: target, mode: "safe")
for point in path {
    move.to(point.x, point.y)
}
```

### 控制结构

```rsl
# 条件
if battery < 20 {
    go_charge()
} else if battery < 50 {
    speak("Battery medium")
} else {
    speak("Battery good")
}

# for 循环
for i in range(0, 10) {
    move.forward(0.5)
    rotate(36)
}

# while 循环
while sense.ultrasonic() > 0.3 {
    move.forward(0.2)
}

# 事件处理
on button.pressed {
    speak("Button pressed!")
}

on voice.command("stop") {
    move.stop()
}
```

### 函数定义

```rsl
fn calculate_distance(x1, y1, x2, y2) -> number {
    let dx = x2 - x1
    let dy = y2 - y1
    return math.sqrt(dx * dx + dy * dy)
}

fn move_to(x, y) {
    let dist = calculate_distance(pos.x, pos.y, x, y)
    while dist > 0.1 {
        move.forward(dist)
        wait(100)
    }
}
```

---

## 编译目标

### Python

```bash
python rslc.py skill.rsl -t python -o skill.py
```

### C++

```bash
python rslc.py skill.rsl -t cpp -o skill.cpp
# 编译
g++ -std=c++17 -o skill skill.cpp -lrobokit
```

### ROS 2

```bash
python rslc.py skill.rsl -t ros -o skill_node.cpp
# 放入 ROS 包并编译
colcon build && source install/setup.bash
ros2 run my_package skill_node
```

### Home Assistant

```bash
python rslc.py skill.rsl -t home_assistant -o automation.yaml
# 将自动化配置添加到 Home Assistant
```

---

## 示例技能

### 智能清扫机器人

查看完整示例: `examples/cleaning_robot/cleaning_robot.rsl`

```rsl
skill cleaning_robot {
    fn loop() {
        if power.battery() < 20 {
            speak("Low battery")
            return_to_charge()
        }

        let dist = sense.ultrasonic()
        if dist < 0.5 {
            rotate(90)
        } else {
            move.forward(0.5)
        }
    }
}
```

### 手势控制

查看完整示例: `examples/gesture_control/gesture_control.rsl`

```rsl
skill gesture_control {
    fn main_loop() {
        let gesture = ai.gesture()

        if gesture == "wave" {
            speak("Hello!")
            move.forward(0.5)
        }
        else if gesture == "stop" {
            move.stop()
        }
    }
}
```

---

## AI 自动生成提示模板

### 基本动作生成

```
请为机器人生成 RSL 代码，实现以下功能：
[描述机器人的动作需求]

要求：
- 使用 RSL 语法
- 包含 setup() 和 loop() 函数
- 使用动作库和感知库
```

### 完整技能生成

```
请为 [机器人类型] 生成完整的 RSL 技能代码。

功能需求：
1. [功能1描述]
2. [功能2描述]
3. [功能3描述]

约束条件：
- 电量低于 [X]% 时执行 [某动作]
- 检测到 [某物体] 时执行 [某动作]
- 支持语音命令 [列出命令]

请生成包含以下部分的代码：
- 技能元数据
- setup() 初始化函数
- loop() 主循环
- 事件处理器
```

### 示例提示词

```
请为清扫机器人生成 RSL 代码：
1. 自动检测前方障碍物，距离小于0.5米时左转90度
2. 每前进1米播报"清扫中"
3. 电量低于20%时返回充电站（位置0,0）
4. 支持语音命令"停止"和"回家"

请使用以下结构：
- skill cleaning_robot
- setup() 初始化传感器和动作
- loop() 主循环检测和执行
- return_to_charge() 返回充电函数
- 事件处理器处理语音命令
```

---

## 项目结构

```
roboskill-dsl/
├── src/
│   ├── lexer/          # 词法分析器
│   │   └── lexer.py
│   ├── parser/         # 语法分析器
│   │   └── parser.py
│   ├── ast/            # AST 节点定义
│   │   └── nodes.py
│   ├── codegen/        # 代码生成器
│   │   └── generator.py
│   └── adapters/       # 适配器层
│       └── adapters.py
├── stdlib/             # 标准库
│   └── stdlib.py
├── examples/           # 示例程序
│   ├── cleaning_robot/
│   ├── gesture_control/
│   └── patrol_robot/
├── docs/               # 文档
├── tests/              # 测试
├── rslc.py             # 编译器入口
├── SPEC.md             # 语言规范
└── README.md
```

---

## 开发指南

### 添加新的编译目标

1. 在 `src/codegen/generator.py` 中创建新的生成器类
2. 继承 `CodeGenerator` 基类
3. 实现所有 `visit_*` 方法
4. 在 `generate_code()` 函数中注册

```python
class MyTargetGenerator(CodeGenerator):
    def visit_program(self, node: Program):
        # 生成目标代码
        pass

    # ... 实现其他方法
```

### 添加新的适配器

1. 在 `src/adapters/adapters.py` 中创建适配器类
2. 继承 `ActionAdapter`、`SensorAdapter` 或 `AIAdapter`
3. 实现抽象方法
4. 在 `AdapterFactory` 中注册

```python
class MyActionAdapter(ActionAdapter):
    def move_forward(self, speed: float) -> bool:
        # 实现动作
        pass
```

---

## 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_lexer.py
python -m pytest tests/test_parser.py

# 运行示例
python rslc.py examples/cleaning_robot/cleaning_robot.rsl -t python -o /tmp/test.py
python /tmp/test.py
```

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 版本历史

- **v1.0.0** (2024) - 初始版本
  - 支持 Python、C++、ROS 2 编译目标
  - 完整的动作、感知、AI 标准库
  - 解释器和代码生成器
