import click
from docling.document_converter import DocumentConverter


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
    converter = DocumentConverter()
    doc = converter.convert(pdf).document

    click.echo(doc.export_to_markdown())
