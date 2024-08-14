from __future__ import annotations

import libcst as cst

from src.config import Config
from src.transform.doc_transformer import DocTransformer


def modify_code(code: str, config: Config) -> str:
    module = cst.parse_module(code)
    transformer = DocTransformer(module, config)
    return module.visit(transformer).code
