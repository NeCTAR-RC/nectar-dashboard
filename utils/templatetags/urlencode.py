from django import template

import urllib

register = template.Library()

class URLEncodeNode(template.Node):

    def __init__(self, nodes, plus=False):
        self.nodes = nodes
        self.plus = plus

    def render(self, context):
        src = self.nodes.render(context).strip()
        if self.plus:
            return urllib.quote_plus(src)
        return urllib.quote(src)

@register.tag
def urlencode(parser, token):
    """ Encodes the contents for safe use as a GET parameter value. """
    args = token.contents.split()
    nodes = parser.parse(('endurlencode',))
    parser.delete_first_token()
    return URLEncodeNode(nodes, plus='plus' in args)
