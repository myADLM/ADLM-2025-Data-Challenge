import difflib

import pandas as pd
from django.core.management.base import BaseCommand

from api.models import Document

def diff_metrics(a: str, b: str):
    sm = difflib.SequenceMatcher(None, a, b)
    opcodes = sm.get_opcodes()

    # Track insertions, deletions, replacements
    insertions = deletions = replacements = 0

    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'insert':
            insertions += (j2 - j1)
        elif tag == 'delete':
            deletions += (i2 - i1)
        elif tag == 'replace':
            # count both sides for how many chars differ
            replacements += max(i2 - i1, j2 - j1)

    total_diff = insertions + deletions + replacements
    total_chars = max(len(a), len(b))
    relative_diff = total_diff / total_chars if total_chars else 0

    insertion_ratio = insertions / total_chars if total_chars else 0
    deletion_ratio = deletions / total_chars if total_chars else 0
    replacement_ratio = replacements / total_chars if total_chars else 0
    total_diff_chars_ratio = total_diff / total_chars if total_chars else 0

    return {
        'insertions': insertions,
        'deletions': deletions,
        'replacements': replacements,
        'total_diff_chars': total_diff,
        'relative_diff': relative_diff,
        'insertion_ratio': insertion_ratio,
        'deletion_ratio': deletion_ratio,
        'replacement_ratio': replacement_ratio,
        'total_diff_chars_ratio': total_diff_chars_ratio,
    }

class Command(BaseCommand):
    help = "Analyze markdown diffs"

    def handle(self, *args, **options):
        print("Analyzing markdown diffs")

        documents = Document.objects.all()
        documents = documents[:100]

        all_diffs = []

        for document in documents:
            for (name_a, a), (name_b, b) in [
                (('marker', document.marker_markdown_plain), ('nougat', document.nougat_markdown)),
                (('marker', document.marker_markdown_plain), ('mineru', document.mineru_markdown)),
                (('nougat', document.nougat_markdown), ('mineru', document.mineru_markdown)),
            ]:
                metrics = diff_metrics(a, b)
                #print(f"{name_a} vs {name_b}: {metrics}")
                metrics['relative_path'] = document.relative_path
                metrics['name_a'] = name_a
                metrics['name_b'] = name_b
                all_diffs.append(metrics)

                metrics = diff_metrics(b, a)
                metrics['relative_path'] = document.relative_path
                metrics['name_a'] = name_b
                metrics['name_b'] = name_a
                all_diffs.append(metrics)

        df = pd.DataFrame(all_diffs)
        df.to_csv('markdown_diffs.csv', index=False)

        print(df)

        agg_df = df.groupby(['name_a', 'name_b']).agg({
            'insertions': 'sum',
            'deletions': 'sum',
            'replacements': 'sum',
            'total_diff_chars': 'sum',
            'relative_diff': 'mean'
        }).reset_index()

        print(agg_df)

        print("Done")