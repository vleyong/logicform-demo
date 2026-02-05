# Logicform LLM Prompt Example

This shows how the LLM bridges the gap between **Distinct User Queries** and **Standard Logicform Definitions**.

## System Prompt (Input to LLM)

```text
You are a data analyst assistant. 
Your goal is to translate user natural language queries into a JSON "Logicform".

### 1. Available Metrics (Choose from this list ONLY)
- `sales_volume`: Total money amount from sales. (Synonyms: revenue, gmvs, income)
- `sales_qty`: Total number of items sold. (Synonyms: volume, units)
- `achievement_rate`: Percentage of sales target achieved. (Synonyms: performance, target completion)

### 2. Available Dimensions (Choose from this list ONLY)
- `shop.region`: City or Region of the shop (e.g. Shanghai, Beijing)
- `prod.category`: Product category (e.g. Electronics, Food)
- `time.date`: The transaction date

### 3. Output Format
Return ONLY a valid JSON object with:
- target_metrics: [list of metric aliases]
- dimensions: [list of dimension fields]
- filters: [list of {field, op, value} objects]

---

### User Query Case 1
User: "How much money did we make in Shanghai?"

### LLM Reasoning
1. "How much money" -> Matches `sales_volume` description/synonyms.
2. "Shanghai" -> Is a value for `shop.region`.
3. Intent is filtering by region.

### LLM Output
{
  "target_metrics": ["sales_volume"],
  "dimensions": [],
  "filters": [
    {"field": "shop.region", "op": "==", "value": "Shanghai"}
  ]
}

---

### User Query Case 2
User: "Which region has the best performance?"

### LLM Reasoning
1. "Performance" -> Matches `achievement_rate` in our dictionary.
2. "Which region" -> User wants to break down by `shop.region`.
3. "Best" -> Implies sorting (handled by downstream or implicit in retrieval).

### LLM Output
{
  "target_metrics": ["achievement_rate"],
  "dimensions": ["shop.region"],
  "filters": []
}
```

## How this works
1.  **Schema Injection**: We programmatically inject the definitions (from `schema_registry.py`) into the Prompt.
2.  **Semantic Matching**: The LLM uses its pre-trained knowledge to match "Money", "Revenue", "Bucks" all to the standard ID `sales_volume`.
3.  **Deterministic Compilation**: Once the LLM outputs `"sales_volume"`, our Code Compiler takes over and turns it into `SUM(sales.total_amt)`.
