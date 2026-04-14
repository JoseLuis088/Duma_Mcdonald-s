import os

path = r"c:\Users\Jose Luis Dominguez\Desktop\Duma Mcdonald's\static\index.html"

if not os.path.exists(path):
    print(f"File not found: {path}")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Correct logical cleanup:
# We know from view_file that line 2707 is '        };' and line 2708 is junk.
# Lines 2708 to 2713 are junk.
# Note: lines is 0-indexed, so line 2708 is index 2707.

if len(lines) >= 2714 and "or al generar el PDF" in lines[2707]:
    print("Found junk. Cleaning up...")
    new_lines = lines[:2707] + lines[2713:]
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Cleanup successful.")
else:
    print(f"Junk not found at expected position or file is shorter than expected. Total lines: {len(lines)}")
    if len(lines) > 2707:
        print(f"Line 2708: {lines[2707]}")
