from __future__ import annotations

from collections import defaultdict

from libcst import ClassDef
from libcst import Expr
from libcst import FunctionDef
from libcst import IndentedBlock
from libcst import Module
from libcst import SimpleStatementLine
from libcst import SimpleString

from src.config import Config
from src.document.docstring_generator import DocstringGenerator
from src.transform.transformer import Transformer


class DocTransformer(Transformer):
    def __init__(self, module: Module, config: Config):
        super().__init__(module, config)
        self.indentation_levels = defaultdict(lambda: 1)

    def leave_FunctionDef(
        self, original_node: "FunctionDef", updated_node: "FunctionDef"
    ) -> "FunctionDef":
        indentation_level = self.indentation_levels[original_node]
        generator = DocstringGenerator(original_node, self.config)
        if not generator.is_valid(indentation_level):
            return original_node
        result_doc = generator.generate()
        expr = Expr(value=SimpleString(value=result_doc))
        statement_line = SimpleStatementLine(body=(expr,))
        path_attrs = self._get_path_attrs(updated_node, ["body", "body"])
        path_attrs = path_attrs[bool(generator.doc) :]
        body = (statement_line, *path_attrs)
        return self._set_path_attrs(updated_node, ["body"], body=body)

    def visit_IndentedBlock_body(self, node: "IndentedBlock") -> None:
        for child in node.body:
            if not isinstance(child, (IndentedBlock, ClassDef, FunctionDef)):
                continue
            self.indentation_levels[child] = self.indentation_levels[node] + 1
        super().visit_IndentedBlock_body(node)
