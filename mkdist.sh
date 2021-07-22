#!/bin/bash
for lang in eng ukr
do
    make html -C doc/$lang
done
cd i18n/po
for i in *.po
do
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
cd -
python3 setup.py sdist --formats="zip,gztar"
rm -rf XRCEA.egg-info
