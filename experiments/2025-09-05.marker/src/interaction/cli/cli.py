from logging import getLogger

import click
from marker.config.parser import ConfigParser
from marker.converters.extraction import ExtractionConverter
from marker.models import create_model_dict
from pydantic import BaseModel

logger = getLogger("markerexperiments")


class Links(BaseModel):
    links: list[str]


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
    schema = Links.model_json_schema()
    config_parser = ConfigParser({"page_schema": schema})

    converter = ExtractionConverter(
        artifact_dict=create_model_dict(),
        config=config_parser.generate_config_dict(),
        llm_service=config_parser.get_llm_service(),
    )
    rendered = converter(pdf)
