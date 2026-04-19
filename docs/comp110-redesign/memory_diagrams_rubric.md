# COMP110 Memory Diagram Rubric · v0 提取

> **来源**：`https://comp110-26s.github.io/static/slides/memory_diagrams_v0.pdf`（1 页 PDF，Kris Jordan，QZ00 Study Guide 附）
> **扒取时间**：2026-04-18 20:32 ET
> **作用**：Phase 2 AI TA 做 memory diagram 预评分时的权威规则表。若学生画的 diagram 与此规则冲突，TA 用 Kris 的原话回复以保证与课堂一致。
> **版本缺口**：v0 仅覆盖 QZ00 范围。QZ01-QZ03 需要的 List mutation / Dict / for-loop / class instance 规则 Kris 在后续 lecture 讲但未单独发 PDF——Phase 2 需从 cl## slides 里补齐或让 AI TA 在规则外回退到 Python Tutor 模拟。

---

## 1. 图的三栏结构

每张 memory diagram 必须包含三列：

| 列 | 名称 | 内容 |
|----|------|------|
| 左 | Function Call **Stack** | 起始帧为 `Globals` |
| 中 | **Heap** | 堆对象（函数、list、dict、instance 等） |
| 右 | Printed **Output** | `print()` 累计输出 |

评估顺序：从代码首行自顶向下逐行。遇到 left column 的 construct，执行右列对应的 action。

---

## 2. 逐构造规则表

### 2.1 Docstring 或 `# Comment`
**动作**：忽略。Docstring 是给人看的文档，Python 实际跳过。

### 2.2 Function Definition
1. 在当前 working frame 内，新增函数名 + value box
2. 在 Heap 加一个函数对象，标注 `Fn Lines S - E`（S = 函数定义起始行号，E = 结束行号）。给它一个 Heap ID `ID:#`（从 0 开始递增，每 heap 对象 +1）
3. Stack 的 value box 里写入该 Heap 对象的 `ID:#`，完成绑定
4. **跳过函数体**！不要逐行评估缩进的函数定义体

### 2.3 `print()` 函数调用
完全求值 argument expression → 结果值加到 Output 列。**不加引号**。

### 2.4 Function Call Expression（一般函数调用）
1. **求值参数**：若 argument 是表达式而非字面量，先从左到右逐个简化到单值
2. **名称解析**：按下方 Name Resolution 规则确认被调名对应一个 function definition
3. **参数匹配**：检查第 1 步的 argument 和 function definition 的 parameter 列表，数量 + 顺序 + 类型必须完全对应
   - 不匹配 → 写 `Function Call Error on Line #C`（C = 错误所在行），停止后续评估
4. **建立新 call frame**：
   - A. 画一条线分隔当前 working frame 与新 frame
   - B. 新 frame 左上角写函数名
   - C. 函数名下方左侧写 `RA: C`（C = 发起调用的代码行号，"Return Address"）
   - D. 右侧每行列出一个 parameter 名 + 空 value
   - E. 第 1 步求值后的 argument 值按顺序填入对应 parameter value
5. 跳到函数体首行。**当前 working frame 现在是新建的这个 frame**，按同规则继续逐行评估

### 2.5 Return Statement
1. Return 只能出现在函数体内——其他位置 → **Error**
2. 完全求值 `return` 后的表达式到单值
3. 在当前 working frame 的 RA 下方加一行 `RV: <value>`（Return Value）
4. 跳到当前 frame 的 RA 所在行号，把原函数调用表达式替换/简化为 `RV`
5. **当前 working frame 切换**：stack 上最底层还没有 RV 的 frame 成为新的 working frame

### 2.6 Name Resolution（变量/参数名查找）
1. 先在当前 working frame 找名字。找到 → 用它绑定的值替换表达式里的名字
2. 找不到 → 到 globals frame 找
3. globals 也找不到 → **NameError**

### 2.7 Arithmetic Expressions
- 按 PEMDAS（括号 > 幂 > 乘除 > 加减）求值
- 同优先级（×÷ 或 +-）→ 从左到右
- 同一运算 → 先评估左操作数，再右操作数

---

## 3. v0 缺口（QZ01+ 需要补的规则）

