# SPDX-License-Identifier: GPL-3.0

PKGNAME = nutgatherer
PKGPATH = ttnutgatherer
COMMON_NAME = nutgatherer

IMAGES = $(wildcard media/nuts/*.png)

include extra/python.make
include extra/debian.make

cowbuild10: debbuild/deb10/${PKGNAME}_${PKG_VERSION}-1.dsc
cowbuild: cowbuild10

ttnutgatherer/nuts.atlas: ${IMAGES}
	rm ttnutgatherer/nuts-?.png
	python3 -m kivy.atlas -- ttnutgatherer/nuts 1500x1500 $^
	optipng ttnutgatherer/nuts*.png
