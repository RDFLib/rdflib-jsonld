"""
"""
__version__ = "0.1"

def registerplugins():
    """
    If rdflib-jsonld is installed with setuptools, all plugins are registered
    through entry_points. This is strongly recommended. 

    If only distutils is available, the plugins must be registed manually
    This method will register the json-ld plugins

    """
    from rdflib import plugin
    from rdflib.parser import Parser
    from rdflib.serializer import Serializer

    try:
        x=plugin.get('json-ld',Parser)
        return # plugins already registered
    except:
        pass # must register plugins    


    plugin.register('json-ld', Parser,
        'rdfextras.parsers.jsonld', 'JsonLDParser')
    plugin.register('json-ld', Serializer,
        'rdfextras.serializers.jsonld', 'JsonLDSerializer')
