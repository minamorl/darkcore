#!/usr/bin/env python3
import re
from pathlib import Path

# 対象ディレクトリ
base = Path("darkcore")

# 追記対象のパターン
patterns = [
    (r"def bind\(.*\):", "  # type: ignore[override]"),
    (r"def ap\(.*\):", "  # type: ignore[override]"),
    (r"def pure\(.*\):", "  # type: ignore[override]"),
    (r"return self.bind\(lambda x: self.pure\(f\(x\)\)\)", "  # type: ignore[arg-type]"),
    (r"return f\(self._value\)", "  # type: ignore[return-value]"),
]

def process_file(path: Path):
    text = path.read_text().splitlines()
    new_lines = []
    for line in text:
        fixed = False
        for pat, comment in patterns:
            if re.search(pat, line) and comment not in line:
                line = line.rstrip() + comment
                fixed = True
                break
        new_lines.append(line)
    path.write_text("\n".join(new_lines) + "\n")
    return path

def main():
    for py in base.glob("*.py"):
        if py.name in {"__init__.py"}:
            continue
        print(f"patching {py}")
        process_file(py)

if __name__ == "__main__":
    main()
