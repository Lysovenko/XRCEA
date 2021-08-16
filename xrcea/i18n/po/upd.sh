#!/bin/bash
git ls-files ../.. | grep \\.py$ | xargs xgettext --language=Python -cNOTE -o xrcea.pot
msguniq  xrcea.pot -u -o xrcea.pot
for i in *.po
do
    msgmerge -U "$i" xrcea.pot
    fnam="../locale/${i%.po}/LC_MESSAGES/xrcea.mo"
    if [ ! -d "../locale/${i%.po}/LC_MESSAGES" ]
    then
	mkdir -p "../locale/${i%.po}/LC_MESSAGES"
    fi
    if [ "$i" -nt "$fnam" ]
    then
	echo $fnam
	rm -f "$fnam"
	msgfmt "$i" -o "$fnam"
    fi
done


