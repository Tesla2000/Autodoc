from __future__ import annotations


def split_lines(
    line: str, line_length: int = 79, indentation_length: int = 4
) -> str:
    line = line.split()
    new_lines = [[]]
    tab = indentation_length * " "
    for word in line:
        last_line = new_lines[-1]
        if last_line and (
            sum(map(len, last_line)) + len(word) + len(last_line)
            > line_length - indentation_length
        ):
            new_lines[-1] = " ".join(new_lines[-1])
            new_lines.append([])
        new_lines[-1].append(word)
    new_lines[-1] = " ".join(new_lines[-1])
    return "".join(map((tab + "{}\n").format, new_lines))
