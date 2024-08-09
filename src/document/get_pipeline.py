from __future__ import annotations

from collections import namedtuple

from src.config import Config


class PipelineWrapper:
    def __init__(self, pipeline, config: Config):
        self.config = config
        self.pipeline = pipeline

    def invoke(self, messages):
        return namedtuple("result", ["content"])(
            self.pipeline(messages, max_new_tokens=self.config.max_new_tokens)[
                0
            ]["generated_text"][-1]["content"].strip()
        )


def get_pipeline(config: Config) -> PipelineWrapper:
    import torch
    from transformers import pipeline

    return PipelineWrapper(
        pipeline(
            "text-generation",
            model=config.llm,
            model_kwargs={"torch_dtype": torch.bfloat16},
            device="cuda",
        ),
        config,
    )
