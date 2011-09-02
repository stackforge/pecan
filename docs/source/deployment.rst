.. _deployment:

Deploying Pecan projects
========================
Deploying a pecan project can be accomplished in several ways. You may
already be familiar with deployment methodologies for other Python
projects, in which case, try that! Pecan doesn't deviate from the
standards laid out by similar Python web frameworks before it.

Here we will outline some of the common methods for deploying your Pecan
project.

Good ol' fashioned source control.
-----------------------------------

Why not? It works! In our modern world of distributed SCM tools, we find
using source control as a completely acceptable method for deployment.
Sure it's a bit more manual than you might like, but it gets the job
done, and rollbacks are free (if you're into that kind of thing ;)). For
this guide, it is assumed you are developing your application in a git
repository.

Here are some tips, free of charge::

  * Develop on "feature" branches.
  * All merge back to "master" when sprint is complete.
  * Tag "release" branches.

To setup::

  * git clone <project> /opt/project/
  * git branch --track <release_branch> origin/<release_branch>
  * git checkout <release_branch>
  * python setup.py install

To deploy going forward::

  * cd /opt/project/
  * git pull
  * git branch --track <release_branch> origin/<release_branch>
  * git checkout <release_branch>
  * python setup.py install

That should do it.

Fabric
------

Fabric makes it way more fun to deploy. You can write straight up python
to automate the SCM deployments, or even go so far as to build a full fledged
release system with it.

Capistrono
----------

Much like fabric, but they built in some out of the box deployment
tools. We'll cover that here.

Chef
----

Chef borrows it's deployment methodologies from Capistrono, we'll cover
that here.

Whiskey Disk
------------

The embarrassingly fast deployment tool. Decoupled from frameworks, one
specific design goal, to deploy quickly and easily. YAML configuration.

Egg
---

Deploy binary packages using python's distribution utilities.

RPM
---

Deploy your apps with RPM's, built with python's distribution utilities.

