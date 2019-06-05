======================
django-simple-webpack
======================

A simple webpack bundle loader for Django.


Getting Started
================

Here's how to get django-simple-webpack up and running right away.

Prerequisites
--------------

Before setting up django-simple-webpack, you have to install and, if necessary,
configure, some applications.

* `nodejs <https://nodejs.org/en/>`_
* `webpack <https://webpack.js.org/>`_
* `webpack-bundle-tracker <https://github.com/ezhome/webpack-bundle-tracker>`_

  and of course,

* `Django <https://www.djangoproject.com/>`_

Installation
-------------

Install django-simple-webpack

::

  pip install django-simple-webpack

1. Open your Django settings file. By default that'd be ``settings.py``.

2. Add ``simple_webpack`` to ``installed_apps``.

::

  INSTALLED_APPS = [
    # Standard Django apps here
    'simple_webpack',
  ]

3. Make sure ``STATIC_URL`` is set. By default it is set to:

::

  STATIC_URL = '/static/'


The value of ``publicPath`` in the ``output`` section of your webpack
configuration file, usually named ``webpack.config.js``, and the value of
``STATIC_URL`` in your Django settings should be identical.

3. Add the path to the directory containing your webpack bundles to
   ``STATICFILES_DIRS``. This should be the same path you set for
   ``publicPath`` in the ``output`` section of your webpack config.
   For example, if your webpack config's output section looks like this:

::

  output: {
    filename: '[hash].bundle.js',
    path: path.resolve('./frontend/dist/'),
    publicPath: '/static/',
  }

Then ``STATIC_URL`` and ``STATICFILES_DIRS`` should look like this:

::

  STATIC_URL = '/static/'
  STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'frontend', 'dist'),
  )

If you want Django to serve other files from your frontend along with your
bundles, such as images, fonts, etc., and you keep them all in subdirectories
of a directory named something like ``assets``, you can add the path to
``assets`` to ``STATICFILES_DIRS`` instead.

This works because Django serves all files contained within any directory added
to ``STATICFILES_DIRS``, including any files in any subdirectories of that
directory. In other words, Django recursively searches through any directory
added to ``STATICFILES_DIRS`` and serves any files it finds.

Further explanation of ``STATIC_URL`` and ``STATICFILES_DIRS`` can be found
in `Django's docs`_.

.. _Django's docs: https://docs.djangoproject.com/en/dev/howto/static-files/#configuring-static-files

4. Set ``WEBPACK_STATS_PATH`` to the full path to your webpack-bundle-tracker
output file. The output file is typically named ``webpack-stats.json``. So if
webpack-bundle-tracker is configured in your webpack config file like this:

::

  plugins: [
    new BundleTracker({ filename: './webpack-stats.json' }),
  ],

``WEBPACK_STATS_PATH`` in your Django settings should look like this:

::

  # Simple Webpack
  WEBPACK_STATS_PATH = os.path.join(BASE_DIR, 'webpack-stats.json')

5. Save and close your Django settings file.

Note:
  If you use hot-loading during development, in your Django settings file you
  can set ``WEBPACK_ALLOW_COMPILING`` to an integer from ``1`` to
  ``10``, to allow webpack that number of seconds to finish compiling before
  django-simple-webpack times out. This setting only works if Django setting
  ``DEBUG`` is ```True``. ``WEBPACK_ALLOW_COMPILING`` defaults to ``False``.


Usage
======

Add ``{% load simple_webpack_tags %}`` to the top of any template you need to
load webpack bundles in, on the line directly after the doctype declaration
``<!DOCTYPE html>``.

Add any django-simple-webpack `template tags`_ to your HTML files where you
need them.


Template Tags
==============

If you're unfamiliar with how template tags work in Django, `their docs`_ do
a great job of explaining it.

.. _their docs: https://docs.djangoproject.com/en/dev/topics/templates/#tags

{% simple_webpack_bundle %}  Load a bundle's URL path by chunk/entry name.
{% simple_webpack_static %}  Load a bundle's URL path by filename.
{% simple_webpack_tags %}    Load all bundles as script/link tags.
