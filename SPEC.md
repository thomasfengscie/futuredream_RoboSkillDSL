# RoboSkill DSL (RSL) 语言规范 v1.0(enlish version in the back)

## 1. 语言概述

RoboSkill DSL (RSL) 是一款专为机器人技能开发设计的领域专用语言，旨在提供简洁、可读性强的语法，使开发者（包括 AI）能够快速编写跨平台的机器人控制程序。

### 1.1 设计目标

- **极简语法**：类似自然语言的声明式语法，减少 boilerplate
- **AI 友好**：语法结构清晰，便于 AI 模型自动生成合法代码
- **硬件无关**：通过适配器层支持多种机器人 SDK
- **模块化**：支持技能包、函数、事件处理
- **可编译**：可转换为 Python、C++、ROS 2、Home Assistant 等目标平台

### 1.2 核心特性

```
✓ 基础数据类型：number, bool, string, list, sensor_data, ai_result
✓ 动作指令：move, rotate, grab, release, speak, light
✓ 控制结构：if/else, for, while, on_event, parallel
✓ AI 接口：vision.detect, voice.recognize, path.plan, predict
✓ 模块化：skill 包、函数定义、事件监听
✓ 硬件抽象：统一的适配器层
```

---

## 2. 词法规范

### 2.1 关键字

```
skill, fn, return, if, else, for, while, on, in, with
true, false, nil
move, rotate, grab, release, speak, light, wait, sleep
sense, detect, recognize, plan, predict, follow
module, import, export, async, await
parallel, when, always, never
```

### 2.2 标识符

- 字母、数字、下划线组成
- 不能以数字开头
- 区分大小写
- 推荐命名风格：`snake_case`（小写下划线）

### 2.3 基础字面量

```rsl
# 数值
42
3.14
-273.15

# 布尔
true
false

# 字符串
"Hello, Robot!"
'Single quotes also work'

# 列表
[1, 2, 3]
["apple", "banana"]

# 传感器数据
{type: "distance", value: 1.5, unit: "m"}
{type: "camera", objects: ["person", "cup"]}
```

### 2.4 注释

```rsl
# 单行注释

##
  多行注释
  可以跨越多行
##
```

---

## 3. 数据类型

### 3.1 内置类型

| 类型 | 描述 | 示例 |
|------|------|------|
| `number` | 整数或浮点数 | `42`, `3.14` |
| `bool` | 布尔值 | `true`, `false` |
| `string` | 字符串 | `"text"` |
| `list` | 列表/数组 | `[1, 2, 3]` |
| `map` | 键值对 | `{key: value}` |
| `sensor_data` | 传感器数据结构 | `{type, value, timestamp}` |
| `ai_result` | AI 处理结果 | `{type, data, confidence}` |

### 3.2 类型系统

```rsl
# 显式类型声明（可选）
let speed: number = 1.5
let name: string = "Robot-001"

# 类型推断
let speed = 1.5        # 自动推断为 number
let is_active = true  # 自动推断为 bool

# 传感器数据
let distance = sense.ultrasonic()    # 返回 sensor_data
let objects = vision.detect("person") # 返回 ai_result
```

---

## 4. 语法结构

### 4.1 技能包定义 (Skill Package)

```rsl
skill cleaning_robot {
  # 技能元数据
  version = "1.0.0"
  author = "RoboTeam"
  description = "智能清扫机器人"

  # 技能初始化
  fn setup() {
    move.init()
    sense.ultrasonic.init()
    vision.init()
  }

  # 主循环
  fn loop() {
    let obstacle = sense.ultrasonic() < 0.5
    if obstacle {
      rotate(90)
    } else {
      move.forward(0.5)
    }
  }
}
```

### 4.2 函数定义

```rsl
fn calculate_distance(x1, y1, x2, y2) -> number {
  let dx = x2 - x1
  let dy = y2 - y1
  return math.sqrt(dx * dx + dy * dy)
}

fn move_to_target(target_x, target_y) {
  let distance = calculate_distance(pos.x, pos.y, target_x, target_y)
  while distance > 0.1 {
    move.forward(distance)
    wait(100)
  }
}
```

### 4.3 动作指令

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
release()
grab.with_force(0.8)

# 灯光
light.on(color: "red")
light.off()
light.blink(frequency: 2)

# 语音
speak("Hello, I am a robot!")
speak("Warning: Obstacle detected", priority: "high")
```

### 4.4 感知指令

```rsl
# 距离传感器
let dist = sense.ultrasonic()
let dist_front = sense.ultrasonic(direction: "front")
let dist_all = sense.ultrasonic(all: true)

