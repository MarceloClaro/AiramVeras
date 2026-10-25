import sys

target = sys.argv[1] if len(sys.argv) > 1 else "docs/index.html"
with open(target, "r", encoding="utf-8") as f:
    lines = f.readlines()

script_lines = []
in_script = False
for i, l in enumerate(lines, 1):
    if "<script>" in l:
        in_script = True
        continue
    if "</script>" in l and in_script:
        in_script = False
        break
    if in_script:
        script_lines.append((i, l))

stack = []
for line_num, line in script_lines:
    i = 0
    in_str = None
    while i < len(line):
        ch = line[i]
        if in_str:
            if ch == "\\":
                i += 2
                continue
            elif ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'", '`'):
                in_str = ch
            elif ch in ('{', '(', '['):
                stack.append((ch, line_num, line.strip()))
            elif ch in ('}', ')', ']'):
                match_map = {'}': '{', ')': '(', ']': '['}
                if not stack:
                    print(f"Unmatched closing {ch} at line {line_num}: {line.strip()}")
                else:
                    last_ch, last_line, last_text = stack.pop()
                    if last_ch != match_map[ch]:
                        print(f"Mismatched {ch} at line {line_num} with {last_ch} at line {last_line}")
        i += 1

print(f"{target} -> Unclosed items remaining on stack: {len(stack)}")
for ch, lnum, ltext in stack:
    print(f"  Unclosed '{ch}' opened at line {lnum}: {ltext[:70]}")
