.PHONY: packaging

packaging:
	cd web && tar czvf ../packaging/web.tar.gz ./*
