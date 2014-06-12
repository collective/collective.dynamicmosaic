Dynamic blocks rendering
========================

This package builds on the transform chain configured in plone.app.blocks.
It adds to that an extra transform that generates page layouts from
page layout templates.

The intent is that a designer can create a generic page layout, but
the decision of what content should be rendered there is made runtime.

The doctest below is a twist on the rendering.rst test from plone.app.blocks.
The numeric rendering steps are performed by plone.app.blocks.
The alphabetic rendering steps are performed by collective.dynamicmosaic.


Blocks rendering in detail
==========================

This doctest illustrates the blocks rendering process. At a high level, it
consists of the following steps:

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



   --- dynamicmosaic specific ---

A. Look for dynamic tile slots in the content page template.

   A dynamic tile is an element (usually a ``<div />``) in the layout page with a
   data-dynamic-tile attribute, for example: ``<div data-dynamic-tile="A" />``.

   The attribute specifies an id which *may* be used as a slot name into which
   a concrete tile id can be placed.

   By convention, dynamic tile ids are single-letter capitals placed in the 
   template in such a way that the most prominent slot is 'A', the second
   most prominent slot is 'B' etc.

B. Resolve and obtain an IDynamicMosaic adapter that provides a mapping
   from dynamic tile slot id to concrete tile ids that can be resolved
   by plone.app.blocks in step 5 below.

C. Replace all dynamic tile ids with the concrete tile ids to be rendered.
   This transforms our dynamicmosaic page layout template containing tile slots,
   into a concrete plone.app.blocks page layout with concrete tile ids.


   ---/ dynamicmosaic specific ---



5. Resolve and obtain tiles. A tile is a placeholder element in the page
   which will be replaced by the contents of a document referenced by a URL.

   A tile is identified by a placeholder element with a ``data-tile``
   attribute containing the tile URL.

   Note that at this point, panel merging has taken place, so if a panel in
   the content page contains tiles, they will be carried over into the merged
   page. Also note that it is possible to have tiles outside of panels - the
   two concepts are not directly related.

   The ``plone.tiles`` package provides a framework for writing tiles,
   although in reality a tile can be any HTML page.

6. Place tiles into the page. The tile should resolve to a full HTML
   document. Any content found in the ``<head />`` of the tile content will
   be merged into the ``<head />`` of the rendered content. The contents of
   the ``<body />`` of the tile content are put into the rendered document
   at the tile placeholder.


Rendering step-by-step
----------------------

Let us now illustrate the rendering process. We'll need a few variables
defined first:

    >>> from plone.testing.z2 import Browser
    >>> import transaction

    >>> app = layer['app']
    >>> portal = layer['portal']

    >>> browser = Browser(app)
    >>> browser.handleErrors = False

Creating a site layout
~~~~~~~~~~~~~~~~~~~~~~

The most common approach for managing site layouts is to use a resource
registered using a ``plone.resource`` directory of type ``sitelayout``, and
then use the ``@@default-site-layout`` view to reference the content. We will
illustrate this below, but it is important to realise that
``plone.app.blocks`` works by post-processing responses rendered by Zope. The
content and layout pages could just as easily be created by views of content
objects, or even resources external to Zope/Plone.

First, we will create a resource representing the site layout and its panels.
This includes some resources and other elements in the ``<head />``,
``<link />`` tags which identify tile placeholders and panels, as well as
content inside and outside panels. The tiles in this case are managed by
``plone.tiles``, and are both of the same type.

    >>> layoutHTML = """\
    ... <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    ... <html>
    ...     <head>
    ...         <title>Layout title</title>
    ...         <link rel="stylesheet" href="/layout/style.css" />
    ...         <script type="text/javascript">alert('layout');</script>
    ...
    ...         <style type="text/css">
    ...         div {
    ...             margin: 5px;
    ...             border: dotted black 1px;
    ...             padding: 5px;
    ...         }
    ...         </style>
    ...
    ...         <link rel="stylesheet" data-tile="./@@test.tile_nobody/tile_css" />
    ...     </head>
    ...     <body>
    ...         <h1>Welcome!</h1>
    ...         <div data-panel="panel1">Layout panel 1</div>
    ...         <div data-panel="panel2">
    ...             Layout panel 2
    ...             <div id="layout-tile1" data-tile="./@@test.tile1/tile1">Layout tile 1 placeholder</div>
    ...         </div>
    ...         <div data-panel="panel3">
    ...             Layout panel 3
    ...             <div id="layout-tile2" data-tile="./@@test.tile1/tile2">Layout tile 2 placeholder</div>
    ...         </div>
    ...     </body>
    ... </html>
    ... """

