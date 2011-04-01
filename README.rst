===================
 CSS Spritemapping 
===================

The problem is an all too common one to not have been solved once and for all:
the problem is that of using sprites on the web.

What *is* this problem, wherefore are sprites a problem? Well, the answer is
mainly HTTP itself. Big players like Google recognize this problem as well and
Google have suggested a new protocol to be the remedy: SPDY, or "speedy".

We're not holding our breath on that one -- Google's Chrome browser has support
for it from what I hear, but until it gains some traction let's leave it aside.

Spritemaps
==========

Clearly the most worthwhile technological change to make is using spritemaps,
and building them yourself is just not fun or feasible for any sort of
self-respecting Web engineer.

Spritemaps are fairly intrusive when it comes to the technological bit because
CSS has to be parsed and then modified, and maps have to be built. Not an easy
thing to do.

Earlier efforts
---------------

We've previously modified CleverCSS__ to be able to build spritemaps, work
which you can check out on `lericson's GitHub fork of CleverCSS`__.

__ http://sandbox.pocoo.org/clevercss/
__ https://github.com/lericson/clevercss/tree/spritemap

This worked very well; in fact it's what `yo.se`__ uses to this day. The
problem with this approach is that it's extremely intrusive. We already used
CleverCSS for its awesomely clever CSS powers, so that move made sense at the
time.

__ http://yo.se/

A simple approach
-----------------

After extensive arguing with my frontend guy `Johan Nordberg`__, we came up
with a simple yet elegant solution -- without further ado, some CSS:

__ http://johan-nordberg.com/

.. code-block:: css

   .emote.smile {
     background: red url(../img/sprites/emoticons/smile.png) no-repeat;
   }
   .emote.grin {
     background: white url(../img/sprites/emoticons/grin.png) no-repeat;
   }

You can probably see where I'm going with this: our approach is to parse the
CSS as CSS, and look at the paths to determine what should be spritemapped and
what shouldn't.

It's important to understand that not everything can be spritemapped. It would
be an error to specify X or Y offsets in the above background attributes.

An example of the output for the above document could be:

.. code-block:: css

   .emote.smile {
     background: red url(../img/spritemaps/emoticons.png) no-repeat 0 0;
   }
   .emote.grin {
     background: white url(../img/spritemaps/emoticons.png) no-repeat 0 -16px;
   }

Usage etc
==========

TODO
