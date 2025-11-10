import os
import time
import base64
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader, select_autoescape
from tqdm import tqdm
from openai import OpenAI


@dataclass
class Config:
    """Configuration for PDF parser."""
    model: str = "google/gemini-2.5-flash"
    rate_limit_delay: int = 50
    temperature: float = 0.0
    top_p: float = 1.0
    max_output_tokens: int = 8192
    pdf_engine: str = "native"
    api_key: Optional[str] = None
    prompt_template: str = "regulatory_lab_parser"


def load_prompt_template(template_name="regulatory_lab_parser"):
    prompts_dir = Path(__file__).parent.parent / "prompts"
    env = Environment(
        loader=FileSystemLoader(str(prompts_dir)),
        autoescape=select_autoescape()
    )
    return env.get_template(f"{template_name}.j2")


def load_metadata_template():
    """Load the metadata header template."""
    prompts_dir = Path(__file__).parent.parent / "prompts"
    env = Environment(
        loader=FileSystemLoader(str(prompts_dir)),
        autoescape=select_autoescape()
    )
    return env.get_template("metadata_header.j2")


def get_api_key(api_key: Optional[str] = None) -> Optional[str]:
    """Get API key from parameter or environment variable."""
    return api_key or os.getenv("OPENROUTER_API_KEY")


def pdf_to_base64(filepath: str) -> Optional[str]:
    """Convert PDF file to base64 encoded string."""
    try:
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        tqdm.write(f"Error: File not found: {filepath}")
        return None


def create_client(api_key: str):
    """Create OpenRouter client."""
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )


def create_metadata_header(metadata_template, filename: str, config: Config) -> str:
    """Create metadata header using Jinja2 template."""
    parameters = {
        "temperature": config.temperature,
        "top_p": config.top_p,
    }
    
    context = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "model": config.model,
        "provider_name": "OpenRouter",
        "provider_url": "https://openrouter.ai",
        "pdf_engine": config.pdf_engine,
        "parameters": parameters,
    }
    
    return metadata_template.render(**context) + "\n"


def process_pdf(client, pdf_path: str, output_path: str, prompt_text: str, 
                config: Config, metadata_template) -> bool:
    """Process PDF using OpenRouter API."""
    filename = os.path.basename(pdf_path)
    base64_pdf = pdf_to_base64(pdf_path)
    if not base64_pdf:
        return False
    
    pdf_size_kb = len(base64_pdf) * 3 / 4 / 1024
    tqdm.write(f"PDF size: {pdf_size_kb:.1f} KB")
    tqdm.write(f"PDF engine: {config.pdf_engine}")
    
    try:
        data_url = f"data:application/pdf;base64,{base64_pdf}"
        
        extra_body = {}
        if config.pdf_engine != "native":
            extra_body["plugins"] = [
                {
                    "id": "file-parser",
                    "pdf": {"engine": config.pdf_engine}
                }
            ]
        
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {
                            "type": "file",
                            "file": {
                                "filename": filename,
                                "file_data": data_url
                            }
                        }
                    ]
                }
            ],
            temperature=config.temperature,
            top_p=config.top_p,
            timeout=1200,
            **extra_body
        )
        
        response_text = response.choices[0].message.content
        if not response_text:
            tqdm.write("WARNING: Empty response received")
            return False
        
        metadata_header = create_metadata_header(metadata_template, filename, config)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(metadata_header + response_text)
        
        lines = response_text.count("\n") + 1
        tqdm.write(f"✓ Success: {lines} lines, {len(response_text)} chars")
        tqdm.write(f"  Output: {output_path}")
        return True
        
    except Exception as e:
        tqdm.write(f"✗ ERROR: {type(e).__name__}")
        tqdm.write(f"  {str(e)[:200]}")
        if "429" in str(e):
            tqdm.write("\nFATAL: Rate limit exceeded. Exiting.")
            raise
        return False


