============
Spritemapper
============
:Homepage: http://yostudios.github.com/Spritemapper/
:Author: Yo Studios

Spritemapper is an application that merges multiple images into one and generating the CSS positioning for the corresponding slices.

The package consists of a simple cli tool that "does the job", and a python library including its own PNG and CSS parser. The choice of writing/bundling this was to stay off 3rd-party requirements. Users of `Imaging http://www.pythonware.com/products/pil/` on different platforms should have a pretty good idea what we're all about.

There are multiple alternatives to Spritemapper, but most of them requires manual work whereas Spritemapper reads your current css and replaces background-images and position with the generated result. 

This technique drastically improves your website's loading speed by reducing bandwidth on downloading multiple images. 

Spritemapper in action
----------------------
Here's a simple example illustrating what Spritemapper will do with your CSS:
.. code-block:: css

   .emote.smile {
     background: red url(../img/sprites/emoticons/smile.png) no-repeat;
   }
   .emote.grin {
     background: white url(../img/sprites/emoticons/grin.png) no-repeat;
   }

..will turn into:

.. code-block:: css

   .emote.smile {
     background: red url(../img/spritemaps/emoticons.png) no-repeat 0 0;
   }
   .emote.grin {
     background: white url(../img/spritemaps/emoticons.png) no-repeat 0 -16px;
   }

Usage
-----
.. code-block::
# spritemapper -h
Usage: spritemapper [opts] <css file(s) ...>

Options:
  -h, --help          show this help message and exit
  -c INI, --conf=INI  read base configuration from INI
  --padding=N         have N pixels of padding between sprites
  --in-memory         keep CSS parsing results in memory
  --anneal=N          simulated anneal steps (default: 9200)


Configuration options
---------------------

Running tests
-------------
The test suite requires `Nose http://somethingaboutorange.com/mrl/projects/nose/`. Run it through setup.py: `python setup.py test` or call `nosetests`.
