from plone.transformchain.interfaces import ITransform
from zope.interface import implements
from repoze.xmliter.serializer import XMLSerializer
from zope.component import getMultiAdapter
from collective.dynamicmosaic import dynamictiles
from collective.dynamicmosaic.interfaces import IDynamicMosaicAssignment
from zope.component.interfaces import ComponentLookupError


class DynamicTiles(object):
    """Replace dynamic tile slot ids with actual tile ids to be rendered.

    Note that this transform is typically called twice:

    - once for the site layout resource with a ``published`` object signature of:
      ``<bound method File.index_html of <File at /plone/portal_resources/sitelayout/mylayout/site.html>>``

    - once for the merged page with a ``pusblished`` signature of the Page View that
      is the initial entry point, and to which the IDynamicMosaicAssignment adapter will be bound.

    Because the dynamic tiles transformation is chained *after* the plone.app.blocks panelmerge,
    the second invocation will do tile replacements on the whole merged page, including not only
    the page layout but also the site layout.

    The upshot of this is, that this enables dynamic tile replacements of site layout tiles,
    without the need to bind the adapter to the site layout resource.
    """ # flake8:noqa

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

        try:
            assignment = getMultiAdapter((self.published, self.request),
                                         IDynamicMosaicAssignment)
        except ComponentLookupError:
            # pass unchanged
            return result

        tree = dynamictiles.assign(self.request,
                                   result.tree,
                                   assignment.tile_mapping())
        if tree is None:
            return None

        # Set a marker in the request to let subsequent steps know the
        # tile assignment has happened
        self.request['collective.dynamicmosaic.assigned'] = True

        result.tree = tree
        return result