def process_directory(input_dir: str, output_dir: str, client, prompt_template,
                     config: Config, metadata_template, max_docs: Optional[int] = None):
    """Process all PDF files in input directory."""
    if not os.path.exists(input_dir):
        print(f"ERROR: Input directory not found: {input_dir}")
        return
    
    pdf_files = sorted([f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")])
    
    if not pdf_files:
        print("No PDF files found.")
        return
    
    print(f"\nFound {len(pdf_files)} PDF(s)")
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    unprocessed = [
        f for f in pdf_files
        if not os.path.exists(os.path.join(output_dir, os.path.splitext(f)[0] + ".md"))
    ]
    
    print(f"Unprocessed: {len(unprocessed)} PDF(s)")
    
    files_to_process = unprocessed[:max_docs] if max_docs and max_docs > 0 else unprocessed
    
    if not files_to_process:
        print("No files to process.")
        return
    
    print(f"\nProcessing {len(files_to_process)} file(s)...\n")
    
    success_count = 0
    for filename in tqdm(files_to_process, desc="Progress"):
        pdf_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".md")
        
        try:
            prompt_text = prompt_template.render()
            if process_pdf(client, pdf_path, output_path, prompt_text, config, metadata_template):
                success_count += 1
        except Exception:
            break
        
        if config.rate_limit_delay > 0:
            time.sleep(config.rate_limit_delay)
    
    print(f"Completed: {success_count}/{len(files_to_process)} files processed successfully")


def main():
    parser = argparse.ArgumentParser(
        description="Parses PDF documents to structured Markdown using OpenRouter.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--input-folder",
        required=True,
        help="Path to folder containing PDF files to process."
    )
    parser.add_argument(
        "--output-folder",
        required=True,
        help="Path to folder where Markdown files will be saved."
    )
    parser.add_argument(
        "--model",
        default=Config.model,
        help=f"Model name (default: {Config.model}). Examples: google/gemini-2.5-flash, z-ai/glm-4.5-air:free"
    )
    parser.add_argument(
        "--api-key",
        help="OpenRouter API key (or set OPENROUTER_API_KEY env var)"
    )
    parser.add_argument(
        "--prompt-template",
        default=Config.prompt_template,
        help=f"Prompt template name (without .j2 extension, default: {Config.prompt_template})"
    )
    parser.add_argument(
        "--max-docs",
        type=int,
        default=0,
        help="Maximum documents to process (0 = unlimited)"
    )
    parser.add_argument(
        "--pdf-engine",
        choices=["native", "pdf-text", "mistral-ocr"],
        default=Config.pdf_engine,
        help=f"PDF processing engine (default: {Config.pdf_engine})"
    )
    parser.add_argument(
        "--rate-limit-delay",
        type=int,
        default=Config.rate_limit_delay,
        help=f"Delay between requests in seconds (default: {Config.rate_limit_delay})"
    )
    
    args = parser.parse_args()
    
    config = Config(
        model=args.model,
        rate_limit_delay=args.rate_limit_delay,
        pdf_engine=args.pdf_engine,
        api_key=get_api_key(args.api_key),
        prompt_template=args.prompt_template
    )
    
    if not config.api_key:
        print("ERROR: API Key not found. Provide --api-key or set OPENROUTER_API_KEY environment variable.")
        return
    
    try:
        prompt_template = load_prompt_template(config.prompt_template)
    except Exception as e:
        print(f"ERROR: Failed to load prompt template '{config.prompt_template}': {e}")
        return
    
    try:
        metadata_template = load_metadata_template()
    except Exception as e:
        print(f"ERROR: Failed to load metadata template: {e}")
        return
    
    try:
        client = create_client(config.api_key)
        print(f"✓ Provider: OpenRouter")
        print(f"✓ Model: {config.model}")
        print(f"✓ Prompt template: {config.prompt_template}")
        print(f"✓ PDF Engine: {config.pdf_engine}")
    except Exception as e:
        print(f"ERROR: Failed to configure API: {e}")
        return
    
    process_directory(
        args.input_folder,
        args.output_folder,
        client,
        prompt_template,
        config,
        metadata_template,
        args.max_docs
    )


if __name__ == "__main__":
    main()