Kris 的 v0 PDF 只覆盖 QZ00（函数 + 算术）。以下 QZ01-QZ03 / final 范围的规则 **v0 没有**，Phase 2 AI TA 预评分时必须用 Python Tutor 模拟或补写：

| 范围 | 缺失规则 | 建议来源 |
|------|----------|----------|
| QZ01（Lists, Loops） | list 字面量在 Heap 创建、list mutation（`append`/`pop`/索引赋值）、aliasing（`a = b` 指向同一 heap ID）、for-loop 迭代变量每轮重新绑定 | cl15-cl19 slides |
| QZ02（Dicts, Functions） | dict 字面量 heap 布局、`dict[key] = value` 增删、`in` 操作、nested collection | cl20-cl24 slides |
| QZ03（Recursion, OOP 初步） | 递归调用时 stack 累积多个同名 frame、类定义在 heap 的 class object、`self` 参数隐式第一位、`instance.attr` 查找链（instance → class → MRO） | cl25-cl31 slides |
| Final（LinkedList, Magic methods） | `__str__`/`__eq__`/`__len__` 调用时触发函数调用规则、node chain 的 heap 表示、`None` 哨兵 | cl28-cl33 slides |

**Phase 2 实现建议**：
- 第一层：rubric-based 规则引擎，严格遵守 v0 规则（已结构化，直接翻成 JSON）
- 第二层：规则外的场景（list / dict / class）→ 调 Python Tutor 后端（`https://pythontutor.com/render.html#code=...`）获取权威 trace → diff 学生答案
- 第三层：Socratic AI 用 Kris 的规则原话解释差异（不给答案，只问引导问题，保持 DESIGN_BRIEF §7 的行为约束）

---

## 4. 机器可读结构（供 Phase 2 system prompt 注入）

```json
{
  "rubric_version": "v0",
  "source_url": "https://comp110-26s.github.io/static/slides/memory_diagrams_v0.pdf",
  "scope": ["QZ00"],
  "columns": ["stack", "heap", "output"],
  "evaluation_order": "top-to-bottom-line-by-line",
  "constructs": {
    "docstring_or_comment": {"action": "ignore"},
    "function_definition": {
      "stack": "add name + value box pointing to heap ID",
      "heap": "add Fn Lines S-E with ID:# counter",
      "skip_body": true
    },
    "print_call": {
      "action": "evaluate arg expression, append result to output column (no quotes)"
    },
    "function_call": {
      "steps": [
        "evaluate args left-to-right to single values",
        "resolve function name via name-resolution",
        "match param count/order/type",
        "create new frame: divider, name, RA:<line>, params with values",
        "jump to function body first line; new frame is working frame"
      ],
      "error_syntax": "Function Call Error on Line #C"
    },
    "return_statement": {
      "validity": "must be inside function body",
      "steps": [
        "evaluate expression to single value",
        "write RV: <value> under RA in current frame",
        "jump to RA line, substitute call expression with RV",
        "working frame = lowest frame without RV"
      ]
    },
    "name_resolution": {
      "order": ["current_working_frame", "globals_frame"],
      "on_miss": "NameError"
    },
    "arithmetic": {
      "precedence": "PEMDAS",
      "tie_breaker": "left-to-right; left operand evaluated before right"
    }
  },
  "common_student_errors": [
    "Forgetting heap ID on function object",
    "Writing RA value instead of line number",
    "Evaluating function body before establishing frame",
    "Skipping name resolution step and guessing value",
    "Printing with quotes in output column"
  ]
}
```

上面的 `common_student_errors` 是根据 v0 规则逆推的高频错误类别——Phase 2 AI TA 遇到学生犯这些错误时，应该用规则对应原话提示，**不要直接给答案**（参见 DESIGN_BRIEF §7 NEVER 规则）。

---

## 5. 使用示例（Phase 2 TA 应答模板）

学生问：「我的 memory diagram 在 function call 那里扣分了，怎么改？」

TA 回：
```
你能先告诉我这个 function call 在哪一行吗？我看你的 diagram 里新建了一个 frame，
但看起来 RA 字段是空的。按 v0 规则，RA 应该是调用表达式所在的那一行号——
这个值对你来说怎么确定？
```

（Socratic：不给答案，只引导学生回到规则 §2.4 step 4C。）
