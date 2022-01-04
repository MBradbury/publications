#!/bin/bash
# sudo apt-get install poppler-utils

mkdir -p firstpages
mkdir -p presentations-firstpages

for paper in papers/*.pdf
do
	target="firstpages/$(basename $paper)"
	target=${target//pdf/svg}

	echo "$paper -> $target"

	pdftocairo -svg -f 1 -l 1 "$paper" "$target"
done

for paper in presentations/*.pdf
do
	target="presentations-firstpages/$(basename $paper)"
	target=${target//pdf/svg}

	echo "$paper -> $target"

	pdftocairo -svg -f 1 -l 1 "$paper" "$target"
done
