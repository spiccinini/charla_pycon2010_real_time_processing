
try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from docutils.core import publish_cmdline, default_description
import slidy_html

def main():
    """Command line interface for rst2slidy."""
    
    description = ('Generates Slidy XHTML slideshow documents from standalone '
                   'reStructuredText sources.  ' + default_description)

    publish_cmdline(writer=slidy_html.Writer(), description=description)

