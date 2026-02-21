def op_to_str(a, b, op):
    if op == '+':
        x = a + b
    elif op == '-':
        x = a - b
    elif op == '*':
        x = a * b
    elif op == '/' and b != 0:
        x = a / b
    else:
        x = 0

    return f'{a} {op} {b} = {x}'
