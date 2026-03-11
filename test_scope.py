from sqlglot import parse_one, exp
from sqlglot.optimizer.qualify import qualify
from sqlglot.optimizer.scope import build_scope

sql = """
with cte1 as (select id from base_table1),
     cte2 as (select id from base_table2)
select c1.id from cte1 c1 join cte2 c2 on c1.id = c2.id
"""

expression = parse_one(sql)
qualified = qualify(expression, validate_qualify_columns=False)
root = build_scope(qualified)

def resolve_table(table_alias, scope):
    print(f"Resolving {table_alias} in scope {scope}")
    source = scope.sources.get(table_alias)
    print(f"Source: {type(source)} - {source}")
    if isinstance(source, exp.Table):
        return [source.name]
    elif source.__class__.__name__ == "Scope":
        bases = []
        for alias, child_source in source.sources.items():
            bases.extend(resolve_table(alias, source))
        return bases
    elif source is None and scope.parent:
        return resolve_table(table_alias, scope.parent)
    return [table_alias]

main_scope = list(root.traverse())[0] # The outermost is usually the one with the final select?
# Actually root is the outermost scope.
for c in qualified.find_all(exp.Column):
    print(c.name, c.table)
    print("Resolved to:", resolve_table(c.table, root))