# 摄像头
let objects = vision.detect("person")
let objects_all = vision.detect()
let gesture = vision.gesture()

# 麦克风
let audio = voice.listen()
let command = voice.recognize()

# 电池
let battery = power.battery()
let is_low = battery < 20

# 位置
let pos = position.current()
let pos_x = position.x()
```

### 4.5 AI 接口

```rsl
# 目标检测
let result = ai.detect("person", confidence: 0.8)
if result.found {
  let obj = result.objects[0]
  speak("I see a " + obj.label)
}

# 手势识别
let gesture = ai.gesture()
if gesture == "wave" {
  speak("Hello!")
}

# 路径规划
let path = ai.path_plan(start: pos, goal: target, mode: "fast")
for point in path {
  move.to(point)
}

# 人物跟随
ai.follow(target: "person", distance: 2.0)

# 语音识别
let cmd = ai.voice_recognize()
if cmd == "come here" {
  move.forward(1.0)
}
```

### 4.6 控制结构

#### 条件语句
```rsl
if battery < 20 {
  speak("Low battery, returning to charge")
  go_charge()
} else if battery < 50 {
  speak("Battery medium")
} else {
  speak("Battery good")
}
```

#### 循环
```rsl
# for 循环
for i in range(0, 10) {
  move.forward(0.5)
  rotate(36)
}

# while 循环
while sense.ultrasonic() > 0.3 {
  move.forward(0.2)
}

# 遍历列表
for obj in objects {
  speak("I see " + obj.label)
}
```

#### 事件处理
```rsl
# 事件监听
on button.pressed {
  speak("Button pressed!")
}

on obstacle.detected {
  move.stop()
  rotate(90)
}

on voice.command("stop") {
  move.stop()
  speak("Stopped")
}
```

#### 并行执行
```rsl
parallel {
  move.forward(1.0)
  speak("Moving forward")
}

parallel {
  vision.detect("person")
  voice.listen()
}
```

---

## 5. 表达式

### 5.1 算术运算

```rsl
let sum = 1 + 2
let diff = 5 - 3
let product = 4 * 5
let quotient = 10 / 2
let power = 2 ^ 8
let mod = 17 % 5
```

### 5.2 比较运算

```rsl
let a = 1 < 2
let b = 3 >= 3
let c = "hello" == "hello"
let d = 5 != 3
```

### 5.3 逻辑运算

```rsl
let a = true and false  # false
let b = true or false   # true
let c = not true        # false
```

### 5.4 成员访问

```rsl
let result = ai.detect("person")
let label = result.objects[0].label
let confidence = result.objects[0].confidence
```

---

## 6. 标准库

### 6.1 动作库 (Actions)

| 函数 | 描述 | 参数 |
|------|------|------|
| `move.forward(speed)` | 前进 | speed: 0.0-1.0 |
| `move.backward(speed)` | 后退 | speed: 0.0-1.0 |
| `move.stop()` | 停止 | - |
| `rotate.left(degrees)` | 左转 | degrees: 数值 |
| `rotate.right(degrees)` | 右转 | degrees: 数值 |
| `grab(force)` | 抓取 | force: 0.0-1.0 |
| `release()` | 释放 | - |
| `speak(text)` | 语音输出 | text: 字符串 |
| `light.on(color)` | 开灯 | color: 颜色字符串 |

### 6.2 感知库 (Sensors)

| 函数 | 描述 | 返回类型 |
|------|------|----------|
| `sense.ultrasonic()` | 超声波距离 | sensor_data |
| `sense.infrared()` | 红外传感器 | sensor_data |
| `sense.touch()` | 触碰传感器 | bool |
| `vision.detect(type)` | 视觉检测 | ai_result |
| `voice.listen()` | 音频采集 | sensor_data |
| `voice.recognize()` | 语音识别 | ai_result |
| `power.battery()` | 电池电量 | number |
| `position.current()` | 当前位置 | map |

### 6.3 AI 库

| 函数 | 描述 | 返回类型 |
|------|------|----------|
| `ai.detect(type)` | 目标检测 | ai_result |
| `ai.gesture()` | 手势识别 | string |
| `ai.path_plan(start, goal)` | 路径规划 | list |
| `ai.follow(target)` | 人物跟随 | void |
| `ai.predict(action)` | 动作预测 | ai_result |
| `ai.emotion()` | 情绪识别 | string |

---

## 7. 模块系统

### 7.1 导入模块

```rsl
import actions
import sensors
import ai

