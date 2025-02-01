import warnings
import os
import shutil
import time

warnings.filterwarnings("ignore")
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import numpy as np
import random
import os
import argparse
import torch

from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import is_bfloat16_supported

from model import DeepSeek_FT_Models
from dataset import FT_Dataset
from utils import Logger
from unsloth import FastLanguageModel

from tqdm import tqdm


class Eval:
    def __init__(self, task, model_name="Q1.5B", prompt_lang="ar", models_dir="./models", logs_dir="./logs"):
        self.task = task
        self.model_name = model_name
        self.prompt_lang = prompt_lang

        self.read_congifs()
        self.load_model()
        self.load_data()

        if not os.path.exists("./preds"):
            os.mkdir("./preds")

        self.preds_file_path = os.path.join("./preds", "_".join([self.model_name, self.task, self.prompt_lang]))
        if os.path.exists(self.preds_file_path):
            shutil.rmtree(self.preds_file_path)

        os.mkdir(self.preds_file_path)

    def generate_predictions(self):
        for i, prompt in enumerate(self.dataset["text"]):
            inputs = self.tokenizer([prompt], return_tensors="pt").to("cuda")
            outputs = self.model.generate(
                input_ids=inputs.input_ids,
                attention_mask=inputs.attention_mask,
                max_new_tokens=1200,
                use_cache=True,
            )
            response = self.tokenizer.batch_decode(outputs)

            logger = Logger(os.path.join(self.preds_file_path, f"{i}.txt"))
            logger(response[0].replace(self.tokenizer.eos_token, ""))

            if i == 10: break

    def load_data(self):
        self.dataset_helper = FT_Dataset(self.tokenizer.eos_token, split="test", test_mode=True)
        self.dataset = self.dataset_helper.get_dataset(self.task, self.CONFIGS["PROMPT_LANG"])
        self.dataset_size = self.dataset_helper.get_size()


    def read_congifs(self):
        CONFIGS = {
            "PROMPT_LANG": "",
            "LOAD_4BIT": -1,
            "MAX_SEQ_LENGTH": -1,
        }

        file_name = "_".join([self.model_name, self.task, self.prompt_lang])+".txt"
        file_path = os.path.join("./logs", file_name)

        with open(file_path) as log_file:
            configs = log_file.readlines()

        count = len(CONFIGS.keys())
        for c in configs:
            if c.split(":")[0] in CONFIGS.keys():
                c = c.replace("\n", "")
                try:
                    CONFIGS[c.split(":")[0]] = int(c.split(":")[1].strip())
                except:
                    CONFIGS[c.split(":")[0]] = c.split(":")[1].strip()
                count -= 1

            if count == 0:
                break

        self.CONFIGS = CONFIGS

    def load_model(self):
        file_name = "_".join([self.model_name, self.task, self.prompt_lang])
        model_path = os.path.join("./models", file_name)

        base_model_path = os.path.join(model_path, "base_model")
        lora_adapter_path = os.path.join(model_path, "lora_adapter")

        config_files = {
            "config.json": base_model_path,
            "adapter_config.json": lora_adapter_path,
            "model.safetensors": base_model_path,
            "adapter_model.safetensors": lora_adapter_path
        }

        # HAVE TO DO SOME REPO MANAGEMENT
        if not os.path.exists(base_model_path):
            os.makedirs(base_model_path)
            os.makedirs(lora_adapter_path)

            # SEPARATE BASE MODEL AND ADAPTER FILES
            for file_name, target_dir in config_files.items():
                source_path = os.path.join(model_path, file_name)
                if os.path.exists(source_path):
                    shutil.move(source_path, os.path.join(target_dir, file_name))

            # COPY COMMON FILES TO BOTH DIRS
            generation_config_source = os.path.join(model_path, "generation_config.json")
            shutil.copy(generation_config_source, os.path.join(base_model_path, "generation_config.json"))
            shutil.copy(generation_config_source, os.path.join(lora_adapter_path, "generation_config.json"))

            generation_config_source = os.path.join(model_path, "special_tokens_map.json")
            shutil.copy(generation_config_source, os.path.join(base_model_path, "special_tokens_map.json"))
            shutil.copy(generation_config_source, os.path.join(lora_adapter_path, "special_tokens_map.json"))

            generation_config_source = os.path.join(model_path, "tokenizer_config.json")
            shutil.copy(generation_config_source, os.path.join(base_model_path, "tokenizer_config.json"))
            shutil.copy(generation_config_source, os.path.join(lora_adapter_path, "tokenizer_config.json"))

            generation_config_source = os.path.join(model_path, "tokenizer.json")
            shutil.copy(generation_config_source, os.path.join(base_model_path, "tokenizer.json"))
            shutil.copy(generation_config_source, os.path.join(lora_adapter_path, "tokenizer.json"))

        base_model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=base_model_path,
            max_seq_length=self.CONFIGS["MAX_SEQ_LENGTH"],
            load_in_4bit=self.CONFIGS["LOAD_4BIT"] == 1,
        )

        # base_model.load_adapter(lora_adapter_path)
        FastLanguageModel.for_inference(base_model)

        self.tokenizer = tokenizer
        self.model = base_model

        
if __name__ == "__main__":
    e = Eval("sentiment")
    e.generate_predictions()

    e = Eval("pos_tagging")
    e.generate_predictions()

    e = Eval("paraphrasing")
    e.generate_predictions()

    e = Eval("summarization")
    e.generate_predictions()

    e = Eval("transliteration")
    e.generate_predictions()

    e = Eval("diacratization")
    e.generate_predictions()