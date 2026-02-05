# Logicform Semantic Layer Demo

This demo illustrates a **Headless BI / Semantic Layer** architecture. It shows how to translate Natural Language (intent) into deterministically correct SQL using a "Logicform" intermediate layer, thus preventing LLM hallucinations in analytics.

## Project Structure

The project uses a standard Python package structure:

1.  **`logicform/schema.py`** (Semantic Layer)
    *   **Role**: The "source of truth".
    *   **Content**: Defines your Tables (`Table`), physical columns (`Field`), Metrics (`Metric`), and Relationships.

2.  **`logicform/models.py`** (The Protocol)
    *   **Role**: The contract / DSL.
    *   **Content**: Pydantic models defining the query structure (`Logicform`, `Filter`).

3.  **`logicform/compiler.py`** (The Engine)
    *   **Role**: The deterministic translation engine.
    *   **Content**: Takes `Logicform` + `SchemaRegistry` -> SQL.

4.  **`demo.py`** (Entry Point)
    *   **Role**: The runnable script.
    *   **Content**:
        *   Imports from the `logicform` package.
        *   Runs the end-to-end verification.

5.  **`docs/prompt_example.md`**
    *   **Role**: Documentation on how to prompt the LLM.

## How to Run

1.  Open a terminal.
2.  Navigate to the directory:
    ```bash
    cd logicform_demo
    ```
3. Run with uv:
    ```bash
    uv run demo.py
    ```

## Expected Output

You will see the pipeline in action:
1.  **User Query**: The natural language input.
2.  **Generated Logicform**: The structured JSON intent (what the LLM would produce).
3.  **Generated SQL**: The correct SQL derived from the Semantic Layer.
4.  **Execution Results**: The actual data rows from the database.

## Key Takeaways

*   **No Hallucinations**: Valid SQL is generated because the *structure* is controlled by code, not the LLM.
*   **Encapsulated Logic**: Complex formulas (like `achievement_rate`) live in code (`schema_registry.py`), not in the LLM's prompt.
