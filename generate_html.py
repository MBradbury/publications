#!/usr/bin/env python3
# Based on: https://github.com/StreakyCobra/plugins/blob/master/v7/publication_list/publication_list.py

import os.path
import re

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

bibtex_dir = "bibtex"
highlight_author = "Matthew Bradbury"
root_dir = "https://github.com/MBradbury/publications/raw/master"

publication_h_number = 4

html_output = ""

for section_name, section_types in sections.items():

    html_output += f'<h2 id="{section_name.replace(" ", "")}">{section_name}</h2>\n'

    html_output += '<div class="publication-list">\n'
    cur_year = None

    for label, entry in data:
        # Skip entries that we should not print
        if entry.type not in section_types:
            continue

        if section_name == "Publications":
            # print a year title when year changes
            if entry.fields["year"] != cur_year:
                if cur_year is not None:  # not first year group
                    html_output += "\t</ul>\n"
                cur_year = entry.fields["year"]
                html_output += f"\t<h{publication_h_number} id='pub_{cur_year}'>{cur_year}</h{publication_h_number}>\n\t<ul>\n"
        else:
            if cur_year is None:
                html_output += "\t<ul>\n"
                cur_year = True

        pub_html = list(style.format_entries([entry]))[0].text.render_as("html")
        pub_html = pub_html.replace("\n", " ")
        if highlight_author:  # highlight an author (usually oneself)
            pub_html = pub_html.replace(highlight_author, "<strong>{}</strong>".format(highlight_author), 1)
        html_output += f'\t\t<li class="publication" id="{entry.key.replace(":", "_")}">\n\t\t\t' + pub_html

        extra_links = []
        if bibtex_dir:  # write bib files to bibtex_dir for downloading
            sanitised_label = label.replace(":", "_")
            bib_link = f"{bibtex_dir}/{sanitised_label}.bib"
            BibliographyData({label: entry}).to_file(bib_link, "bibtex")
            extra_links.append(f'[<a href="{root_dir}/{bib_link}">bibtex</a>]')

        if "file" in entry.fields:  # the link to the pdf file
            (a, filename, kind) = entry.fields["file"].split(":", 2)

            file_path = os.path.join("papers", filename)
            presentation_path = os.path.join("presentations", filename)

            extra_links.append(f'[<a href="{root_dir}/{file_path}">file</a>]')

            if "presentation" in entry.fields:
                (_, presentation_filename, _) = entry.fields["presentation"].split(":", 2)
                presentation_path = os.path.join("presentations", presentation_filename)
            if os.path.exists(presentation_path):
                extra_links.append(f'[<a href="{root_dir}/{presentation_path}">presentation</a>]')

        if "dataset" in entry.fields:
            dataset_path = entry.fields["dataset"]
            extra_links.append(f'[<a href="{dataset_path}">dataset</a>]')

        if extra_links:
            html_output += "<br/>" + " ".join(extra_links)

        html_output += "\n\t\t</li>\n"

    if len(data) != 0:  # publication list is nonempty
        html_output += "\t</ul>\n"

    html_output += "</div>\n"

md_output = md(html_output, heading_style="ATX")

# Not all headings will be formatted correctly, some may have leading spaces
md_output = re.sub(r" +#", "#", md_output)

with open("out.html", "w") as out:
    print(html_output, file=out)

with open("README.md", "w") as readme:
    print(md_output, file=readme)
