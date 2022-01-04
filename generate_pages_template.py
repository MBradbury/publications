#!/usr/bin/env python3
# Based on: https://github.com/StreakyCobra/plugins/blob/master/v7/publication_list/publication_list.py

import os.path
import re
import pathlib
import time

from markdownify import markdownify as md

from pybtex.plugin import find_plugin
from pybtex.database import parse_file
from pybtex.database import BibliographyData

style = find_plugin('pybtex.style.formatting', 'plain')()

with open('self.bib') as bibtex_file:
    db = parse_file(bibtex_file, 'bibtex')

sections = {
    "Publications": {"inproceedings", "article"},
    "PhD Thesis": {"phdthesis"},
    "Technical Reports": {"techreport"},
}

data = list(sorted(db.entries.items(), key=lambda e: e[1].fields["year"], reverse=True))

pages = pathlib.Path("pages")
pages.mkdir(parents=True, exist_ok=True)

bibtex_dir = "bibtex"
highlight_author = "Matthew Bradbury"
root_dir = "https://raw.githubusercontent.com/MBradbury/publications/master"

for section_name, section_types in sections.items():

    for label, entry in data:
        # Skip entries that we should not print
        if entry.type not in section_types:
            continue

        sanitised_label = label.replace(":", "_")

        this_paper = pages / (sanitised_label + ".md")

        print(this_paper)

        pub_html = list(style.format_entries([entry]))[0].text.render_as("html")
        pub_html = pub_html.replace("\n", " ")
        if highlight_author:  # highlight an author (usually oneself)
            pub_html = pub_html.replace(highlight_author, "<strong>{}</strong>".format(highlight_author), 1)

        pub_md = md(pub_html, heading_style="ATX")

        with open(this_paper, "w") as this_paper_file:
            print("---", file=this_paper_file)
            print(f"title: \"{entry.fields['title'].replace('{', '').replace('}', '')}\"", file=this_paper_file)
            print(f"citation: \"{pub_md}\"", file=this_paper_file)

            print(entry.fields.get('month', ''))
            month = entry.fields.get('month', 'January')

            # Need to strip dates out of month
            if '--' in month:
                month = month.split(' ', 1)[1]

            month = str(time.strptime(month, '%B').tm_mon).zfill(2)
            print(f"publishDate: \"{entry.fields['year']}-{month}\"", file=this_paper_file)

            if "file" in entry.fields:  # the link to the pdf file
                (a, filename, kind) = entry.fields["file"].split(":", 2)

                print(f"file: {root_dir}/papers/{filename}", file=this_paper_file)

                presentation_path = os.path.join("presentations", filename)
                if os.path.exists(presentation_path):
                    print(f"presentation: {root_dir}/presentations/{filename}", file=this_paper_file)

            print(f"bibtex: {root_dir}/{bibtex_dir}/{sanitised_label}.bib", file=this_paper_file)
            
            if "dataset" in entry.fields:
                print(f"dataset: {entry.fields['dataset']}", file=this_paper_file)

            print("""---

## Summary

## Importance

## Perspectives

""", file=this_paper_file)
