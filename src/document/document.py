from __future__ import annotations

from src.config import Config


class DocstringGen:
    def __init__(self, config: Config):
        import torch

        self.model_id = config.llm
        self.fine_tuned_model_id = config.fine_tuned_llm
        self.max_new_tokens = config.max_new_tokens
        self.token = config.huggingface_token
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self._model = None

    def generate_text(self, code: str):
        import torch
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
        )

        torch.cuda.empty_cache()

        # Load model and tokenizer
        model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            token=self.token.get_secret_value(),
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
            ),
        )
        tokenizer = AutoTokenizer.from_pretrained(
            self.model_id, token=self.token.get_secret_value()
        )

        input_ids = tokenizer(code, return_tensors="pt").to(self.device)
        output_tokens = model.generate(
            **input_ids,
            max_new_tokens=self.max_new_tokens,
            pad_token_id=tokenizer.eos_token_id,
        )
        return tokenizer.decode(output_tokens[0], skip_special_tokens=False)

    @property
    def model(self):
        from transformers import AutoModelForCausalLM

        self._model = self._model or AutoModelForCausalLM.from_pretrained(
            self.model_id, token=self.token.get_secret_value()
        )
        return self._model

    def fine_tuned_generate_text(self, code: str):
        """
        Sample output on a fine-tuned model
        we should ignore everything that comes after any of FIM tokens or the
        EOS token
        """

        import torch
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            BitsAndBytesConfig,
        )
        from peft import PeftModel

        torch.cuda.empty_cache()

        FIM_PREFIX = "<|fim_prefix|>"
        FIM_SUFFIX = "<|fim_suffix|>"
        FIM_MIDDLE = "<|fim_middle|>"
        FIM_FILE_SEPARATOR = "<|file_separator|>"

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.tokenizer.padding_side = "right"  # to prevent warnings

        terminators = self.tokenizer.convert_tokens_to_ids(
            [FIM_PREFIX, FIM_MIDDLE, FIM_SUFFIX, FIM_FILE_SEPARATOR]
        )
        terminators += [self.tokenizer.eos_token_id]

        input_ids = self.tokenizer(code, return_tensors="pt").to(self.device)

        model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
            ),
        )
        fine_tuned_model = PeftModel.from_pretrained(
            model,
            self.fine_tuned_model_id,
            quantization_config=BitsAndBytesConfig(
                load_in_4bit=True, bnb_4bit_compute_dtype=torch.float16
            ),
        )
        output_tokens = fine_tuned_model.generate(
            **input_ids,
            eos_token_id=terminators,
            max_new_tokens=self.max_new_tokens,
        )

        return self.tokenizer.decode(
            output_tokens[0], skip_special_tokens=True
        )