We can create an in-ZODB resource directory of type ``sitelayout`` that
contains this layout. Another way would be to register a resource directory
in a package using ZCML, or use a global resource directory. See
``plone.resource`` for more details.

    >>> from Products.CMFCore.utils import getToolByName
    >>> from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
    >>> from StringIO import StringIO
    >>> from OFS.Image import File

    >>> resources = getToolByName(portal, 'portal_resources')
    >>> resources._setOb('sitelayout', BTreeFolder2('sitelayout'))
    >>> resources['sitelayout']._setOb('mylayout', BTreeFolder2('mylayout'))
    >>> resources['sitelayout']['mylayout']._setOb('site.html', File('site.html', 'site.html', StringIO(layoutHTML)))

    >>> transaction.commit()

This resource can now be accessed using the path
``/++sitelayout++mylayout/site.html``. Let's render it on its own to verify
that.

    >>> browser.open(portal.absolute_url() + '/++sitelayout++mylayout/site.html')

Because of an annoying lxml cross-platform output inconsistency, we need to sanitize
the output a bit.

    >>> print browser.contents.replace('<head><meta', '<head>\n\t<meta')
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
          <meta http-equiv="Content-Type" content="text/html; charset=ASCII" />
          <title>Layout title</title>
          <link rel="stylesheet" href="/layout/style.css" />
          <script type="text/javascript">alert('layout');</script>
        <style type="text/css">
            div {
                margin: 5px;
                border: dotted black 1px;
                padding: 5px;
            }
            </style>
        <link rel="stylesheet" data-tile="./@@test.tile_nobody/tile_css" />
          </head>
          <body>
            <h1>Welcome!</h1>
            <div data-panel="panel1">Layout panel 1</div>
            <div data-panel="panel2">
                Layout panel 2
                <div id="layout-tile1" data-tile="./@@test.tile1/tile1">Layout tile 1 placeholder</div>
            </div>
            <div data-panel="panel3">
                Layout panel 3
                <div id="layout-tile2" data-tile="./@@test.tile1/tile2">Layout tile 2 placeholder</div>
            </div>
        </body>
    </html>

We can now set this as the site-wide default layout by setting the registry
key ``plone.defaultSiteLayout``. There are two indirection views,
``@@default-site-layout`` and ``@@page-site-layout``, that respect this
registry setting. By using one of these views to reference the layout of
a given page, we can manage the default site layout centrally.

    >>> from zope.component import getUtility
    >>> from plone.registry.interfaces import IRegistry
    >>> registry = getUtility(IRegistry)
    >>> registry['plone.defaultSiteLayout'] = '/++sitelayout++mylayout/site.html'
    >>> transaction.commit()


Creating tiles
~~~~~~~~~~~~~~

We register a tile type which we can use to test tile rendering.

We do this in code for the purposes of the test, and we have to apply security
because we will shortly render those pages using the test publisher. In real
life, these could be registered using the standard ``<plone:tile />`` directive.

    >>> from zope.interface import Interface, implements
    >>> from zope import schema
    >>> from plone.tiles import Tile

    >>> class ITestTile(Interface):
    ...     magicNumber = schema.Int(title=u"Magic number", required=False)

    >>> class TestTile(Tile):
    ...     __name__ = 'test.tile1' # normally set by ZCML handler
    ...
    ...     def __call__(self):
    ...         # fake a page template to keep things simple in the test
    ...         return """\
    ... <html>
    ...     <head>
    ...         <meta name="tile-name" content="%(name)s" />
    ...     </head>
    ...     <body>
    ...         <p>
    ...             This is a demo tile with id %(name)s
    ...         </p>
    ...         <p>
    ...             Magic number: %(number)d; Form: %(form)s; Query string: %(queryString)s; URL: %(url)s
    ...         </p>
    ...     </body>
    ... </html>""" % dict(name=self.id, number=self.data['magicNumber'] or -1,
    ...                   form=sorted(self.request.form.items()), queryString=self.request['QUERY_STRING'], url=self.request.getURL())

Let's add another tile, this time only a head part. This could for example
be a tile that only needs to insert some CSS.

    >>> class TestTileNoBody(Tile):
    ...     __name__ = 'test.tile_nobody'
    ...
    ...     def __call__(self):
    ...         return """\
    ... <html>
    ...     <head>
    ...         <link rel="stylesheet" type="text/css" href="tiled.css" />
    ...     </head>
    ... </html>"""

