# -*- coding: utf-8 -*-
# :Project:   pj -- examples makefile
# :Created:   lun 07 mar 2016 01:43:23 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#

WP := node_modules/.bin/webpack -v

.PHONY: serve
serve: www/colorflash/bundle.js
	@echo "Please visit http://localhost:8000 with a browser"
	cd www/colorflash && python -m http.server

www/colorflash/bundle.js: node_modules/.bin/webpack js
	@echo "Building the bundle"
	$(WP)

js:
	@echo "Compiling sources..."
	pj -o js src

node_modules/.bin/webpack:
	@echo "Installing nodejs dependencies"
	npm install
