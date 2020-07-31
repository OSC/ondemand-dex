.PHONY: packaging

packaging:
	cd theme && tar czvf ../packaging/theme.tar.gz ./*
	cd templates && tar czvf ../packaging/templates.tar.gz ./*
	cd static && tar czvf ../packaging/static.tar.gz ./*
