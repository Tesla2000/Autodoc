from __future__ import annotations

from typing import Sequence


def conv2docstring_lines(
    parameters: tuple[str, ...],
    return_value: str,
    missing_parameter_names: Sequence[str],
) -> tuple[tuple[str, ...], str]:
    return (
        tuple(
            f":param {name}: {description}"
            for name, description in zip(missing_parameter_names, parameters)
        ),
        f":return: {return_value}",
    )
