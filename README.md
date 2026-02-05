# Logicform 语义层（Semantic Layer）演示

本项目演示了一个 **Headless BI / Semantic Layer（语义层）** 的架构实现。它展示了如何将自然语言（用户意图）转化为确定性、无幻觉的 SQL 查询，核心机制是引入了 "Logicform" 中间层。

## 项目结构 (Project Structure)

本项目采用了标准的 Python 包结构：

1.  **`logicform/schema.py`** (语义层 / Semantic Layer)
    *   **角色**：事实源头 (Single Source of Truth)。
    *   **内容**：定义了所有的数据表 (`Table`)、物理字段 (`Field`)、指标公式 (`Metric`) 以及表之间的关联关系 (`Relationship`)。
    *   **核心价值**：LLM 只能看到这层定义，看不到底层的物理表结构。复杂的指标逻辑（如“达成率”）是在这里通过 SQL 片段预定义的，保证了计算口径的一致性。

2.  **`logicform/models.py`** (协议 / DSL)
    *   **角色**：通信契约。
    *   **内容**：使用 Pydantic 定义的标准查询结构 (`Logicform`, `Filter`)。这也是所有 LLM 需要输出的目标 JSON 格式。

3.  **`logicform/compiler.py`** (引擎 / Engine)
    *   **角色**：确定性翻译器。
    *   **内容**：负责将 `Logicform` 对象结合 `SchemaRegistry` 编译成可执行的 SQL。
        *   **指标展开**：自动将 `sales_volume` 替换为 `SUM(sales.amt)`。
        *   **路径探索**：根据查询维度，自动补充 `LEFT JOIN` 语句。

4.  **`demo.py`** (入口脚本 / Entry Point)
    *   **角色**：演示程序。
    *   **内容**：
        *   初始化一个内存 SQLite 数据库。
        *   插入模拟数据（店铺、产品、销售记录）。
        *   运行端到端的演示流程：**自然语言 -> Logicform -> SQL -> 结果**。

5.  **`docs/prompt_example.md`**
    *   **角色**：LLM 提示词指南。

## 如何运行 (How to Run)

1.  打开终端 (Terminal)。
2.  进入项目目录：
    ```bash
    cd logicform_demo
    ```
3.  使用 `uv` 运行：
    ```bash
    uv run demo.py
    ```

## 预期输出 (Expected Output)

您将看到完整的执行流水线：
1.  **用户查询 (User Query)**：输入的自然语言问题。
2.  **Logicform**：生成的结构化 JSON 意图（模拟 LLM 的输出）。
3.  **Generated SQL**：由编译器基于语义层生成的准确 SQL。
4.  **执行结果 (Execution Results)**：从数据库查询出的实际数据。

## 核心价值 (Key Takeaways)

*   **零幻觉 (No Hallucinations)**：因为 SQL 的结构是由确定性的代码控制的，而不是由 LLM 生成的，所以保证了语法的绝对正确。
*   **逻辑封装 (Encapsulated Logic)**：复杂的计算逻辑（如 `achievement_rate`）被封装在代码库 (`schema.py`) 中，而不是暴露在 Prompt 里，确保了业务逻辑的统一管理。
