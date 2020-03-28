# SPDX-License-Identifier: GPL-3.0
# debian.make: 2020-02-28.1

debian_orig_tar := debbuild/${PKGNAME}_${PKG_VERSION}.orig.tar.gz

.SECONDARY:

# Native package:
debbuild/deb%/${PKGNAME}_${PKG_VERSION}-1.dsc: debbuild/${PKGNAME}_${PKG_VERSION}-1.dsc
	@rm -rf debbuild/deb$*
	@mkdir -p /tmp/cowbuild.${USER}
	cb -$* -o debbuild/deb$* $<  >/tmp/cowbuild.${USER}/${PKGNAME}.$*.log 2>&1 || cat /tmp/cowbuild.${USER}/${PKGNAME}.$*.log
	@ln -f ${debian_orig_tar} debbuild/deb$*/

debbuild/${PKGNAME}-${PKG_VERSION}.tstamp: ${debian_orig_tar}
	rm -rf '$(basename $@)'
	cd debbuild && tar -xf $(notdir ${debian_orig_tar})
	date >$@

debbuild/${PKGNAME}_${PKG_VERSION}-1.dsc: debbuild/${PKGNAME}-${PKG_VERSION}.tstamp
	@head -n1 debian/changelog | grep "(${PKG_VERSION}-1)" debian/changelog || (/bin/echo -e "\e[1m\e[91m** debian/changelog requires update **\e[0m" && false)
	rm -rf 'debbuild/${PKGNAME}_${PKG_VERSION}-1' 'debbuild/${PKGNAME}_${PKG_VERSION}-1_'*
	cp -a 'debbuild/${PKGNAME}-${PKG_VERSION}' 'debbuild/${PKGNAME}_${PKG_VERSION}-1'
	cp -a debian 'debbuild/${PKGNAME}_${PKG_VERSION}-1/'
	cd 'debbuild/${PKGNAME}_${PKG_VERSION}-1' && dpkg-source --build .

release:: | test
	perl -MTime::Piece -pi -E 'if(/^\w/ and not $$done) { $$done=1; /released/||do{chomp;$$_.=" released ".localtime->ymd()."\n"} }' ChangeLog.txt
	(head -n1 debian/changelog | grep -q ${PKG_VERSION}-) || dch -v ${PKG_VERSION}-1 --distribution unstable  "New release"
	dch --release ''
	$(MAKE) cowbuild
	@rm -rf _release/${PKG_VERSION}; mkdir -p _release/${PKG_VERSION}
	rsync -aH --del debbuild/deb?? _release/${PKG_VERSION}/
	rm -rf debbuild

version-bump::
	dch -v ${NEW_VERSION}-1 --distribution unstable  "New release"
