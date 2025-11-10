import os
import time
import base64
import argparse
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader

MODEL_NAME = 'gemini-2.5-flash'
RATE_LIMIT_DELAY_SECONDS = 50
TEMPERATURE = 0.0
TOP_P = 1.0
TOP_K = 40
MAX_OUTPUT_TOKENS = 8192

def load_prompt_template(template_name="regulatory_lab_parser"):
    prompts_dir = Path(__file__).parent.parent / "prompts"
    env = Environment(loader=FileSystemLoader(str(prompts_dir)))
    return env.get_template(f"{template_name}.j2")

def pdf_to_base64(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def process_pdf(model, pdf_path, output_path, prompt_template):
    filename = os.path.basename(pdf_path)
    print(f"\nProcessing: {filename}")
    
    base64_pdf = pdf_to_base64(pdf_path)
    prompt_text = prompt_template.render()
    
    generation_config = genai.types.GenerationConfig(
        temperature=TEMPERATURE,
        top_p=TOP_P,
        top_k=TOP_K,
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )
    
    response = model.generate_content(
        [prompt_text, {"mime_type": "application/pdf", "data": base64_pdf}],
        generation_config=generation_config
    )
    
    response_text = response.text
    
    metadata_header = f"""<!--
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source PDF: {filename}
Model: {MODEL_NAME}
-->

"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(metadata_header + response_text)
    
    print(f"Saved: {output_path}")

def process_directory(input_dir, output_dir, model, prompt_template, max_docs=None):
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    pdf_files.sort()
    
    print(f"Found {len(pdf_files)} PDF(s)")
    
    os.makedirs(output_dir, exist_ok=True)
    
    unprocessed = []
    for f in pdf_files:
        md_file = os.path.splitext(f)[0] + ".md"
        if not os.path.exists(os.path.join(output_dir, md_file)):
            unprocessed.append(f)
    
    print(f"Unprocessed: {len(unprocessed)} PDF(s)")
    
    if max_docs and max_docs > 0:
        files_to_process = unprocessed[:max_docs]
    else:
        files_to_process = unprocessed
    
    if not files_to_process:
        print("No files to process.")
        return
    
    print(f"Processing {len(files_to_process)} file(s)...\n")
    
    success_count = 0
    for filename in files_to_process:
        pdf_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".md")
        
        try:
            process_pdf(model, pdf_path, output_path, prompt_template)
            success_count += 1
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            if "429" in str(e) or "quota" in str(e).lower():
                print("Rate limit exceeded. Exiting.")
                break
        
        if RATE_LIMIT_DELAY_SECONDS > 0:
            time.sleep(RATE_LIMIT_DELAY_SECONDS)
    
    print(f"\nCompleted: {success_count}/{len(files_to_process)} files processed")

def main():
    parser = argparse.ArgumentParser(description="Parses PDF documents to structured Markdown.")
    parser.add_argument("--input-folder", required=True, help="Path to folder containing PDF files")
    parser.add_argument("--output-folder", required=True, help="Path to folder where Markdown files will be saved")
    parser.add_argument("--api-key", help="Google AI Studio API key (or set GOOGLE_API_KEY env var)")
    parser.add_argument("--prompt-template", default="regulatory_lab_parser", help="Prompt template name")
    parser.add_argument("--max-docs", type=int, default=0, help="Maximum documents to process (0 = unlimited)")
    args = parser.parse_args()

    api_key = args.api_key or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: API Key not found. Provide --api-key or set GOOGLE_API_KEY environment variable.")
        return

    try:
        prompt_template = load_prompt_template(args.prompt_template)
    except Exception as e:
        print(f"ERROR: Failed to load prompt template: {e}")
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_NAME)
    except Exception as e:
        print(f"ERROR: Failed to configure API: {e}")
        return

    process_directory(args.input_folder, args.output_folder, model, prompt_template, args.max_docs)

if __name__ == "__main__":
    main()
