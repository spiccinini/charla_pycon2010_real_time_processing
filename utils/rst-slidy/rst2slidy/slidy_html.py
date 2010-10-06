# $Id: __init__.py 4883 2007-01-16 01:51:28Z wiemann $
# Authors: Nathan Yergler <nathan@yergler.net>;
#          Chris Liechti <cliechti@gmx.net>;
#          David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Slidy XHTML Slideshow Writer.
"""

__docformat__ = 'reStructuredText'


import sys
import os
import re
import docutils
from docutils import frontend, nodes, utils
from docutils.writers import html4css1
from docutils.parsers.rst import directives

import rst_directive


themes_dir_path = utils.relative_path(
    os.path.join(os.getcwd(), 'dummy'),
    os.path.join(os.path.dirname(__file__), 'themes'))

def find_theme(name):
    # Where else to look for a theme?
    # Check working dir?  Destination dir?  Config dir?  Plugins dir?
    path = os.path.join(themes_dir_path, name)
    if not os.path.isdir(path):
        raise docutils.ApplicationError(
            'Theme directory not found: %r (path: %r)' % (name, path))
    return path


class Writer(html4css1.Writer):

    settings_spec = html4css1.Writer.settings_spec + (
        'Slidy Slideshow Specific Options',
        'For the Slidy/XHTML writer, the --no-toc-backlinks option '
        '(defined in General Docutils Options above) is the default, '
        'and should not be changed.',
        (
            ('Allow Slidy and theme files in the destination directory to be '
             'overwritten.  The default is not to overwrite theme files.',
             ['--overwrite-theme-files'],
             {'action': 'store_true', 'validator': frontend.validate_boolean}),

            ))

    settings_default_overrides = {'toc_backlinks': 0}

    config_section = 'slidy_xhtml writer'
    config_section_dependencies = ('writers', 'html4css1 writer')

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = SlidyXHTMLTranslator


class SlidyXHTMLTranslator(html4css1.HTMLTranslator):

    slidy_stylesheet_template = """\
<!-- Slidy links -->
<link rel="stylesheet" href="%(path)s/style/slidy.css"
      type="text/css" media="screen, projection, print" />
<link rel="stylesheet" href="%(path)s/style/slidy-theme.css"
      type="text/css" media="screen, projection, print" />
<script src="%(path)s/style/slidy.js" type="text/javascript"></script>
\n"""

    pygmentize_sylesheet = """\
<link rel="stylesheet" href="style/pygments-style.css"
      type="text/css" media="screen, projection, print" />
\n"""

    disable_current_slide = """
<style type="text/css">
#currentSlide {display: none;}
</style>\n"""

    layout_template = """\
