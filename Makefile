packaging:
	[ -d packaging/theme ] && rm -rf packaging/theme || :
	cp -r theme packaging/theme