We register these views and tiles in the same way the ZCML handlers for
``<plone:tile />`` would:

    >>> from plone.tiles.type import TileType
    >>> from Products.Five.security import protectClass
    >>> from App.class_init import InitializeClass
    >>> from zope.component import provideAdapter, provideUtility
    >>> from zope.interface import Interface

    >>> testTileType = TileType(
    ...     name=u'test.tile1',
    ...     title=u"Test tile",
    ...     description=u"A tile used for testing",
    ...     add_permission="cmf.ManagePortal",
    ...     schema=ITestTile)

    >>> testTileTypeNoBody = TileType(
    ...     name=u'test.tile_nobody',
    ...     title=u"Test tile using only a header",
    ...     description=u"Another tile used for testing",
    ...     add_permission="cmf.ManagePortal")

    >>> protectClass(TestTile, 'zope2.View')

    >>> InitializeClass(TestTile)

    >>> provideAdapter(TestTile, (Interface, Interface,), Interface, u'test.tile1',)
    >>> provideAdapter(TestTileNoBody, (Interface, Interface,), Interface, u'test.tile_nobody',)
    >>> provideUtility(testTileType, name=u'test.tile1')
    >>> provideUtility(testTileTypeNoBody, name=u'test.tile_nobody')


Creating a page layout
~~~~~~~~~~~~~~~~~~~~~~

Here, we do something special. Instead of defining a layout that directly
specifies the panel ids to be rendered, we here define a layout _template_
that will be used to generate the concrete layout.

Note the "data-dynamic-tile" attributes below - those will be changed into
"data-tile" attributes to reflect our intended tile assignment.

    >>> pageHTML = """\
    ... <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    ... <html data-layout="./@@default-site-layout">
    ...     <body>
    ...         <h1>Welcome!</h1>
    ...         <div data-panel="panel1">
    ...             <div id="page-tile2" data-dynamic-tile="A">slot A (will become tile2)</div>
    ...         </div>
    ...         <div data-panel="panel2">
    ...             <div id="page-tile3" data-dynamic-tile="B">Slot B (will become tile 3)</div>
    ...         </div>
    ...         <div data-panel="panel4">
    ...             <div id="page-tile4" data-dynamic-tile="X">Slot X (ignored)</div>
    ...         </div>
    ...     </body>
    ... </html>
    ... """

We then register a view that simply return this HTML.

We do this in code for the purposes of the test, and we have to apply security
because we will shortly render those pages using the test publisher. In real
life, these could be registered using the standard ``<browser:page />`` directive.

    >>> from zope.publisher.browser import BrowserView

    >>> class Page(BrowserView):
    ...     __name__ = 'test-page'
    ...     def __call__(self):
    ...         return pageHTML

We register this view in the same way the ZCML handlers for ``<browser:page />`` would:

    >>> from Products.Five.security import protectClass
    >>> from App.class_init import InitializeClass
    >>> from zope.component import provideAdapter, provideUtility
    >>> from zope.interface import Interface

    >>> protectClass(Page, 'zope2.View')

    >>> InitializeClass(Page)

    >>> provideAdapter(Page, (Interface, Interface,), Interface, u'test-page')


Providing a dynamic layout adapter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally we have to provide an adapter that decides which panels should be rendered
into which dynamic panel slot.


Rendering the page
~~~~~~~~~~~~~~~~~~

We can now render the page. Provided ``plone.app.blocks`` is installed and
working, it should perform its magic. We make sure that Zope is in
"development mode" to get pretty-printed output.

    >>> browser.open(portal.absolute_url() + '/@@test-page')
    >>> print browser.contents.replace('<head><meta', '<head>\n\t<meta')
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=ASCII" />
        <title>Layout title</title>
        <link rel="stylesheet" href="/layout/style.css" />
        <script type="text/javascript">alert('layout');</script>
        <style type="text/css">
            div {
                margin: 5px;
                border: dotted black 1px;
                padding: 5px;
            }
            </style>
        <link rel="stylesheet" type="text/css" href="tiled.css" />
        <meta name="tile-name" content="tile2" />
        <meta name="tile-name" content="tile3" />
        <meta name="tile-name" content="tile2" />
      </head>
      <body>
            <h1>Welcome!</h1>
            <div data-panel="panel1">
            <p>
                This is a demo tile with id tile2
            </p>
            <p>
                Magic number: 2; Form: [('magicNumber', 2)]; Query string: magicNumber:int=2; URL: http://nohost/plone/@@test.tile1/tile2
            </p>
            </div>
            <div data-panel="panel2">
            <p>
                This is a demo tile with id tile3
            </p>
            <p>
                Magic number: -1; Form: []; Query string: ; URL: http://nohost/plone/@@test.tile1/tile3
            </p>
            </div>
            <div data-panel="panel3">
                Layout panel 3
            <p>
                This is a demo tile with id tile2
            </p>
            <p>
                Magic number: -1; Form: []; Query string: ; URL: http://nohost/plone/@@test.tile1/tile2
            </p>
            </div>
        </body>
    </html>
    <BLANKLINE>

Notice how:

* Panels from the page have been merged into the layout, replacing the
  corresponding panels there.
* The ``<head />`` sections of the two documents have been merged
* The rest of the layout page is intact
* The rest of the content page is discarded
* The tiles have been rendered, replacing the relevant placeholders
* The ``<head />`` section from the rendered tiles has been merged into the
  ``<head />`` of the output page.

