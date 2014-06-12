# -*- coding: utf-8 -*-
from lxml import etree

dynamictileXPath = etree.XPath("//*[@data-dynamic-tile]")


def assign(request, pageTree, tile_mapping={}):
    """Perform dynamic tile placing for the given page.
    """

    # Map concrete page tile ids onto dynamic tile slots

    dynamicTiles = dict(
        (node.attrib['data-dynamic-tile'], node)
        for node in dynamictileXPath(pageTree)
    )

    for (id, tile) in dynamicTiles.items():
        if id in tile_mapping:
            del tile.attrib['data-dynamic-tile']
            tile.attrib['data-tile'] = tile_mapping[id]

    return pageTree
