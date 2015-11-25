if [ $1 ] ; then
    pdflatex $1.tex
    bibtex $1.aux
    makeindex $1.idx
    # makeindex $1.nlo -s nomencl.ist -o $1.nls
    pdflatex $1.tex
    pdflatex $1.tex
else
    echo "falsey"
fi
