#! /bin/sh
cd /
pytest --cov-report xml:/out/coverage.xml --cov=code code/
sed -i 's|<source>/code</source>|<source>code</source>|g' /out/coverage.xml