from __future__ import annotations

import os
from pathlib import Path
from typing import Type

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic import SecretStr

from src.custom_argument_parser import CustomArgumentParser

load_dotenv()


class Config(BaseModel):
    _root: Path = Path(__file__).parent
    code: str
    tab_length: int = 4
    line_length: int = 79
    # llm: str = "google/gemma-2b"
    llm: str = "google/gemma-2-2b-it"
    # llm: str = "gpt-4o-mini"
    # fine_tuned_llm: str = "documint/CodeGemma2B-fine-tuned"
    fine_tuned_llm: str = ""
    huggingface_token: SecretStr = os.getenv("HUGGINGFACE_API_TOKEN")
    max_new_tokens: int = 100
    summary_prompt: str = (
        "Write a short description of the function bellow.\nFunction:\n\n"
        "{code}\n\nThe description should be up to 2 sentences long "
        "with one sentence description being preferred."
    )
    return_value_prompt: str = (
        "Given the function below write a short description of"
        " a return value.\nFunction:\n\n{code}\n\nThe description "
        "should a few words long. Assume that your completion starts from "
        ":return: so don't include it."
    )
    parameter_prompt: str = (
        "Given the function below write a short "
        "description of parameter {parameter}.\nFunction:\n\n{code}\n\nThe "
        "description should be up to one sentence long. Assume that "
        "your completions starts from :param {parameter}: so don't "
        "include it."
    )
    update_overwrite: bool = True


def parse_arguments(config_class: Type[Config]):
    parser = CustomArgumentParser(
        description="Configure the application settings."
    )

    for name, value in config_class.model_fields.items():
        if name.startswith("_"):
            continue
        parser.add_argument(
            f"--{name}",
            type=value.annotation,
            default=value.default,
            help=f"Default: {value}",
        )

    return parser.parse_args()


def create_config_with_args(config_class: Type[Config], args) -> Config:
    config = config_class(
        **{name: getattr(args, name) for name in config_class.model_fields}
    )
    for variable in config.model_fields:
        value = getattr(config, variable)
        if (
            isinstance(value, Path)
            and value.suffix == ""
            and not value.exists()
        ):
            value.mkdir(parents=True)
    return config
