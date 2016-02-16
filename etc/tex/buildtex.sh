# apt-get install texlive-full
pdflatex cidadeiluminada.tex
bibtex cidadeiluminada.aux
makeindex cidadeiluminada.idx
pdflatex cidadeiluminada.tex
pdflatex cidadeiluminada.tex
rm cidadeiluminada.bbl
rm cidadeiluminada.blg
rm cidadeiluminada.idx
rm cidadeiluminada.ind
rm cidadeiluminada.aux
rm cidadeiluminada.brf
rm cidadeiluminada.ilg
rm cidadeiluminada.log
evince cidadeiluminada.pdf &
