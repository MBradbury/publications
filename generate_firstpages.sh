#!/bin/bash

for paper in papers/*.pdf
do
	target="firstpages/$(basename $paper)"
	target=${target//pdf/png}

	echo "$paper -> $target"

	gs -o $target -sDEVICE=png16m -r300 -dDownScaleFactor=3 -dFirstPage=1 -dPDFLastPage=1 $paper
done
