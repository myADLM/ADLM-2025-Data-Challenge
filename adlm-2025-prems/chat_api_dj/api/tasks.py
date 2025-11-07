
from django_tasks import task


@task()
def populate_entities() -> None:
    print('Populating entities')
    from api.management.commands.populate_entity import Command
    command = Command()
    command.handle()

@task()
def populate_embeddings() -> None:
    print('Populating embeddings')
    from api.management.commands.populate_embeddings import Command
    command = Command()
    command.handle()


@task()
def spacy_ner_extraction() -> None:
    print('Spacy NER Extraction')
    from api.management.commands.spacy_ner_extraction import Command
    command = Command()
    command.handle()

@task()
def load_mineru_content() -> None:
    print('Loading mineru content')
    from api.management.commands.load_mineru_content import Command
    command = Command()
    command.handle()