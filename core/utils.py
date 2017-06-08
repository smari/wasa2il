from HTMLParser import HTMLParser

#class MLStripper(HTMLParser):
#    def __init__(self):
#        self.reset()
#        self.fed = []
#    def handle_data(self, d):
#        self.fed.append(d)
#    def get_data(self):
#        return ''.join(self.fed)
#
#def strip_tags(html):
#    s = MLStripper()
#    s.feed(html)
#    return s.get_data()


class AttrDict(dict):
    __getattr__ = dict.__getitem__

    def __setattr__(self, key, value):
        self[key] = value
