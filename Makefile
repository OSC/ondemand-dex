.PHONY: packaging
TAR := tar
VERSION := 2.27.0

deb-packaging:
	git ls-files | $(TAR) -c \
		--transform 'flags=r;s,packaging/deb,debian,' \
		--transform 's,^,ondemand-dex-$(VERSION)/,' -T - | gzip > build/ondemand-dex-$(VERSION).tar.gz

rpm-packaging:
	cd web && tar czvf ../packaging/rpm/web.tar.gz ./*
