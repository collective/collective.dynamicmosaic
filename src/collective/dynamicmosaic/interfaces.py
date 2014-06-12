from zope.interface import Interface


class IDynamicMosaicLayer(Interface):
    """Browser layer used to ensure dynamic mosaic functionality
    can be installed on a site-by-site basis.
    """


class IDynamicMosaicEnabled(Interface):
    """Marker interface for content or site layouts for which tile id
    substitution should take place.
    """


class IDynamicMosaicAssignment(Interface):
    """Interface for multi adapters providing a mapping from
    "data-dynamic-tile" -> "data-tile" ids.

    An adapter implementing this interface would typically be used
    for on-the-fly runtime decisions which tiles should be rendered
    for the specific context and request.
    """

    def __init__(published, request):
        """Multi adapter that can be resolved from within the transform chain.

        ``published`` is the published object.
        It should be marked ``IDynamicMosaicEnabled``.
        This can be a site layout, or it can be a content context object.

        ``request`` should provide ``IDynamicMosaicLayer``.
        """

    def tile_mapping():
        """Returns: a dict-like key->value mapping of data-dynamic-tile keys
        to data-tile values.

        See tests/render.rst for example.
        """
