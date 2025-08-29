from logging import getLogger
from pathlib import Path

import click
from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
from docling.document_converter import (
    ConversionResult,
    DocumentConverter,
    InputFormat,
    PdfFormatOption,
)
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
