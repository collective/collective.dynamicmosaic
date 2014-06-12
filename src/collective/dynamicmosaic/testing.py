from plone.app.blocks.testing import BLOCKS_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class CollectivedynamicmosaicLayer(PloneSandboxLayer):

    # re-use the testing infrastructure of plone.app.blocks
    defaultBases = (BLOCKS_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.dynamicmosaic
        xmlconfig.file(
            'configure.zcml',
            collective.dynamicmosaic,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.dynamicmosaic:default')

COLLECTIVE_DYNAMICMOSAIC_FIXTURE = CollectivedynamicmosaicLayer()
COLLECTIVE_DYNAMICMOSAIC_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_DYNAMICMOSAIC_FIXTURE,),
    name="CollectivedynamicmosaicLayer:Integration"
)
COLLECTIVE_DYNAMICMOSAIC_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_DYNAMICMOSAIC_FIXTURE, z2.ZSERVER_FIXTURE),
    name="CollectivedynamicmosaicLayer:Functional"
)
