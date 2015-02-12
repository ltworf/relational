#!/bin/sh

for i in pages/*
do
    cat templates/header $i templates/footer > $(basename $i).html
    git add $(basename $i).html
done

git commit -m "run of compile.sh"
