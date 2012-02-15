# $Id: GNUmakefile,v 1.4 2008-12-01 07:23:29 kmura Exp $
# $Name: not supported by cvs2svn $
# ===========================================================
#   Makefile for building Geant4Py site-modules
# ===========================================================
include  ../config/config.gmk

SUBDIR := geometries materials physics_lists primaries python

.PHONY: all install clean

all:
	@for dir in $(SUBDIR); do (cd $$dir && $(MAKE)); done;:

install:
	@for dir in $(SUBDIR); do (cd $$dir && $(MAKE) install); done;:

clean:
	@for dir in $(SUBDIR); do (cd $$dir && $(MAKE) clean); done;:

