import time
from datetime import datetime

from django.core.management.base import BaseCommand
import schedule

from api.tasks import populate_entities, populate_embeddings, spacy_ner_extraction, load_mineru_content

def print_time():
    print('')
    now = datetime.now()
    timestr = now.strftime("%Y-%m-%d %H:%M:%S")
    print(timestr, end=' ', flush=True)

class Command(BaseCommand):
    help = "Scheduler for tasks"

    def handle(self, *args, **options):
        print("Scheduler for tasks")

        schedule.every(1).minutes.do(populate_entities.enqueue)
        schedule.every(1).minutes.do(load_mineru_content.enqueue)
        # Want to enable, but we've got 2mil + to run through, maybe train a better one to start
        # lean onto only using one set or the other for chunk, maybe merge a bunch of them
        #schedule.every(1).minutes.do(spacy_ner_extraction.enqueue)
        schedule.every(1).minutes.do(populate_embeddings.enqueue)
        #schedule.every().hour.do(populate_embeddings.enqueue)
        #schedule.every().day.at("10:30").do(spacy_ner_extraction.enqueue)

        i = 0
        while True:
            if i % 120 == 0:
                print_time()
                i = 0
            else:
                print('.', end='', flush=True)
            schedule.run_pending()
            time.sleep(1)
            i += 1

            