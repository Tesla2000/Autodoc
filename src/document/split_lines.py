from __future__ import annotations


def split_lines(
    documentation: str, line_length: int = 79, tab_length: int = 4
) -> str:
    new_lines = []
    for line in documentation.splitlines():
        line = line.split()
        line_lines = [[]]
        for word in line:
            last_line = line_lines[-1]
            if last_line and (
                sum(map(len, last_line)) + len(word) + len(last_line)
                > line_length - tab_length
            ):
                line_lines[-1] = " ".join(line_lines[-1])
                line_lines.append([])
            line_lines[-1].append(word)
        line_lines[-1] = " ".join(line_lines[-1])
        new_lines.append("".join(map("    {}\n".format, line_lines)))
    return "".join(new_lines)
