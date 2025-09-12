import json
from logging import getLogger
from pathlib import Path

import click
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    RapidOcrOptions,
    VlmPipelineOptions,
)
from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat
from docling.document_converter import (
    ConversionResult,
    DocumentConverter,
    InputFormat,
    PdfFormatOption,
)
from docling.pipeline.vlm_pipeline import VlmPipeline
from modelscope import snapshot_download

from src.common.settings import settings

logger = getLogger("doclingtrials")


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument(
    "pdf",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
)
def test1(pdf: str) -> None:
    # Download RappidOCR models from HuggingFace
    logger.info("Downloading RapidOCR models.")
    model_cache_path = snapshot_download(repo_id="RapidAI/RapidOCR", cache_dir=settings.model_cache)
    model_cache = Path(model_cache_path)

    # Setup RapidOcrOptions for english detection
    det_model_path = model_cache / "onnx" / "PP-OCRv5" / "det" / "ch_PP-OCRv5_server_det.onnx"
    rec_model_path = model_cache / "onnx" / "PP-OCRv5" / "rec" / "ch_PP-OCRv5_rec_server_infer.onnx"
    cls_model_path = model_cache / "onnx" / "PP-OCRv4" / "cls" / "ch_ppocr_mobile_v2.0_cls_infer.onnx"
    ocr_options = RapidOcrOptions(
        det_model_path=str(det_model_path),
        rec_model_path=str(rec_model_path),
        cls_model_path=str(cls_model_path),
    )

    pipeline_options = PdfPipelineOptions(
        ocr_options=ocr_options,
    )

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            ),
        },
    )

    conversion_result: ConversionResult = converter.convert(source=pdf)
    doc = conversion_result.document
    doc_md = doc.export_to_markdown()
    print(doc_md)


def ollama_vlm_options(model: str, prompt: str) -> ApiVlmOptions:
    return ApiVlmOptions(
        url=f"{settings.ollama_api_url}/v1/chat/completions",
        params={"model": model},
        prompt=prompt,
        timeout=90,
        scale=1.0,
        response_format=ResponseFormat.MARKDOWN,
    )


@cli.command()
@click.argument(
    "pdf",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    required=True,
)
def test2(pdf: str) -> None:
    logger.info("Running VLM pipeline with Ollama backend.")
    pipeline_options = VlmPipelineOptions(
        enable_remote_services=True  # <-- this is required!
    )

    pipeline_options.vlm_options = ollama_vlm_options(
        model=settings.ollama_model,
        prompt="OCR the full page to markdown.",
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
                pipeline_cls=VlmPipeline,
            )
        }
    )

    result = doc_converter.convert(pdf)
    print(json.dumps(result.document.export_to_dict(), indent=2))
