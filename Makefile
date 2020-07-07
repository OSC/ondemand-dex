.PHONY: packaging

packaging:
	cd theme && tar czvf ../packaging/theme.tar.gz ./*
