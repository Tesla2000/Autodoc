from __future__ import annotations

import time
from typing import Sequence

from langchain.chat_models import init_chat_model
from pydantic.v1.error_wrappers import ValidationError

from src.config import Config
from src.document.get_pipeline import get_pipeline


def generate_descriptions(
    code: str, parameters: Sequence[str], config: Config
) -> tuple[str, tuple[str, ...], str]:
    try:
        model = init_chat_model(config.llm, temperature=0.2)
    except ValidationError:
        raise
    except ValueError:
        model = get_pipeline(config)
    start = time.time()
    summary = model.invoke(
        _to_chat(config.summary_prompt.format(code=code.strip()))
    ).content
    return_value = model.invoke(
        _to_chat(config.return_value_prompt.format(code=code.strip()))
    ).content.lstrip()
    # result = (
    #     f"{summary}"
    #     + "".join(
    #         f"\n    :param {parameter}: "
    #         +
    #     )
    #     + f"\n    :return: {return_value}"
    # )

    print(time.time() - start)
    return (
        summary,
        tuple(
            model.invoke(
                _to_chat(
                    config.parameter_prompt.format(
                        parameter=parameter, code=code.strip()
                    )
                )
            ).content.lstrip()
            for parameter in parameters
        ),
        return_value,
    )


def _to_chat(content: str) -> list[dict[str, str]]:
    return [{"role": "user", "content": content}]
