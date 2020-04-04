# SPDX-License-Identifier: GPL-3.0
# python.make: 2020-02-28.1

YEAR ?= $(shell date +%Y)
TODAY ?= $(shell date +%Y-%m-%d)

PKG_VERSION ?= $(shell python3 -c 'import re; print(re.search(r"__version__ = \"([\d.]+)\"", open("${PKGPATH}/__init__.py").read()).group(1))')
NEW_PYTHON_VERSION := $(shell perl -E '($$y,$$m)=(localtime)[5,4];$$m++;$$y-=100;$$r=0;$$r=$$1+1 if 0==index("${PKG_VERSION}","$$y.$$m") and "${PKG_VERSION}" =~ /\.(\d+)$$/; say "$$y.$$m.$$r"')
NEW_VERSION ?= ${NEW_PYTHON_VERSION}
PY_PATHS ?= ${PKGNAME} tests

SOURCES ?= $(shell cat ${PKGPATH}.egg-info/SOURCES.txt 2>/dev/null)


.PHONY: check
check::
	python3 -m flake8 --config=extra/flake8.ini ${PY_PATHS}
	@echo OK

clean::
	rm -rf cover build dist debbuild ${PKGPATH}.egg-info
	rm -f .coverage .prove MANIFEST
	pyclean .

debbuild/${PKGNAME}_${PKG_VERSION}.orig.tar.gz: ${PKGPATH}.egg-info/SOURCES.txt $(SOURCES)
	$(MAKE) test
	python3 setup.py sdist
	@rm -rf debbuild; mkdir -p debbuild
	mv -f dist/${PKGNAME}-${PKG_VERSION}.tar.gz debbuild/${PKGNAME}_${PKG_VERSION}.orig.tar.gz
	@rmdir --ignore-fail-on-non-empty dist

${PKGPATH}.egg-info/SOURCES.txt:
	python3 setup.py sdist

.PHONY: test
test::
	python3 -E -B -m nose --verbosity=0 tests

version-bump::
	perl -pi -E 's/\Q${PKG_VERSION}\E/${NEW_VERSION}/' ${PKGPATH}/__init__.py

.PHONY: zip
zip::
	python3 setup.py sdist --format=zip
