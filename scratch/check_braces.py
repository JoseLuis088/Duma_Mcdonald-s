def check_braces(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    brace_stack = []
    paren_stack = []

    for i, line in enumerate(lines):
        for char in line:
            if char == '{':
                brace_stack.append((i+1, char))
            elif char == '}':
                if brace_stack:
                    brace_stack.pop()
                else:
                    print(f"Unmatched '}}' at line {i+1}: {line}")
            elif char == '(':
                paren_stack.append((i+1, char))
            elif char == ')':
                if paren_stack:
                    paren_stack.pop()
                else:
                    print(f"Unmatched ')' at line {i+1}: {line}")

    if brace_stack:
        for b in brace_stack:
            print(f"Unmatched '{{' opened at line {b[0]}")
    if paren_stack:
        for p in paren_stack:
            print(f"Unmatched '(' opened at line {p[0]}")

check_braces('scratch/script_0.js')
