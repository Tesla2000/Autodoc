from __future__ import annotations

from typing import Sequence

from langchain.chat_models import init_chat_model
from pydantic.v1.error_wrappers import ValidationError

from src.config import Config
from src.document.get_pipeline import get_pipeline


def generate_documentation(
    code: str, parameters: Sequence[str], config: Config
) -> str:
    try:
        model = init_chat_model(config.llm, temperature=0.2)
    except ValidationError:
        raise
    except ValueError:
        model = get_pipeline(config)
    result = model.invoke(
        f"Write a short description of the function bellow.\nFunction:\n\n"
        f"{code.strip()}\n\nThe description should be up to 2 sentences long "
        f"with one sentence description being preferred."
    )
    print(result)
    summary = model.invoke(
        f"Write a short description of the function bellow.\nFunction:\n\n"
        f"{code.strip()}\n\nThe description should be up to 2 sentences long "
        f"with one sentence description being preferred."
    ).content
    return_value = model.invoke(
        f"Given the function below write a short description of "
        f"a return value.\nFunction:\n\n{code.strip()}\n\nThe description "
        f"should a few words long."
    ).content
    return (
        f"{summary}"
        + "".join(
            f"\n\t:param {parameter}: "
            + model.invoke(
                f"Given the function below write a short description of "
                f"parameter {parameter}.\nFunction:\n\n{code.strip()}\n\nThe "
                f"description should be up to one sentence long."
            ).content
            for parameter in parameters
        )
        + f"\n\t:return: {return_value}"
    )
