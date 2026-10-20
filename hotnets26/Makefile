# Name of the main LaTeX file without the .tex extension
MAIN = hotnets26

# draw.io CLI: prefer one on PATH, otherwise fall back to the macOS app bundle
DRAWIO ?= $(shell command -v drawio 2>/dev/null || command -v diagrams 2>/dev/null || echo "/Applications/draw.io.app/Contents/MacOS/draw.io")

# All .drawio sources under figures/ and the PDFs they produce
DRAWIO_SRC = $(wildcard figures/*.drawio)
DRAWIO_PDF = $(DRAWIO_SRC:.drawio=.pdf)

# Default target
all: figures
	latexmk -pdf -interaction=nonstopmode $(MAIN).tex
	rm -f $(MAIN).bbl
	latexmk -c

# Build only
build: figures
	latexmk -pdf -interaction=nonstopmode $(MAIN).tex

# Regenerate figure PDFs from their .drawio sources
figures: $(DRAWIO_PDF)

# A figure PDF is rebuilt whenever its .drawio source is newer.
# If draw.io is unavailable but the PDF already exists, keep using it.
figures/%.pdf: figures/%.drawio
	@if [ -x "$(DRAWIO)" ]; then \
		"$(DRAWIO)" --export --format pdf --crop --output $@ $<; \
	elif [ -f "$@" ]; then \
		echo "draw.io not found; using existing $@"; \
	else \
		echo "Error: draw.io not found and $@ does not exist."; \
		exit 1; \
	fi

# Remove auxiliary files but keep the PDF
clean:
	latexmk -c

# Remove auxiliary files and the PDF
distclean:
	latexmk -C

# Continuously watch files and rebuild on changes
watch:
	latexmk -pdf -pvc -interaction=nonstopmode $(MAIN).tex

# Force rebuild from scratch (figures included)
rebuild:
	latexmk -C
	rm -f $(DRAWIO_PDF)
	$(MAKE) figures
	latexmk -pdf -interaction=nonstopmode $(MAIN).tex
	latexmk -c

.PHONY: all build clean distclean watch rebuild figures