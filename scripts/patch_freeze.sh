#!/bin/bash
echo -n "patch django-freeze..."
#parserfile="/home/vagrant/.local/lib/python3.8/site-packages/freeze/parser.py"
parserfiledir=$(pip show django_freeze | grep Location | cut -d " " -f2)
parserfile="${parserfiledir}/freeze/parser.py"
#echo -n $parserfile
if test -f $parserfile; then
    sed -i '/from django.core.urlresolvers import reverse, NoReverseMatch/c from django.urls import reverse, NoReverseMatch' $parserfile
    echo "OK"
else
    echo "not OK"
fi
