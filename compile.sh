#!/bin/sh

for i in pages/*
do
    php templates/header >> $(basename $i).html
    php $i >> $(basename $i).html
    php templates/footer >> $(basename $i).html
    git add $(basename $i).html
done

git commit -m "run of compile.sh"
