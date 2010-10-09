.. _app_engine:

App Engine Support
=========================

Pecan runs smoothly in Google's App Engine. There is **no** hacking/patching or weird 
changes that you need to make to work with Pecan. However, since App Engine has certain 
restrictions you may want to be aware of how to set it up correctly.


Dependencies
---------------
Pecan has a few dependencies and one of them is already supported by App Engine (WebOb)
so no need to grab that. Just so you are aware, this is the list of things that you absolutely need 
to grab:

 *  simplegeneric >= 0.7",
 *  Paste >= 1.7.5.1",

These are optional, depending on the templating engine you want to use. However, depending on your choice,
you might want to check the engine's dependencies as well. The only engine from this list that doesn't require 
a dependency is Kajiki.

 *  Genshi >= 0.6
 *  Kajiki >= 0.2.2
 *  Mako >= 0.3
 
