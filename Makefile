all:

install:
	install -m755 ac_import.py $(HOME)/.gimp-2.8/plug-ins

.PHONY: all install
