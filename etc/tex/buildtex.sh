# apt-get install texlive-full
pdflatex cidadeiluminada.tex
bibtex cidadeiluminada.aux
makeindex cidadeiluminada.idx
pdflatex cidadeiluminada.tex
pdflatex cidadeiluminada.tex
rm  !(*.tex|*.bib|*.sh|*.pdf|android|site)
evince cidadeiluminada.pdf &
