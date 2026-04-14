with open(r"c:\Users\Jose Luis Dominguez\Desktop\Duma Mcdonald's\static\index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()
    for i in range(2155, 2170):
        print(f"{i+1}: {repr(lines[i])}")
