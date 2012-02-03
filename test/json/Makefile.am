# -*- Mode: Makefile -*-
#
# Makefile.am - automake file for Raptor JSON tests
#
# Copyright (C) 2010, David Beckett http://purl.org/net/dajobe/
# 
# This package is Free Software and part of Redland http://librdf.org/
# 
# It is licensed under the following three licenses as alternatives:
#   1. GNU Lesser General Public License (LGPL) V2.1 or any newer version
#   2. GNU General Public License (GPL) V2 or any newer version
#   3. Apache License, V2.0 or any newer version
# 
# You may not use this file except in compliance with at least one of
# the above three licenses.
# 
# See LICENSE.html or LICENSE.txt at the top of this package for the
# complete terms and further detail along with the license texts for
# the licenses in COPYING.LIB, COPYING and LICENSE-2.0.txt respectively.
# 
# 

TEST_FILES=\
example1.json example2.json example3.json example4.json

TEST_OUT_FILES=\
example1.nt example2.nt example3.nt example4.nt

JSON_BAD_TEST_FILES=bad-00.json bad-01.json bad-02.json bad-03.json \
bad-04.json bad-05.json bad-06.json bad-07.json bad-08.json bad-09.json \
bad-10.json bad-11.json bad-12.json bad-13.json

# Used to make N-triples output consistent
BASE_URI=http://example.librdf.org/

EXTRA_DIST = \
	$(TEST_FILES) \
	$(TEST_OUT_FILES) \
	$(JSON_BAD_TEST_FILES)

build-rapper:
	@(cd $(top_builddir)/utils ; $(MAKE) rapper)

if RAPTOR_PARSER_JSON
check-local: build-rapper check-json check-bad-json
else
check-local:
endif

check-json: build-rapper $(TEST_FILES)
	@result=0; \
	$(RECHO) "Testing legal JSON"; \
	for test in $(TEST_FILES); do \
	  name=`basename $$test .json` ; \
	  baseuri=$(BASE_URI)$$test; \
	  $(RECHO) $(RECHO_N) "Checking $$test $(RECHO_C)"; \
	  $(top_builddir)/utils/rapper -q -i json -o ntriples $(srcdir)/$$test $$baseuri > $$name.res 2> $$name.err; \
	  status=$$?; \
	  if test $$status != 0 -a $$status != 2 ; then \
	    $(RECHO) FAILED returned status $$status; result=1; \
	  elif cmp $(srcdir)/$$name.nt $$name.res >/dev/null 2>&1; then \
	    if test $$status = 2 ; then \
	      $(RECHO) "ok with warnings"; grep Warning $$name.err; \
	    else \
	      $(RECHO) "ok"; \
	    fi; \
	  else \
	    $(RECHO) "FAILED"; \
	    cat $$name.err; \
	    diff $(srcdir)/$$name.nt $$name.res; result=1; \
	  fi; \
	  rm -f $$name.res $$name.err; \
	done; \
	exit $$result

check-bad-json: build-rapper $(JSON_BAD_TEST_FILES)
	@set +e; result=0; \
	$(RECHO) "Testing that bad JSON fails"; \
	for test in $(JSON_BAD_TEST_FILES); do \
	  name=`basename $$test .json` ; \
	  baseuri=$(BASE_URI)$$name.json; \
	  $(RECHO) $(RECHO_N) "Checking $$test $(RECHO_C)"; \
	  $(top_builddir)/utils/rapper -q -i json -o ntriples file:$(srcdir)/$$test $$baseuri > $$name.res 2> $$name.err; \
	  status=$$?; \
	  if test $$status -eq 1 ; then \
	    $(RECHO) "ok"; \
	  elif test $$status -eq 2 ; then \
	    $(RECHO) "FAILED - parsing succeeded with a warning"; \
	    cat $$name.res; grep Warning $$name.err; result=1; \
	  elif test $$status -eq 0 ; then \
	    $(RECHO) "FAILED - parsing succeeded but should have failed"; \
	    cat $$name.res; result=1; \
	  else \
	    $(RECHO) "FAILED - parsing failed with unknown status $$status"; \
	    cat $$name.res; result=1; \
	  fi; \
	  rm -f $$name.res $$name.err ; \
	done; \
	set -e; exit $$result