<div class="layout">
<div id="controls"></div>
<div id="currentSlide"></div>
<div id="header">
%(header)s
</div>
<div id="footer">
%(title)s%(footer)s
</div>
</div>\n"""
# <div class="topleft"></div>
# <div class="topright"></div>
# <div class="bottomleft"></div>
# <div class="bottomright"></div>

    #default_theme = 'default'
    #"""Name of the default theme."""

    #base_theme_file = '__base__'
    #"""Name of the file containing the name of the base theme."""

    direct_theme_files = (
        'slidy.css', 'slidy.js')
    """Names of theme files directly linked to in the output HTML"""

    #indirect_theme_files = (
    #    's5-core.css', 'framing.css', 'pretty.css', 'blank.gif', 'iepngfix.htc')
    #"""Names of files used indirectly; imported or used by files in
    #`direct_theme_files`."""

    required_theme_files = direct_theme_files
    """Names of mandatory theme files."""
    #required_theme_files = indirect_theme_files + direct_theme_files

    def __init__(self, *args):
        html4css1.HTMLTranslator.__init__(self, *args)

        #insert Slidy stylesheet and scripts
        self.theme_file_path = '.'
        self.setup_theme()

        self.stylesheet.append(self.slidy_stylesheet_template
                               % {'path': self.theme_file_path})
        self.stylesheet.append(self.pygmentize_sylesheet)

        # self.add_meta('<meta name="version" content="S5 1.1" />\n')
        self.s5_footer = []
        self.s5_header = []
        self.section_count = 0
        self.theme_files_copied = None

    def setup_theme(self):
        #if self.document.settings.theme:
        self.copy_theme()
        #elif self.document.settings.theme_url:
        #    self.theme_file_path = self.document.settings.theme_url
        #else:
        #    raise docutils.ApplicationError(
        #        'No theme specified for S5/HTML writer.')

    def copy_theme(self):
        """
        Locate & copy theme files.

        A theme may be explicitly based on another theme via a '__base__'
        file.  The default base theme is 'default'.  Files are accumulated
        from the specified theme, any base themes, and 'default'.
        """

        settings = self.document.settings
        # path = find_theme(settings.theme)
        path = os.path.join(os.path.dirname(__file__), 'slidy')
        theme_paths = [path]
        self.theme_files_copied = {}
        required_files_copied = {}
        # This is a link (URL) in HTML, so we use "/", not os.sep:
        # self.theme_file_path = '%s/%s' % ('ui', settings.theme)
        if settings._destination:
            settings._destination = os.path.abspath(settings._destination)

            dest_dir = os.path.dirname(settings._destination)

            if not os.path.isdir(dest_dir):
                os.makedirs(dest_dir)

        else:
            # no destination, so we can't copy the theme
            return
        # default = 0
        while path:
            for f in os.listdir(path):  # copy all files from each theme
                if ( self.copy_file(f, path, dest_dir)
                     and f in self.required_theme_files):
                    required_files_copied[f] = 1

            # XXX no theme support yet
            path = None

            #if default:
            #    break                   # "default" theme has no base theme
            #    path = find_theme(self.default_theme)
            #    theme_paths.append(path)
            #    default = 1


        if len(required_files_copied) != len(self.required_theme_files):
            # Some required files weren't found & couldn't be copied.
            required = list(self.required_theme_files)
            for f in required_files_copied.keys():
                required.remove(f)
            raise docutils.ApplicationError(
                'Theme files not found: %s'
                % ', '.join(['%r' % f for f in required]))

    files_to_skip_pattern = re.compile(r'~$|\.bak$|#$|\.cvsignore$')

    def copy_file(self, name, source_dir, dest_dir):
        """
        Copy file `name` from `source_dir` to `dest_dir`.
        Return 1 if the file exists in either `source_dir` or `dest_dir`.
        """
        source = os.path.join(source_dir, name)
        dest = os.path.join(dest_dir, name)
        if self.theme_files_copied.has_key(dest):
            return 1
        else:
            self.theme_files_copied[dest] = 1
        if os.path.isfile(source):
            if self.files_to_skip_pattern.search(source):
                return None
            settings = self.document.settings
            if os.path.exists(dest) and not settings.overwrite_theme_files:
                settings.record_dependencies.add(dest)
            else:
                src_file = open(source, 'rb')
                src_data = src_file.read()
                src_file.close()
                dest_file = open(dest, 'wb')
                dest_dir = dest_dir.replace(os.sep, '/')
                dest_file.write(src_data.replace(
                    'ui/default', dest_dir[dest_dir.rfind('ui/'):]))
                dest_file.close()
                settings.record_dependencies.add(source)
            return 1
        if os.path.isfile(dest):
            return 1

    def depart_document(self, node):
        header = ''.join(self.s5_header)
        footer = ''.join(self.s5_footer)
        title = ''.join(self.html_title).replace('<h1 class="title">', '<h1>')
        layout = self.layout_template % {'header': header,
                                         'title': title,
                                         'footer': footer}
        self.fragment.extend(self.body)
        # self.body_prefix.extend(layout)
        #self.body_prefix.append('<div class="presentation">\n')
        self.body_prefix.append(
        """\
<div class="background"><img alt="" id="head-icon"
src="style/icon-blue.png" /><object id="head-logo"
data="style/w3c-logo-white.svg" type="image/svg+xml"
title="W3C logo"><a href="http://www.w3.org/"><img
alt="W3C logo" id="head-logo-fallback"
src="style/w3c-logo-white.gif" /></a></object></div>

<div class="background slanty">
<img src="style/w3c-logo-slanted.jpg" alt="Logo" />
</div>
""")
        self.body_prefix.append(
            self.starttag({'classes': ['slide'], 'ids': ['slide0']}, 'div'))
        if not self.section_count:
            self.body.append('</div>\n')
        #self.body_suffix.insert(0, '</div>\n')
        # skip content-type meta tag with interpolated charset value:
        self.html_head.extend(self.head[1:])
        self.html_body.extend(self.body_prefix[1:] + self.body_pre_docinfo
                              + self.docinfo + self.body
                              + self.body_suffix[:-1])

    def depart_footer(self, node):
        start = self.context.pop()
        self.s5_footer.append('<h2>')
        self.s5_footer.extend(self.body[start:])
        self.s5_footer.append('</h2>')
        del self.body[start:]

    def depart_header(self, node):
        start = self.context.pop()
        header = ['<div id="header">\n']
        header.extend(self.body[start:])
        header.append('\n</div>\n')
        del self.body[start:]
        self.s5_header.extend(header)

    def visit_section(self, node):
        if not self.section_count:
            self.body.append('\n</div>\n')
        self.section_count += 1
        self.section_level += 1
        if self.section_level > 1:
            # dummy for matching div's
            self.body.append(self.starttag(node, 'div', CLASS='section'))
        else:
            self.body.append(self.starttag(node, 'div', CLASS='slide'))

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.section):
            level = self.section_level + self.initial_header_level - 1
            if level == 1:
                level = 2
            tag = 'h%s' % level
            self.body.append(self.starttag(node, tag, ''))
            self.context.append('</%s>\n' % tag)
        else:
            html4css1.HTMLTranslator.visit_subtitle(self, node)

    def visit_title(self, node):
        html4css1.HTMLTranslator.visit_title(self, node)