# 使用别名
import actions as act
import custom.skill as my_skill
```

### 7.2 导出

```rsl
skill my_skill {
  export fn helper_function() {
    # ...
  }
}
```

---

## 8. 示例程序

### 8.1 智能清扫机器人

```rsl
skill cleaning_robot {
  version = "1.0.0"

  fn setup() {
    move.init()
    sense.ultrasonic.init()
    vision.init()
  }

  fn loop() {
    if power.battery() < 20 {
      speak("Low battery, returning to charge")
      go_charge()
      return
    }

    let dist = sense.ultrasonic()
    if dist < 0.5 {
      speak("Obstacle detected")
      rotate(90)
    } else {
      move.forward(0.5)
    }
  }

  fn go_charge() {
    let path = ai.path_plan(
      start: position.current(),
      goal: {x: 0, y: 0}
    )
    for point in path {
      move.to(point)
    }
    speak("Charging")
  }
}
```

### 8.2 手势控制

```rsl
skill gesture_control {
  fn on_gesture() {
    let gesture = ai.gesture()

    if gesture == "wave" {
      speak("Hello!")
      move.forward(0.5)
    }
    else if gesture == "stop" {
      move.stop()
      speak("Stopped")
    }
    else if gesture == "come" {
      move.forward(1.0)
    }
  }
}
```

---

## 9. 编译目标

RSL 支持编译到以下目标平台：

| 目标 | 扩展名 | 说明 |
|------|--------|------|
| Python | `.py` | 兼容 Python 3.8+ |
| C++ | `.cpp` | 兼容 C++17 |
| ROS 2 | `.cpp` + `.hpp` | 支持 rclcpp |
| Home Assistant | `.yaml` | 自动化脚本 |
| JavaScript | `.js` | Web 机器人控制 |

---

## 10. 语法速查表

```
skill name { ... }           # 定义技能包
fn name() { ... }           # 定义函数
let x = value               # 声明变量
if condition { ... }        # 条件
for x in collection { ... } # 循环
on event { ... }            # 事件监听
move.forward(speed)         # 动作
sense.ultrasonic()          # 感知
ai.detect("person")         # AI
import module               # 导入
export fn name() { ... }    # 导出
parallel { ... }            # 并行
```

---

*版本: 1.0.0 | 最后更新: 2024*

# RoboSkill DSL (RSL) Language Specification v1.0
## Domain-Specific Language for Robot Skill Development

[English](./SPEC.md) | 中文

---

## 1. Language Overview
RoboSkill DSL (RSL) is a domain-specific language designed exclusively for robot skill development. It provides concise, highly readable syntax that enables developers (including AI models) to rapidly write cross-platform robot control programs.

### 1.1 Design Goals
- **Minimalist Syntax**: Natural language-like declarative grammar, eliminating boilerplate code
- **AI-Friendly**: Clear structural syntax for AI models to auto-generate valid code
- **Hardware-Agnostic**: Supports diverse robot SDKs via an adapter layer
- **Modular**: Supports skill packages, functions, and event handling
- **Compilable**: Transpiles to Python, C++, ROS 2, Home Assistant, and other target platforms

### 1.2 Core Features
✓ Basic Data Types: `number`, `bool`, `string`, `list`, `sensor_data`, `ai_result`
✓ Action Commands: `move`, `rotate`, `grab`, `release`, `speak`, `light`
✓ Control Structures: `if/else`, `for`, `while`, `on_event`, `parallel`
✓ AI Interfaces: `vision.detect`, `voice.recognize`, `path.plan`, `predict`
✓ Modularity: Skill packages, function definitions, event listeners
✓ Hardware Abstraction: Unified adapter layer

---

## 2. Lexical Specification
### 2.1 Keywords
```
skill, fn, return, if, else, for, while, on, in, with
true, false, nil
move, rotate, grab, release, speak, light, wait, sleep
sense, detect, recognize, plan, predict, follow
module, import, export, async, await
parallel, when, always, never
```

### 2.2 Identifiers
- Composed of letters, numbers, and underscores
- Cannot start with a number
- Case-sensitive
- Recommended convention: `snake_case`

### 2.3 Basic Literals
```rsl
# Numbers
42
3.14
-273.15

# Booleans
true
false

# Strings
"Hello, Robot!"
'Single quotes also work'

# Lists
[1, 2, 3]
["apple", "banana"]

# Sensor Data
{type: "distance", value: 1.5, unit: "m"}
{type: "camera", objects: ["person", "cup"]}
```

### 2.4 Comments
```rsl
# Single-line comment

