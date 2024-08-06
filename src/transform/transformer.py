from __future__ import annotations

from typing import Sequence

import libcst as cst
from libcst import Expr
from libcst import FunctionDef
from libcst import Module
from libcst import SimpleStatementLine
from libcst import SimpleString

from src.config import Config
from src.generate_documentation import generate_documentation


class Transformer(cst.CSTTransformer):

    def __init__(self, module: Module, config: Config):
        super().__init__()
        self.config = config
        self.module = module

    def leave_FunctionDef(
        self, original_node: "FunctionDef", updated_node: "FunctionDef"
    ) -> "FunctionDef":
        attrs = ["body", "body", 0, "body", 0]
        statement_line = self._get_path_attrs(original_node, attrs)
        if (
            isinstance(statement_line, Expr)
            and isinstance(docstring := statement_line.value, SimpleString)
            and getattr(docstring, "quote", None) in ("'''", '"""')
        ):
            return updated_node
        return self._set_path_attrs(
            updated_node,
            ["body"],
            body=(
                SimpleStatementLine(
                    body=(
                        Expr(
                            value=SimpleString(
                                value=f'"""\n{generate_documentation()}\n"""',
                            )
                        ),
                    )
                ),
                *self._get_path_attrs(updated_node, ["body", "body"]),
            ),
        )

    def _get_path_attrs(self, elem, attrs: Sequence[str | int]):
        current_elem = elem
        for attr in attrs:
            if isinstance(attr, str) and not hasattr(current_elem, attr):
                return
            if isinstance(attr, int) and (
                not isinstance(current_elem, list | tuple | dict)
                or attr >= len(current_elem)
            ):
                return
            if isinstance(attr, str):
                current_elem = getattr(current_elem, attr)
            else:
                current_elem = current_elem[attr]
        return current_elem

    def _set_path_attrs(self, elem, attrs: Sequence[str | int], **kwargs):
        inner_element = self._get_path_attrs(elem, attrs)
        inner_element = inner_element.with_changes(**kwargs)
        for i in range(1, len(attrs) + 1):
            outer_element = self._get_path_attrs(elem, attrs[:-i])
            inner_element = outer_element.with_changes(
                **{attrs[-i]: inner_element}
            )
        return inner_element
