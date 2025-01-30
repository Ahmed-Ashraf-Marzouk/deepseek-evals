# DeepSeek Evals

This repository is designed to finetune and evaluate the DeepSeek distilled models on Arabic NLP tasks.

<img src="/fig/ds.png">

## Requirements
```
pip install torch torchvision
pip install unsloth
pip install conllu
pip install datasets
pip install tqdm
pip install transformers
```


## Fine-tuning
To fine-tune the distilled models on the Arabic NLP tasks, you can use the following command:
```
python finetune.py --model Q1.5B --task sentiment --prompt_lang ar --rank 4 --load_4bit 0 --max_seq_length 2048 --batch_size 2 --gradient_accumulation_steps 2 --epochs 1
```

- <b>model</b>
-- options: ['L8B', 'L70B', 'Q1.5B', 'Q7B', 'Q14B', 'Q32B']
-- description: The model to be fine-tuned.

- <b>task</b>
-- options: ['sentiment', 'diacratization', 'mcq', 'pos_tagging', 'summarization', 'translation', 'transliteration']

- <b>prompt_lang</b>
-- options: ['ar', 'en']
-- description: The language of the prompt.

- <b>rank</b>
-- options: ['4', '8', '16']
-- description: The rank of LoRA decomposition.

- <b>load_4bit</b>
-- options: ['0', '1']
-- description: Whether to load the 4-bit model or not.

- <b>max_seq_length</b>
-- options: [512, 1024, 2048]
-- description: The maximum sequence length.

- <b>batch_size</b>
-- options: [2, 4, 8, 16, 32]
-- description: The batch size.

- <b>gradient_accumulation_steps</b>
-- options: [1, 2, 4, 8]
-- description: The number of gradient accumulation steps.

- <b>epochs</b>
-- description: The number of epochs.

## Evaluation