# -*- coding: utf-8 -*-
import unittest2 as unittest
import doctest
from plone.testing import layered

from collective.dynamicmosaic.testing import \
    COLLECTIVE_DYNAMICMOSAIC_INTEGRATION_TESTING

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_NDIFF)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([layered(
        doctest.DocFileSuite('rendering.rst',
                             optionflags=optionflags),
        layer=COLLECTIVE_DYNAMICMOSAIC_INTEGRATION_TESTING),
    ])
    return suite
