#!/bin/bash

# python3 -m venv .venv
# source .venv/bin/activate
# python -m pip install setuptools markdownify pybtex

./generate_html.py
./generate_latex.py
./generate_firstpages.sh
./generate_pages_template.py
