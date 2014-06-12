# -*- coding: utf-8 -*-
from lxml import etree

dynamictileXPath = etree.XPath("//*[@data-dynamic-tile]")


def assign(request, pageTree):
    """Perform dynamic tile placing for the given page.
    """

    # Map concrete page tile ids onto dynamic tile slots

    dynamicTiles = dict(
        (node.attrib['data-dynamic-tile'], node)
        for node in dynamictileXPath(pageTree)
    )

    # hardcode mapping for now -- WIP
    slotmapping = {'A': './@@test.tile1/tile2?magicNumber:int=2',
                   'B': './@@test.tile1/tile3',
                   'X': './@@test.tile1/tile4'}

    for (slotId, tile) in dynamicTiles.items():
        if slotId in slotmapping:
            del tile.attrib['data-dynamic-tile']
            tile.attrib['data-tile'] = slotmapping[slotId]

    return pageTree
