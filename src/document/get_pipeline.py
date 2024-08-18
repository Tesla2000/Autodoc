from __future__ import annotations

from collections import namedtuple

from src.config import Config

wrapped_pipeline = None


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
    global wrapped_pipeline
    import torch
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

    if wrapped_pipeline:
        return wrapped_pipeline
    cuda = torch.cuda.is_available()
    if not cuda:
        print("No cuda, are you for real?")
    tokenizer = AutoTokenizer.from_pretrained(
        config.llm,
        cache_dir=config.hf_home,
        token=config.huggingface_token.get_secret_value(),
    )
    model = AutoModelForCausalLM.from_pretrained(
        config.llm,
        torch_dtype=torch.bfloat16,
        cache_dir=config.hf_home,
        token=config.huggingface_token.get_secret_value(),
    )

    device = 0 if cuda else -1
    wrapped_pipeline = PipelineWrapper(
        pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device=device,
        ),
        config,
    )
    return wrapped_pipeline
