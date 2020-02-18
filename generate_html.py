#!/usr/bin/env python3

# Based on: https://github.com/StreakyCobra/plugins/blob/master/v7/publication_list/publication_list.py

IMG_DOC = "https://www2.warwick.ac.uk/brands/icons/acrobat.gif"
IMG_PRES = "https://www2.warwick.ac.uk/brands/icons/powerpoint.gif"

import os.path
from pybtex.plugin import find_plugin
from pybtex.database import parse_file
from pybtex.database import BibliographyData
from markdownify import markdownify as md

style = find_plugin('pybtex.style.formatting', 'plain')()
HTML = find_plugin('pybtex.backends', 'html')()

with open('self.bib') as bibtex_file:
    db = parse_file(bibtex_file, 'bibtex')

data = sorted(db.entries.items(), key=lambda e: e[1].fields["year"], reverse=True)

def run(data, style):
    bibtex_dir = "bibtex"
    highlight_author = "Matthew Bradbury"
    root_dir = "https://raw.githubusercontent.com/MBradbury/publications/master"

    html = '<div class="publication-list">\n'
    cur_year = None

    for label, entry in data:
        # print a year title when year changes
        if entry.fields["year"] != cur_year:
            if cur_year is not None:  # not first year group
                html += "</ul>"
            cur_year = entry.fields["year"]
            html += "<h4>{}</h4>\n<ul>".format(cur_year)

        pub_html = list(style.format_entries((entry,)))[0].text.render_as("html")
        if highlight_author:  # highlight an author (usually oneself)
            pub_html = pub_html.replace(highlight_author, "<strong>{}</strong>".format(highlight_author), 1)
        html += '<li class="publication">' + pub_html

        extra_links = []
        if bibtex_dir:  # write bib files to bibtex_dir for downloading
            sanitised_label = label.replace(":", "_")
            bib_link = f"{bibtex_dir}/{sanitised_label}.bib"
            bib_data = BibliographyData({label: entry})
            bib_data.to_file(bib_link, "bibtex")
            extra_links.append(f'[<a href="{root_dir}/{bib_link}">bibtex</a>]')

        if "file" in entry.fields:  # the link to the pdf file
            (a, filename, kind) = entry.fields["file"].split(":", 2)
            filepath = os.path.join("papers", filename)

            extra_links.append(f'[<a href="{root_dir}/{filepath}">file</a>]')

            presentation_path = os.path.join("presentations", filename)
            if os.path.exists(presentation_path):
                extra_links.append(f'[<a href="{root_dir}/{presentation_path}">presentation</a>]')

        if extra_links:
            html += "<br/>" + " ".join(extra_links)

        html += "</li>"

    if len(data) != 0:  # publication list is nonempty
        html += "</ul>"

    html += "</div>"

    return html

html_output = run(data, style)
md_output = md(html_output)

with open("out.html", "w") as out:
    print(html_output, file=out)

with open("README.md", "w") as readme:
    print(md_output, file=readme)
