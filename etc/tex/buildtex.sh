# apt-get install texlive-full
if [ $1 ] ; then
    pdflatex $1.tex
    bibtex $1.aux
    makeindex $1.idx
    pdflatex $1.tex
    pdflatex $1.tex
else
    echo "falsey"
fi
