#!/bin/bash
set -e
python3 preprocess.py
latexmk -shell-escape -xelatex -file-line-error -halt-on-error -interaction=nonstopmode -output-directory=build main.l.tex
