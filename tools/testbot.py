#!/usr/bin/env python

import sys, httplib2

h = httplib2.Http()
print h.request(sys.argv[1], 'HEAD')
