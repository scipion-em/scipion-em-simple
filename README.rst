=============
Simple plugin
=============

This plugin allows to use Simple programs within the Scipion framework.

Simple is a a program package for cryo-EM image processing, focusing on ab initio 3D reconstruction of low-symmetry single-particles. It is developed by [Hans Elmlund](http://simplecryoem.com).

Supported versions of Simple: 2.1
 
- **Dependencies**

 We need libgfortran3
 
.. code-block::

   sudo apt install libgfortran3

=====
Setup
=====

- **Install this plugin:**

.. code-block::

    scipion installp -p scipion-em-simple

OR

  - through the plugin manager GUI by launching Scipion and following **Configuration** >> **Plugins**

Alternatively, in devel mode:

.. code-block::

    scipion installp -p local/path/to/scipion-em-simple --devel

![build status](http://heisenberg.cnb.csic.es:9980/badges/simple_devel.svg)

