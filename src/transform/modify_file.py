from __future__ import annotations

import libcst as cst

from src.config import Config
from src.transform.transformer import Transformer


def modify_file(code: str, config: Config) -> str:
    module = cst.parse_module(code)
    transformer = Transformer(module, config)
    return module.visit(transformer).code
