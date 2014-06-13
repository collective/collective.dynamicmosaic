.. contents::

Introduction
============

This package builds on the transform chain configured in `plone.app.blocks`_.
It adds to that an extra transform that makes it possible to assign tiles
to tile slots at render-time.

The intent is that a designer can create generic page and site layouts,
but the decision of what content should be rendered where is made runtime.
A pluggable adapter architecture makes it possible to configure rendering
policies at will.


Dynamic blocks rendering in detail
==================================

At a high level, the rendering process consists of the following steps:

plone.app.blocks
----------------

0. Obtain the content page, an HTML document.

1. Look for a site layout link in the content page. This takes the form of an
   attribute on the html tag like ``<html data-layout="..." />``.

   Usually, the site layout URL will refer to a resource in a resource
   directory of type ``sitelayout``, e.g. ``/++sitelayout++foo/site.html``,
   although the layout can be any URL. An absolute path like this will be
   adjusted so that it is always relative to the Plone site root.

2. Resolve and obtain the site layout. This is another HTML document.

3. Extract panels from the site layout.

   A panel is an element (usually a ``<div />``) in the layout page with a
   data-panel attribute, for example: ``<div data-panel="panel1" />``. The
   attribute specifies an id which *may* be used in the content page.

4. Merge panels. This is the process which applies the layout to the
   unstyled page. All panels in the layout page that have a matching
   element in the content page, are replaced by the content page element.
   The rest of the content page is discarded.


collective.dynamicmosaic
------------------------

5. Look for dynamic tile slots in the content page template.

   A dynamic tile is an element (usually a ``<div />``) in the layout page with a
   ``data-dynamic-tile`` attribute, for example: ``<div data-dynamic-tile="A" />``.

   The attribute specifies an id which *may* be used as a slot name into which
   a concrete tile id can be placed.

   By convention, dynamic tile ids are single-letter capitals placed in the 
   template in such a way that the most prominent slot is 'A', the second
   most prominent slot is 'B' etc.

6. Resolve and obtain an ``IDynamicMosaicAssignment`` adapter that provides a mapping
   from dynamic tile slot id to concrete tile ids that can be resolved
   by plone.app.blocks in step 5 below.

7. Replace all dynamic ``data-dynamic-tile`` ids with concrete ``data-tile`` ids.
   Because this step occurs *after* the panel merging (4. above) it affects
   all tile slots, whether defined in the page layout or in the site layout.

   The injected ``data-tile`` ids will then be expanded into the actual tile
   renderings by plone.app.blocks below.


plone.app.blocks again
----------------------

8. Resolve and obtain tiles. A tile is a placeholder element in the page
   which will be replaced by the contents of a document referenced by a URL.

   A tile is identified by a placeholder element with a ``data-tile``
   attribute containing the tile URL.

   Note that at this point, panel merging has taken place, so if a panel in
   the content page contains tiles, they will be carried over into the merged
   page. Also note that it is possible to have tiles outside of panels - the
   two concepts are not directly related.

   The ``plone.tiles`` package provides a framework for writing tiles,
   although in reality a tile can be any HTML page.

9. Place tiles into the page. The tile should resolve to a full HTML
   document. Any content found in the ``<head />`` of the tile content will
   be merged into the ``<head />`` of the rendered content. The contents of
   the ``<body />`` of the tile content are put into the rendered document
   at the tile placeholder.


.. _plone.app.blocks: http://github.com/plone/plone.app.blocks
