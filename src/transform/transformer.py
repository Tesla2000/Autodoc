from __future__ import annotations

import traceback
from functools import partial
from typing import Sequence

import libcst as cst
from libcst import Expr
from libcst import FunctionDef
from libcst import Module
from libcst import SimpleStatementLine
from libcst import SimpleString

from src.config import Config
from src.document.conv2docstring_lines import conv2docstring_lines
from src.document.generate_descriptions import generate_descriptions
from src.document.split_lines import split_lines


class Transformer(cst.CSTTransformer):

    def __init__(self, module: Module, config: Config):
        super().__init__()
        self.config = config
        self.module = module

    def leave_FunctionDef(
        self, original_node: "FunctionDef", updated_node: "FunctionDef"
    ) -> "FunctionDef":
        expected_parameters = tuple(
            param.name.value for param in original_node.params.params
        )
        tab = self.config.tab_length * " "
        if doc := original_node.get_docstring():
            actual_parameters = dict(
                (
                    (partition := param.partition(":"))[0],
                    f"{tab}:param {partition[0]}:{partition[2]}",
                )
                for param in doc.rpartition(":return:")[0].split(":param ")[1:]
            )
        else:
            actual_parameters = {}
        missing_parameters = tuple(
            set(expected_parameters) - set(actual_parameters.keys())
        )
        if not missing_parameters:
            return updated_node
        code = cst.Module(body=[original_node]).code
        summary, parameters, result = generate_descriptions(
            code, missing_parameters, self.config
        )
        parameters, result = conv2docstring_lines(
            parameters, result, missing_parameters
        )
        line_splitter = partial(
            split_lines,
            line_length=self.config.line_length,
            tab_length=self.config.tab_length,
        )
        summary, parameters, result = (
            line_splitter(summary),
            tuple(map(line_splitter, parameters)),
            line_splitter(result),
        )
        parameters = dict(zip(missing_parameters, parameters))
        parameters.update(actual_parameters)
        result_doc = '"""{}{}{}"""'.format(
            "\n" + summary,
            "".join(map(parameters.get, expected_parameters)),
            result + tab,
        )
        return self._set_path_attrs(
            updated_node,
            ["body"],
            body=(
                SimpleStatementLine(
                    body=(
                        Expr(
                            value=SimpleString(
                                value=result_doc,
                            )
                        ),
                    )
                ),
                *self._get_path_attrs(updated_node, ["body", "body"])[
                    bool(doc) :
                ],
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
            key = attrs[-i]
            if isinstance(key, int):
                inner_element = outer_element[attrs[-i]]
            else:
                try:
                    inner_element = outer_element.with_changes(
                        **{attrs[-i]: inner_element}
                    )
                except TypeError:
                    traceback.format_exc()
        return inner_element
