# SPDX-License-Identifier: GPL-3.0

PKGNAME = nutgatherer
PKGPATH = ttnutgatherer
COMMON_NAME = nutgatherer

include extra/python.make
include extra/debian.make

cowbuild10: debbuild/deb10/${PKGNAME}_${PKG_VERSION}-1.dsc
cowbuild: cowbuild10