##
Multi-line comment
Spanning multiple lines
##
```

---

## 3. Data Types
### 3.1 Built-in Types
| Type | Description | Example |
|------|-------------|---------|
| `number` | Integer or floating-point | `42`, `3.14` |
| `bool` | Boolean value | `true`, `false` |
| `string` | Text string | `"text"` |
| `list` | Ordered array | `[1, 2, 3]` |
| `map` | Key-value structure | `{key: value}` |
| `sensor_data` | Structured sensor data | `{type, value, timestamp}` |
| `ai_result` | AI processing output | `{type, data, confidence}` |

### 3.2 Type System
```rsl
# Explicit type declaration (optional)
let speed: number = 1.5
let name: string = "Robot-001"

# Type inference
let speed = 1.5        # Infers to number
let is_active = true   # Infers to bool

# Sensor/AI data types
let distance = sense.ultrasonic()    # Returns sensor_data
let objects = vision.detect("person") # Returns ai_result
```

---

## 4. Syntax Structures
### 4.1 Skill Package Definition
```rsl
skill cleaning_robot {
  # Skill metadata
  version = "1.0.0"
  author = "RoboTeam"
  description = "Smart Cleaning Robot"

  # Skill initialization
  fn setup() {
    move.init()
    sense.ultrasonic.init()
    vision.init()
  }

  # Main execution loop
  fn loop() {
    let obstacle = sense.ultrasonic() < 0.5
    if obstacle {
      rotate(90)
    } else {
      move.forward(0.5)
    }
  }
}
```

### 4.2 Function Definition
```rsl
fn calculate_distance(x1, y1, x2, y2) -> number {
  let dx = x2 - x1
  let dy = y2 - y1
  return math.sqrt(dx * dx + dy * dy)
}

fn move_to_target(target_x, target_y) {
  let distance = calculate_distance(pos.x, pos.y, target_x, target_y)
  while distance > 0.1 {
    move.forward(distance)
    wait(100)
  }
}
```

### 4.3 Action Commands
```rsl
# Movement
move.forward(speed: 1.0)
move.backward(speed: 0.5)
move.stop()

# Rotation
rotate.left(degrees: 90)
rotate.right(degrees: 45)
rotate.to(angle: 180)

# Gripping
grab()
release()
grab.with_force(0.8)

# Lighting
light.on(color: "red")
light.off()
light.blink(frequency: 2)

# Speech
speak("Hello, I am a robot!")
speak("Warning: Obstacle detected", priority: "high")
```

### 4.4 Perception Commands
```rsl
# Distance sensor
let dist = sense.ultrasonic()
let dist_front = sense.ultrasonic(direction: "front")

# Vision
let objects = vision.detect("person")
let gesture = vision.gesture()

# Voice
let command = voice.recognize()

# Power & Position
let battery = power.battery()
let pos = position.current()
```

### 4.5 AI Interfaces
```rsl
# Object detection
let result = ai.detect("person", confidence: 0.8)
if result.found {
  speak("I see a " + result.objects[0].label)
}

# Gesture recognition
let gesture = ai.gesture()
if gesture == "wave" {
  speak("Hello!")
}

# Path planning
let path = ai.path_plan(start: pos, goal: target, mode: "fast")
for point in path {
  move.to(point)
}

# Voice control
let cmd = ai.voice_recognize()
if cmd == "come here" {
  move.forward(1.0)
}
```

### 4.6 Control Structures
#### Conditionals
```rsl
if battery < 20 {
  speak("Low battery, returning to charge")
  go_charge()
} else if battery < 50 {
  speak("Battery medium")
} else {
  speak("Battery good")
}
```

#### Loops
```rsl
# For loop
for i in range(0, 10) {
  move.forward(0.5)
  rotate(36)
}

# While loop
while sense.ultrasonic() > 0.3 {
  move.forward(0.2)
}

# Iterate over list
for obj in objects {
  speak("I see " + obj.label)
}
```

#### Event Handling
```rsl
# Event listeners
on button.pressed {
  speak("Button pressed!")
}

on obstacle.detected {
  move.stop()
  rotate(90)
}

on voice.command("stop") {
  move.stop()
  speak("Stopped")
}
```

#### Parallel Execution
```rsl
parallel {
  move.forward(1.0)
  speak("Moving forward")
}

