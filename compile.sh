#!/bin/sh

for i in pages/*
do
    cat templates/header $i templates/footer > $(basename $i).html
    git add $(basename $i).html
    git commit -m "compile.sh"
done
