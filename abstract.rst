========================
 Pure CSS Spritemapping 
========================

The problem is an all too common one to not have been solved once and for all:
the problem is that of using sprites on the web.

What *is* this problem, wherefore are sprites a problem? Well, the answer is
mainly HTTP itself. Big players like Google recognize this problem as well and
Google have suggested a new protocol to be the remedy: SPDY, or "speedy".

I'm not holding my breath on that one -- Google's Chrome browser has support
for it from what I hear, but until it gains some traction let's leave it aside.

Methods
=======

There are a number of other solutions to this problem that are more portable
and hence usable, so in order of perceived prevalence:

1. Compiling, by hand or automation, a large image and then referring to
   offsets into the image space via browser support for CSS.

   - Allows any raster graphics of any size
   - Requires the graphics be rasterized
   - Requires some amount of book-keeping on where the sprites within the
     spritemap reside
   - Requires the ability to offset into the image space
   - Requires a build phase where sprites are extracted, packed and
     rereferenced from the stylesheet

2. Compiling "web fonts" with glyphs that are actually vectorized visual
   elements on the site (limited applicability)

   - Allows any vector graphics
   - Allows text effects to be applied
   - Requires the graphics be vectorized
   - Requires some amount of book-keeping on which codepoint corresponds to
     what symbol
   - Requires fancy web font support
   - Requires a build phase
   - Requires some degree of hand-tooling; much harder to automate
   - Requires that the image be single-color

3. Compiling HTML5 manifests with each resource named therein

   - Allows anything the browser can handle, very flexible
   - Completely eliminates request overhead when cached
   - Conversely also requires a request per resource when uncached

As for anything that aims to reduce the request-response loop latency, the best
outcome is to not need to ask any questions at all. We therefore segue into the
realm of HTTP caching.

HTML5 manifests are basically listings of resources to be cached, coupled with
a JavaScript API that tells you what's cached, what isn't and what's undergoing
caching.

Conditions
==========

So, to get some kind of comparison going, I think we have three cases we need
to examine in each condition:

1. What happens when a newly installed browser visits the site?

2. What happens when a regular users visits the site?

3. What happens when a user visits the site after the static content has been
   updated?

So we'll imagine a site like `yo.se`__ - suppose it has 25 site-wide sprites,
and 5 frontpage-specific sprites.

__ http://yo.se/

Comparison
==========

1. For the case of just using ``background: url(sprites/banner.png);``, we'll
   then get 30 requests for type 1 visitors, of which 100% will transfer data.
   For type 2 visitors, we'll still get 30 requests, but the amount of data
   depends on how well we formulate caching headers - ideally 0% will transfer
   data and instead say "not modified". (Types 3 and 1 behave the same.)

2. For the case of building spritemaps out of the images and referring to
   offsets like ``background: url(sprites/banner.png) 24px 32px;`` the
   situation is much better in terms of request cycles: at most 2 requests. The
   boost is huge, for some definitions of the term.

3. But what of the case with HTML5 manifests? HTML5 manifests are designed to
   allow Web applications to function offline. It's helpful, because it allows
   you to tell the browser not to even bother re-requesting a resource.

   Thus, with HTML5 manifests alone there will be 31 requests on the frontpage
   for type 1 visitors -- one for the manifest itself, plus the 30 sprites.
   Type 2 visitors, however, will only have to request the manifest! The
   browser goes by the logics of 'if the manifest hasn't changed, neither has
   any of the resources it labels "cache"'.

   We can improve this situation by combining method 2 and 3: spritemaps named
   by an HTML5 manifest. This means we'll have 3 requests, then 1. (Not to
   mention that the HTML5 manifest can name CSS sheets, JavaScripts, Flash
   objects, etc.)

Whether or not HTML5 manifests are worthwhile pursuit is often a case-by-case
scenario -- much like SPDY, it suffers from the problem that the technology is
very new and so not widely available, and more importantly gives the users a
mixed experience of the site: Mozilla Firefox will for example give the user a
frightening question along the lines of "do you want to allow this site to
store data on your computer?" I hope the Firefox team fix that obvious UI bug,
but I digress.

Spritemaps
==========

Clearly the most worthwhile technological change to make is using spritemaps,
and building them yourself is just not doable for any sort of self-respecting
Web engineer.

Spritemaps are fairly intrusive when it comes to the technological bit because
CSS has to be parsed and then modified, and maps have to be built. A challenge
for an engineer.

Earlier efforts
---------------

I've previously modified CleverCSS__ to be able to build spritemaps, work which
you can check out on `my GitHub fork of CleverCSS`__.

__ http://sandbox.pocoo.org/clevercss/
__ https://github.com/lericson/clevercss/tree/spritemap

This worked very well; in fact it's what `yo.se`__ uses to this day. The
problem with this approach is that it's extremely intrusive: we already used
CleverCSS for its awesomely clever CSS powers, so that move made sense at the
time.

__ http://yo.se/

A pure approach
---------------

After extensive arguing with my frontend guy, friend and roomie `Johan
Nordberg`__, we came up with a simple yet elegant solution -- without further
ado, some CSS:

__ http://johan-nordberg.com/

.. code-block:: css

   .emote.smile {
     background: url(../img/sprites/emoticons/smile.png) no-repeat;
   }
   .emote.grin {
     background: url(../img/sprites/emoticons/grin.png) no-repeat;
   }

You can probably see where I'm going with this: our approach is to parse the
CSS as CSS, and look at the paths to determine what should be spritemapped and
what shouldn't. It's important to understand that not everything can be
spritemapped: it would be an error to specify X or Y offsets in the above
background attributes.

.. code-block:: css

   .emote.smile {
     background: red url(../img/spritemaps/emoticons.png) no-repeat 0 0;
   }
   .emote.grin {
     background: white url(../img/spritemaps/emoticons.png) no-repeat -16px -16px;
   }
