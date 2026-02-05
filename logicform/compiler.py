from typing import List, Set
from .models import Logicform, Filter
from .schema import SchemaRegistry, Relationship

class Compiler:
    def __init__(self, schema: SchemaRegistry):
        self.schema = schema
        # In a real scenario, we'd have a more dynamic way to pick the base table.
        # For this demo, we assume 'sales' (dwd_sales) is the central Fact table.
        self.base_table_alias = "sales"

    def compile(self, lf: Logicform) -> str:
        """
        Transpiles Logicform to SQL.
        """
        select_clauses = []
        join_clauses: List[str] = []
        where_clauses = []
        group_by_clauses = []
        
        # Track which tables we need to join
        # We start with the base table
        involved_table_aliases: Set[str] = {self.base_table_alias}

        # 1. Process Dimensions (GROUP BY)
        for dim_ref in lf.dimensions:
            # dim_ref e.g., "shop.region"
            table_alias, field_name = self._parse_ref(dim_ref)
            involved_table_aliases.add(table_alias)
            
            # Resolve physical column
            # For simplicity, assuming alias matches schema alias
            table = self.schema.get_table(table_alias)
            if not table:
                raise ValueError(f"Unknown table alias: {table_alias}")
            
            field = table.get_field(field_name)
            if not field:
                raise ValueError(f"Unknown field: {field_name} in table {table_alias}")
            
            col_expr = f"{table.alias}.{field.db_column}"
            select_clauses.append(f"{col_expr} AS `{dim_ref}`")
            group_by_clauses.append(col_expr)

        # 2. Process Metrics (SELECT)
        for metric_name in lf.target_metrics:
            metric = self.schema.get_metric(metric_name)
            if not metric:
                raise ValueError(f"Unknown metric: {metric_name}")
            
            # Metric formula is already a SQL fragment, e.g. "SUM(sales.amt)"
            # We assume it uses the correct table aliases.
            select_clauses.append(f"{metric.formula} AS `{metric_name}`")
            
            # If the metric formula involves other tables (not implemented in this simple parser),
            # we would need to parse dependencies. Here we assume metrics are mostly on the Fact table.

        # 3. Process Filters (WHERE)
        for flt in lf.filters:
            table_alias, field_name = self._parse_ref(flt.field)
            involved_table_aliases.add(table_alias)
            
            table = self.schema.get_table(table_alias)
            field = table.get_field(field_name)
            col_expr = f"{table.alias}.{field.db_column}"
            
            # quote value if string
            val = flt.value
            if isinstance(val, str):
                val = f"'{val}'"
            
            where_clauses.append(f"{col_expr} {flt.op} {val}")

        # 4. Generate Joins
        # Find paths from base_table to all other involved tables
        for target_alias in involved_table_aliases:
            if target_alias == self.base_table_alias:
                continue
                
            path = self.schema.find_path(self.base_table_alias, target_alias)
            if not path:
                raise ValueError(f"No join path found between {self.base_table_alias} and {target_alias}")
            
            for rel in path:
                join_str = f"{rel.join_type} {self.schema.get_table(rel.target_table).name} AS {rel.target_table} ON {rel.source_table}.{rel.source_col} = {rel.target_table}.{rel.target_col}"
                if join_str not in join_clauses:
                     join_clauses.append(join_str)

        # 5. Assemble Query
        base_table = self.schema.get_table(self.base_table_alias)
        sql = f"SELECT\n    {', '.join(select_clauses)}\n"
        sql += f"FROM {base_table.name} AS {base_table.alias}\n"
        
        if join_clauses:
            sql += "\n".join(join_clauses) + "\n"
            
        if where_clauses:
            sql += "WHERE " + " AND ".join(where_clauses) + "\n"
            
        if group_by_clauses:
            sql += "GROUP BY " + ", ".join(group_by_clauses) + "\n"
            
        if lf.limit:
            sql += f"LIMIT {lf.limit}"

        return sql

    def _parse_ref(self, ref: str):
        """Parses 'table.field' -> ('table', 'field')"""
        parts = ref.split('.')
        if len(parts) != 2:
            raise ValueError(f"Invalid reference format: {ref}. Expected table.field")
        return parts[0], parts[1]
