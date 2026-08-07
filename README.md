==============================
SIMPLE 4.0 plugin for Scipion3
==============================

 This plugin allows to use SIMPLE programs within the Scipion framework.

 SIMPLE is a a program package for cryo-EM image processing, focusing on ab initio 3D reconstruction of low-symmetry single-particles. It is developed at the [Hans Elmlund](https://hael.github.io/SIMPLE) lab.

 ## Available protocols
 * **abinitio2D**: Classifies particles into multiple 2D classes to facilitate stack cleaning and removal of junk particles. Determines the required parameters for the rest of the SIMPLE workflow: downsampling, sampling scheme, classes...
  * **symmetry_test**: Helps looking for the point group or symmetry of your particles. Recommended to run after abinitio2D.
 * **abinitio3D**: Allows generating an ab-initio reconstruction from classified particles or 2D averages. Uses the newly developed nonuniform refinement and the polar Fourier geometric approach for reconstruction. Requires a prior abinitio2D execution.
 * **refine3D**: Allows to launch the classic SIMPLE refinement or the newly developed nonuniform refinement over your map and angle-containing particles.

**Latest plugin version**
==========================

**v4.0.0**
----------
* **updated**       Add support for SIMPLE 4.0.0
* **deprecation**   Remove older 2D&3D cluster protocols, as well as Movie Unblur and old 3D refinement
* **new**           Add support for the new 2026 abinitio2D, abinitio3D and refine3D with polar Fourier and the new nonuniform particle refinement

 Supported versions of SIMPLE: 4.0.0

**Installing the plugin**
=========================

In order to install the plugin follow these instructions:

**Install the plugin in production mode**

.. code-block::

     scipion installp -p scipion-em-simple

or through the **plugin manager** by launching Scipion and following **Configuration** >> **Plugins**

**To install in development mode**

- Clone or download the plugin repository

.. code-block::

          git clone https://github.com/scipion-em/scipion-em-simple.git

- Install the plugin in developer mode.

.. code-block::

  scipion installp -p local/path/to/scipion-em-simple --devel

===============
Buildbot status
===============

Status devel version:

.. image:: http://scipion-test.cnb.csic.es:9980/badges/simple_devel.svg

Status production version:

.. image:: http://scipion-test.cnb.csic.es:9980/badges/simple_prod.svg
