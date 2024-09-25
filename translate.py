import os
import deepl
import re

if __name__ == "__main__":
    # Read the DeepL API key from an environment variable
    api_key = os.getenv('DEEPL_API_KEY')

    if not api_key:
        raise ValueError("DeepL API key not found. Please set the DEEPL_API_KEY environment variable.")

    # Initialize the DeepL translator
    translator = deepl.Translator(api_key)

    def translate_file(input_file, output_file):
        with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
            for line in infile:
                # Extract timestamp and text
                match = re.match(r'(\[.+?\])\s*(.+)', line.strip())
                if match:
                    timestamp, text = match.groups()
                    
                    # Translate the text
                    result = translator.translate_text(text, target_lang="EN-US")
                    
                    # Write the translated line to the output file
                    outfile.write(f"{timestamp} {result.text}\n")
                else:
                    # If the line doesn't match the expected format, write it as is
                    outfile.write(line)

    # Usage
    input_file = 'transcribe.txt'  # Replace with your input file name
    output_file = 'translated.txt'  # Replace with your desired output file name

    translate_file(input_file, output_file)
    print("Translation complete. Check the output file.")
