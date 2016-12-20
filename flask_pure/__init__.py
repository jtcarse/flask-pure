# -*- coding: utf-8 -*-
# Copyright (c) 2016, Philip Xu <pyx@xrefactor.com> and contributors.
# See AUTHORS for more details.
# License: BSD New, see LICENSE for details.
"""Flask-Pure - a Flask extension for Pure.css"""

from flask import Blueprint, Markup, current_app, url_for

__version__ = '0.4.dev0'
__all__ = ['Pure']

LINK_TEMPLATE = (
    '<link rel="stylesheet" href="{URI}" '
    'integrity="{HASH}" crossorigin="anonymous">')

PURE_VERSION = '0.6.1'

# SRI hash (without prefix 'sha384-') can be generated with:
# cat CSS_FILE | openssl dgst -sha384 -binary | openssl enc -base64 -A
SRI_HASH = {
    'pure.css':
    'sha384-QBtdI61Wy+ikCpWa4q1qr13NIcHPZ54RQOKg9pjUVmuG0IWd5u5el/Md3Kdr8Bts',

    'pure-min.css':
    'sha384-CCTZv2q9I9m3UOxRLaJneXrrqKwUNOzZ6NGEUMwHtShDJ+nCoiXJCAgi05KfkLGY',

    'grids-responsive.css':
    'sha384-p3KDYWuAiuJGRrYoXWvd9rCsP0Qn4B/hOJEF/6s+aJ/b7b0bFXhKYhxDJJecys7v',

    'grids-responsive-min.css':
    'sha384-XFOTHpTomywMwwGi19rYAmPxQVsd5yzo5Hmx37ZfFQgXj+v9UnjfCvaS7B7WRWyp',
}

# CDN hosts as listed on http://purecss.io/
HOST = {
    'unpkg': 'https://unpkg.com/purecss@{VERSION}/build/{FILENAME}',
    'cdnjs': '//cdnjs.cloudflare.com/ajax/libs/pure/{VERSION}/{FILENAME}',
    'jsdelivr': '//cdn.jsdelivr.net/pure/{VERSION}/{FILENAME}',
    'keycdn': '//opensource.keycdn.com/pure/{VERSION}/{FILENAME}',
    'maxcdn': '//oss.maxcdn.com/libs/pure/{VERSION}/{FILENAME}',
    'rawgit': '//cdn.rawgit.com/yahoo/pure-release/v{VERSION}/{FILENAME}',
    'staticfile': 'http://cdn.staticfile.org/pure/{VERSION}/{FILENAME}',
}


class Pure(object):
    """Flask-Pure extension

    provides base template layout as :code:`pure/layout.html` and links to the
    Pure.css static assets.
    """
    def __init__(self, app=None):
        self.app = app

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """create and register a blueprint with the Flask application.

        :param app:
            Flask application instance
        """
        app.config.setdefault('PURECSS_RESPONSIVE_GRIDS', True)
        app.config.setdefault('PURECSS_USE_CDN', True)
        app.config.setdefault('PURECSS_CDN', 'unpkg')
        app.config.setdefault('PURECSS_USE_MINIFIED', True)

        pure = Blueprint(
            'pure',
            __name__,
            template_folder='templates',
            static_folder='static',
            static_url_path=app.static_url_path + '/pure/css')

        app.register_blueprint(pure)

        if not hasattr(app, 'extensions'):
            app.extensions = {}

        app.extensions['pure'] = self
        app.context_processor(lambda: {'pure': self})

    @property
    def css(self):
        """property the will be rendered as Pure.css :code:`<link>` tags"""
        stylesheets = ['pure']

        if current_app.config['PURECSS_RESPONSIVE_GRIDS']:
            stylesheets.append('grids-responsive')

        if current_app.config['PURECSS_USE_MINIFIED']:
            stylesheets = [ss + '-min' for ss in stylesheets]

        stylesheets = [ss + '.css' for ss in stylesheets]

        if current_app.config['PURECSS_USE_CDN']:
            host_tpl = HOST[current_app.config['PURECSS_CDN']]
            stylesheets = [
                (ss, host_tpl.format(VERSION=PURE_VERSION, FILENAME=ss))
                for ss in stylesheets]
        else:
            stylesheets = [
                (ss, url_for('pure.static', filename=ss))
                for ss in stylesheets]

        link = '\n'.join(
            LINK_TEMPLATE.format(URI=uri, HASH=SRI_HASH[ss])
            for ss, uri in stylesheets)

        return Markup(link)