parallel {
  vision.detect("person")
  voice.listen()
}
```

---

## 5. Expressions
### 5.1 Arithmetic Operations
```rsl
let sum = 1 + 2
let diff = 5 - 3
let product = 4 * 5
let quotient = 10 / 2
let power = 2 ^ 8
let mod = 17 % 5
```

### 5.2 Comparison Operations
```rsl
let a = 1 < 2
let b = 3 >= 3
let c = "hello" == "hello"
let d = 5 != 3
```

### 5.3 Logical Operations
```rsl
let a = true and false  # false
let b = true or false   # true
let c = not true        # false
```

### 5.4 Member Access
```rsl
let result = ai.detect("person")
let label = result.objects[0].label
let confidence = result.objects[0].confidence
```

---

## 6. Standard Library
### 6.1 Action Library
| Function | Description | Parameters |
|----------|-------------|------------|
| `move.forward(speed)` | Move forward | `speed`: 0.0-1.0 |
| `move.backward(speed)` | Move backward | `speed`: 0.0-1.0 |
| `move.stop()` | Stop movement | - |
| `rotate.left(degrees)` | Rotate left | `degrees`: number |
| `rotate.right(degrees)` | Rotate right | `degrees`: number |
| `grab(force)` | Gripper close | `force`: 0.0-1.0 |
| `release()` | Gripper open | - |
| `speak(text)` | Audio output | `text`: string |
| `light.on(color)` | Turn light on | `color`: string |

### 6.2 Sensor Library
| Function | Description | Return Type |
|----------|-------------|-------------|
| `sense.ultrasonic()` | Ultrasonic distance | `sensor_data` |
| `sense.infrared()` | Infrared sensor | `sensor_data` |
| `sense.touch()` | Touch detection | `bool` |
| `vision.detect(type)` | Visual detection | `ai_result` |
| `voice.recognize()` | Speech-to-text | `ai_result` |
| `power.battery()` | Battery percentage | `number` |
| `position.current()` | Current coordinates | `map` |

### 6.3 AI Library
| Function | Description | Return Type |
|----------|-------------|-------------|
| `ai.detect(type)` | Object detection | `ai_result` |
| `ai.gesture()` | Gesture recognition | `string` |
| `ai.path_plan(start, goal)` | Path planning | `list` |
| `ai.follow(target)` | Target following | `void` |
| `ai.predict(action)` | Action prediction | `ai_result` |

---

## 7. Module System
### 7.1 Import Modules
```rsl
import actions
import sensors
import ai

# Alias imports
import actions as act
import custom.skill as my_skill
```

### 7.2 Export
```rsl
skill my_skill {
  export fn helper_function() {
    # Shared utility function
  }
}
```

---

## 8. Example Programs
### 8.1 Smart Cleaning Robot
```rsl
skill cleaning_robot {
  version = "1.0.0"

  fn setup() {
    move.init()
    sense.ultrasonic.init()
  }

  fn loop() {
    if power.battery() < 20 {
      speak("Low battery, returning to charge")
      go_charge()
      return
    }

    let dist = sense.ultrasonic()
    if dist < 0.5 {
      rotate(90)
    } else {
      move.forward(0.5)
    }
  }

  fn go_charge() {
    let path = ai.path_plan(
      start: position.current(),
      goal: {x: 0, y: 0}
    )
    for point in path {
      move.to(point)
    }
  }
}
```

### 8.2 Gesture Control
```rsl
skill gesture_control {
  fn on_gesture() {
    let gesture = ai.gesture()

    if gesture == "wave" {
      speak("Hello!")
      move.forward(0.5)
    }
    else if gesture == "stop" {
      move.stop()
      speak("Stopped")
    }
    else if gesture == "come" {
      move.forward(1.0)
    }
  }
}
```

---

## 9. Compilation Targets
RSL supports compilation to these platforms:

| Target | Extension | Description |
|--------|-----------|-------------|
| Python | `.py` | Python 3.8+ compatible |
| C++ | `.cpp` | C++17 standard |
| ROS 2 | `.cpp/.hpp` | rclcpp integration |
| Home Assistant | `.yaml` | Automation scripts |
| JavaScript | `.js` | Web robot control |

---

## 10. Syntax Cheat Sheet
```rsl
skill name { ... }           # Define skill package
fn name() { ... }           # Define function
let x = value               # Declare variable
if condition { ... }        # Conditional statement
for x in collection { ... } # For loop
on event { ... }            # Event listener
move.forward(speed)         # Movement action
sense.ultrasonic()          # Sensor reading
ai.detect("person")         # AI inference
import module               # Import module
export fn name() { ... }    # Export function
parallel { ... }            # Parallel execution
```

---
**Version**: 1.0.0 | Last Updated: 2024
