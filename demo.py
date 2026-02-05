import sqlite3
import json
from logicform import Logicform, Filter
from logicform import SchemaRegistry
from logicform import Compiler

def setup_db():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # 1. Create Tables
    # dim_shops
    cursor.execute("""
    CREATE TABLE dim_shops (
        shop_id TEXT PRIMARY KEY,
        shop_name TEXT,
        region_name TEXT
    )
    """)
    
    # dim_products
    cursor.execute("""
    CREATE TABLE dim_products (
        prod_id TEXT PRIMARY KEY,
        prod_name TEXT,
        category_name TEXT,
        price REAL
    )
    """)
    
    # dwd_sales_detail
    cursor.execute("""
    CREATE TABLE dwd_sales_detail (
        trx_id TEXT PRIMARY KEY,
        shop_id TEXT,
        prod_id TEXT,
        dt TEXT,
        qty INTEGER,
        total_amt REAL,
        target_amt REAL
    )
    """)
    
    # 2. Insert Dummy Data
    shops = [
        ('S01', 'Shop A (Shanghai)', 'Shanghai'),
        ('S02', 'Shop B (Shanghai)', 'Shanghai'),
        ('S03', 'Shop C (Beijing)', 'Beijing'),
    ]
    cursor.executemany("INSERT INTO dim_shops VALUES (?,?,?)", shops)
    
    prods = [
        ('P01', 'iPhone 15', 'Electronics', 6000),
        ('P02', 'MacBook Pro', 'Electronics', 12000),
        ('P03', 'Coffee', 'Food', 30),
    ]
    cursor.executemany("INSERT INTO dim_products VALUES (?,?,?,?)", prods)
    
    # Sales:
    # Shop A sold 10 iPhones (60k) target 50k -> Achieved
    # Shop C sold 100 Coffees (3k) target 5k -> Not Achieved
    sales = [
        ('T01', 'S01', 'P01', '2024-01-01', 10, 60000, 50000),
        ('T02', 'S01', 'P03', '2024-01-01', 20, 600, 500),
        ('T03', 'S03', 'P03', '2024-01-02', 100, 3000, 5000),
    ]
    cursor.executemany("INSERT INTO dwd_sales_detail VALUES (?,?,?,?,?,?,?)", sales)
    
    conn.commit()
    return conn

def run_demo():
    print("=== Logicform Semantic Layer Demo ===\n")
    conn = setup_db()
    compiler = Compiler(SchemaRegistry)
    
    # Mocking the NL -> Logicform step (which would be done by an LLM)
    test_cases = [
        {
            "nl": "Show me the total sales amount by region",
            "logicform": {
                "target_metrics": ["sales_volume"],
                "dimensions": ["shop.region"],
                "filters": []
            }
        },
        {
            "nl": "What is the sales achievement rate for Electronics in Shanghai?",
            "logicform": {
                "target_metrics": ["achievement_rate", "sales_volume", "sales_target"],
                "dimensions": [],
                "filters": [
                    {"field": "shop.region", "op": "==", "value": "Shanghai"},
                    {"field": "prod.category", "op": "==", "value": "Electronics"}
                ]
            }
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"--- Case {i} ---")
        print(f"User Query: {case['nl']}")
        
        # 1. Get Logicform (Mock)
        lf_dict = case['logicform']
        lf = Logicform(**lf_dict)
        print(f"Generated Logicform:\n{json.dumps(lf_dict, indent=2)}")
        
        # 2. Compile to SQL
        sql = compiler.compile(lf)
        print(f"\nGenerated SQL:\n{sql}")
        
        # 3. Execute
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
            cols = [desc[0] for desc in cursor.description]
            
            print("\nExecution Results:")
            print(f"{' | '.join(cols)}")
            print("-" * 30)
            for row in results:
                print(f"{' | '.join(map(str, row))}")
        except Exception as e:
            print(f"Error executing SQL: {e}")
            
        print("\n" + "="*40 + "\n")

    conn.close()

if __name__ == "__main__":
    run_demo()
