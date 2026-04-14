import ast
import re

with open("static/index.html", "r", encoding="utf-8") as f:
    text = f.read()

scripts = re.findall(r'<script>(.*?)</script>', text, re.DOTALL)
for i, s in enumerate(scripts):
    print(f"Script {i} length: {len(s)}")
    with open(f"scratch/script_{i}.js", "w", encoding="utf-8") as out:
        out.write(s)
