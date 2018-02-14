
SOURCE=python101-spec

LATEX=lualatex

all: $(SOURCE).pdf


%.pdf : %.tex
	$(LATEX) $<
	$(LATEX) $<


clean:
	rm -f *.log
	rm -f *.nav
	rm -f *.smn
	rm -f *.out
	rm -f *.toc
	rm -f *.aux
	rm -f *.svn
	rm -f *.vrb
	rm -f *~


cleanall: clean
	rm -f $(SOURCE).pdf
