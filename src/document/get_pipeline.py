from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from src.config import Config

if TYPE_CHECKING:
    from transformers import SummarizationPipeline


def get_pipeline(config: Config) -> "SummarizationPipeline":
    from peft import PeftModel
    from transformers import GemmaTokenizer, AutoModelForCausalLM
    from transformers import SummarizationPipeline

    tokenizer = GemmaTokenizer.from_pretrained(
        config.llm, token=config.huggingface_token.get_secret_value()
    )
    model = AutoModelForCausalLM.from_pretrained(
        config.llm, token=config.huggingface_token
    )
    if config.fine_tuned_llm:
        model = PeftModel.from_pretrained(
            model, config.fine_tuned_llm, token=config.huggingface_token
        )

    class CustomPipeline(SummarizationPipeline):
        def invoke(self, *args, **kwargs):
            with torch.no_grad():
                return self()

    return CustomPipeline(
        tokenizer=tokenizer,
        model=model,
        device="cuda",
        max_new_tokens=100,
    )
