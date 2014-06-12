from plone.transformchain.interfaces import ITransform
from zope.interface import implements
from repoze.xmliter.serializer import XMLSerializer
from collective.dynamicmosaic import dynamictiles


class DynamicTiles(object):
    """Replace dynamic tile slot ids with actual tile ids to be rendered.
    """

    implements(ITransform)

    order = 8400

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def transformString(self, result, encoding):
        return None

    def transformUnicode(self, result, encoding):
        return None

    def transformIterable(self, result, encoding):
        if not self.request.get('plone.app.blocks.enabled', False) or \
                not isinstance(result, XMLSerializer):
            return None

        tree = dynamictiles.assign(self.request, result.tree)
        if tree is None:
            return None

        # Set a marker in the request to let subsequent steps know the
        # tile assignment has happened
        self.request['collective.dynamicmosaic.assigned'] = True

        result.tree = tree
        return result
