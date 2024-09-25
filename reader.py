import torch
import sys
from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

if __name__ == "__main__":
    device = "cpu"

    model = ParlerTTSForConditionalGeneration.from_pretrained("parler-tts/parler-tts-mini-v1").to(device)
    tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-mini-v1")

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        print("Please provide a prompt as a command-line argument.")
        sys.exit(1)

    description = "Jon's voice is monotone regular speed in delivery, with a very close recording that has no background noise. With UK accent."

    input_ids = tokenizer(description, return_tensors="pt").input_ids.to(device)
    prompt_input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

    generation = model.generate(input_ids=input_ids, prompt_input_ids=prompt_input_ids)
    audio_arr = generation.cpu().numpy().squeeze()
    sf.write("parler_tts_out.wav", audio_arr, model.config.sampling_rate)
