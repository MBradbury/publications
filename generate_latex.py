#!/usr/bin/env python3
# Based on: https://github.com/StreakyCobra/plugins/blob/master/v7/publication_list/publication_list.py

import os.path

from pybtex.plugin import find_plugin
from pybtex.database import parse_file
from pybtex.database import BibliographyData

style = find_plugin('pybtex.style.formatting', 'plain')(abbreviate_names=True)

def process_bib(filename, sections):
    with open(filename) as bibtex_file:
        db = parse_file(bibtex_file, 'bibtex')

    data = list(sorted(db.entries.items(), key=lambda e: e[1].fields.get("year", 0), reverse=True))

    highlight_author = "M.~Bradbury"
    tex_output = ""

    for section_name, section_types in sections.items():

        tex_output += f'\\section{{{section_name}}}\n'

        cur_year = None

        for label, entry in data:
            # Skip entries that we should not print
            if entry.type not in section_types:
                continue

            if section_name in {"Published Journal Papers", "Published Conference and Workshop Papers"}:
                # print a year title when year changes
                if entry.fields.get("year", None) != cur_year:
                    if cur_year is not None:  # not first year group
                        tex_output += "\\end{bibsection}\n"

                    first_entry = cur_year is None
                    cur_year = entry.fields["year"]

                    if first_entry:
                        tex_output += f"\\vspace{{-\\baselineskip}}\\subsectionhidden{{{cur_year}}}\n"
                    else:
                        tex_output += f"\\subsection{{{cur_year}}}\n"

                    tex_output += "\\begin{bibsection}\n\\small\n"
            else:
                if cur_year is None:
                    tex_output += "\\begin{bibsection}\n\\small\n"
                    cur_year = True

            pub_latex = list(style.format_entries([entry]))[0].text.render_as("latex")
            if highlight_author:  # highlight an author (usually oneself)
                pub_latex = pub_latex.replace(highlight_author, f"\\textbf{{{highlight_author}}}", 1)
            tex_output += f'\\item {pub_latex}'

            tex_output += "\n"

        if len(data) != 0:  # publication list is nonempty
            tex_output += "\n"

        tex_output += "\\end{bibsection}\n"

    return tex_output


tex_output = ""

tex_output += process_bib("self.bib", sections={
    "Published Journal Papers": {"article"},
    "Published Conference and Workshop Papers": {"inproceedings"},
    #"Publications": {"inproceedings", "article"},
    "PhD Thesis": {"phdthesis"},
    "Technical Reports": {"techreport"},
})

tex_output += process_bib("preparation.bib", sections={
    "Papers in Preparation": {"unpublished"},
})

tex_output += process_bib("event.bib", sections={
    "Event Reports": {"article", "techreport"},
})

with open("out.tex", "w") as out:
    print(tex_output, file=out)
