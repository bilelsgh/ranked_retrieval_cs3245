import re

def find_brackets(li):
    l = []
    temp_str = ""
    found_start = False
    for i, item in enumerate(li):
        if not found_start:
            if item.find("(") != -1:
                temp_str = item
                found_start = True
            else:
                l.append(item)
        else:
            temp_str += " OR " + item
            if item.find(")") != -1:
                temp_str += " OR " + item
                l.append(temp_str)
                found_start = False

    return l

def order_opr(query):    
    or_expr = query.split(" OR ")
    or_expr = find_brackets(or_expr)
    for i, expr in enumerate(or_expr):
        or_expr[i] = expr.split(" AND ")
    pass


query = "bill OR Gates AND (vista OR XP) AND NOT mac"
query = "bill OR Gates AND (vista OR XP)"
order_opr(query)