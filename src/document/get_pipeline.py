from __future__ import annotations

from typing import TYPE_CHECKING

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
            model, config.fine_tuned_llm, token=config.hugginhface_token
        )
    return SummarizationPipeline(
        tokenizer=tokenizer,
        model=model,
        device=0,
    )
