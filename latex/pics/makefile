Source=Hex-5.tex Hex-6.tex Hex-7.tex Hexagon-1.tex Hexagon-2.tex Hexagon-3.tex Poly10-8.tex Poly-1.tex Poly-2.tex Poly-3.tex Poly5-7.tex Poly8-18.tex Sqr-1.tex Sqr-2.tex Sqr-3.tex Square-1.tex Square-2.tex Square-3.tex Tri-1.tex Tri-2.tex Tri-3.tex Tri-H.tex Tri-S.tex Tri-T.tex

Square.pdf: $(Source) allpics.tex
	pdflatex allpics
	pdftk allpics.pdf burst
	pdfcrop pg_0001.pdf Square.pdf
	pdfcrop pg_0002.pdf Sqr.pdf
	pdfcrop pg_0003.pdf Triangle.pdf
	pdfcrop pg_0004.pdf Tri.pdf
	pdfcrop pg_0005.pdf Hexagon.pdf
	pdfcrop pg_0006.pdf Hex-n.pdf
	pdfcrop pg_0007.pdf Poly.pdf
	pdfcrop pg_0008.pdf Poly2.pdf
	rm pg_000[1-8].pdf doc_data.txt
