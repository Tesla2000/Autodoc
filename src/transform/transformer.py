from __future__ import annotations

import traceback
from typing import Sequence

import libcst as cst
from libcst import Module

from src.config import Config


class Transformer(cst.CSTTransformer):

    def __init__(self, module: Module, config: Config):
        super().__init__()
        self.config = config
        self.module = module

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
