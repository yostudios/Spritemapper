==============
 Spritemapper 
==============

:Homepage: http://yostudios.github.com/Spritemapper/
:Authors: Yo Studios <opensource@yostudios.se>

Spritemapper is an application that merges multiple images into one and
generating the CSS positioning for the corresponding slices.

The package consists of a simple command-line tool that "does the job", and a
Python library including its own PNG and CSS parser. The choice of
writing/bundling this was to stay off 3rd-party requirements. Anybody who has
ever had the pleasant job of installing PIL__ on various platforms should have
a pretty good idea about what we're trying to avoid.

__ http://www.pythonware.com/products/pil/

There are multiple alternatives to Spritemapper, but they all require a bit too
much manual labour, whereas Spritemapper reads your current CSS and replaces
background images and position with the generated result. 

This technique drastically improves your website's loading speed by reducing
bandwidth on downloading multiple images. 

Spritemapper in action
----------------------

Here's a simple example illustrating what Spritemapper will do with your CSS:

.. code-block:: css

   .emote.smile {
     background: red url(../img/emoticons/smile.png) no-repeat;
   }
   .emote.grin {
     background: white url(../img/emoticons/grin.png) no-repeat;
   }

... turns into:

.. code-block:: css

   .emote.smile {
     background: red url(../img/emoticons.png) no-repeat 0 0;
   }
   .emote.grin {
     background: white url(../img/emoticons.png) no-repeat 0 -16px;
   }

Usage
-----

``-h``, ``--help``
    show a help message and exit

``-c INI``, ``--conf=INI``
    read base configuration from INI (see `Configuration options`_)

``--padding=N``
    keep N pixels of padding between sprites

Configuration options
---------------------

Configuration options can be specified in one of two ways: inline in the CSS,
*or* using passing an INI file with defaults. For CSS it looks something like:

.. code-block:: css

   /* spritemapper.output_css = foofile.css

You can do the exact equivalent using an INI file, like this:

.. code-block:: ini

   [spritemapper]
   output_css = foofile.css

It's important to note that all paths are relative to the CSS file being
processed.

.. _opt_ref:

``base_url``
    a url at which the resulting css and image files can be reached.  
    by default uses file-relative paths (recommended).

``sprite_dirs``
    a list of directories within which to allow spritemaps to be generated.  
    by default all directories are eligible.

``recursive``
    set if sub-spritemaps should be generated when sub-directories are found.
    set by default.

``output_image``
    the name of output spritemap image.
    ``sprite_dirs`` is incompatible with this because both tell the
    spritemapper how to sort sprites into spritemaps.
    by default *<dir>* + ``.png``.

``output_css``
    the name for the rewritten CSS file.
    by default ``sm_{basename}{extension}``.

``padding``
    amount of padding space between two images. this is mostly useful to
    counteract subpixel rendering artifacts on iOS devices.
    by default 1.

``anneal_steps``
    a larger number here makes the box packer algorithm try more combinations.
    by default 9200.

Running tests
-------------

The test suite requires Nose__. You can run it through setup.py with ``python
setup.py test`` or just ``nosetests``.

__ http://somethingaboutorange.com/mrl/projects/nose/
