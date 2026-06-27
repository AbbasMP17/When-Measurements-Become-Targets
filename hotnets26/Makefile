# Name of the main LaTeX file without the .tex extension
MAIN = hotnets26

# Default target
all:
	latexmk -pdf -interaction=nonstopmode $(MAIN).tex
	rm -f $(MAIN).bbl
	latexmk -c

# Build only
build:
	latexmk -pdf -interaction=nonstopmode $(MAIN).tex

# Remove auxiliary files but keep the PDF
clean:
	latexmk -c

# Remove auxiliary files and the PDF
distclean:
	latexmk -C

# Continuously watch files and rebuild on changes
watch:
	latexmk -pdf -pvc -interaction=nonstopmode $(MAIN).tex

# Force rebuild from scratch
rebuild:
	latexmk -C
	latexmk -pdf -interaction=nonstopmode $(MAIN).tex
	latexmk -c

.PHONY: all build clean distclean watch rebuild