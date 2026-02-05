from typing import List, Dict, Optional, Literal
from dataclasses import dataclass

@dataclass
class Field:
    name: str
    description: str
    db_column: str  # The physical column name in Doris/DB
    is_primary: bool = False

@dataclass
class Table:
    name: str       # Physical table name
    alias: str      # Logical name for joining
    fields: Dict[str, Field]
    
    def get_field(self, name: str) -> Optional[Field]:
        return self.fields.get(name)

@dataclass
class Metric:
    name: str
    description: str
    formula: str  # SQL fragment e.g., "SUM(sales_amt)"
    format: str = "number"  # number, percent, currency

@dataclass
class Relationship:
    source_table: str
    target_table: str
    source_col: str
    target_col: str
    join_type: str = "LEFT JOIN"

# --- Schema Definition ---

# 1. Dimensions
dim_shops = Table(
    name="dim_shops",
    alias="shop",
    fields={
        "id": Field("id", "Shop ID", "shop_id", is_primary=True),
        "name": Field("name", "Shop Name", "shop_name"),
        "region": Field("region", "Region", "region_name"),
    }
)

dim_products = Table(
    name="dim_products",
    alias="prod",
    fields={
        "id": Field("id", "Product ID", "prod_id", is_primary=True),
        "name": Field("name", "Product Name", "prod_name"),
        "category": Field("category", "Category", "category_name"),
        "price": Field("price", "Unit Price", "price"),
    }
)

# 2. Facts
dwd_sales = Table(
    name="dwd_sales_detail",
    alias="sales",
    fields={
        "id": Field("id", "Transaction ID", "trx_id", is_primary=True),
        "shop_id": Field("shop_id", "Shop ID FK", "shop_id"),
        "prod_id": Field("prod_id", "Product ID FK", "prod_id"),
        "date": Field("date", "Date", "dt"),
        "quantity": Field("quantity", "Qty", "qty"),
        "amt": Field("amt", "Amount", "total_amt"),
        "target_amt": Field("target_amt", "Target Amount", "target_amt") # Virtual column for demo simplicity
    }
)

# 3. Registry
class SchemaRegistry:
    tables: Dict[str, Table] = {
        "shop": dim_shops,
        "prod": dim_products,
        "sales": dwd_sales
    }
    
    relationships: List[Relationship] = [
        Relationship("sales", "shop", "shop_id", "shop_id"),
        Relationship("sales", "prod", "prod_id", "prod_id"),
    ]
    
    metrics: Dict[str, Metric] = {
        "sales_volume": Metric("sales_volume", "Total Sales Amount", "SUM(sales.total_amt)", "currency"),
        "sales_qty": Metric("sales_qty", "Total Sales Quantity", "SUM(sales.qty)", "number"),
        "sales_target": Metric("sales_target", "Target Sales Amount", "SUM(sales.target_amt)", "currency"),
        
        # Derived Metric defined in Semantic Layer!
        # Note: In a real system, this might be handled by a sophisticated expression parser.
        # Here we substitute the names of other metrics or columns.
        "achievement_rate": Metric(
            "achievement_rate", 
            "Sales Achievement Rate", 
            "CAST(SUM(sales.total_amt) AS FLOAT) / NULLIF(SUM(sales.target_amt), 0)", 
            "percent"
        )
    }

    @classmethod
    def get_table(cls, alias: str) -> Optional[Table]:
        return cls.tables.get(alias)

    @classmethod
    def get_metric(cls, name: str) -> Optional[Metric]:
        return cls.metrics.get(name)

    @classmethod
    def find_path(cls, start_table_alias: str, end_table_alias: str) -> List[Relationship]:
        """Simple pathfinding for Star Schema (Fact -> Dim)"""
        # In this demo, we assume queries start from Fact (sales) and go to Dims
        for rel in cls.relationships:
            if rel.source_table == start_table_alias and rel.target_table == end_table_alias:
                return [rel]
        return []
