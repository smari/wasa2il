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


def real_strip_tags(content, open_tag='<', close_tag='>'):

    s = content

    search_start = 0
    index_start = s.find(open_tag, search_start)
    while index_start > -1:

        index_end = s.find(close_tag, index_start)
        if index_end > -1:
            s = s[0:index_start] + s[index_end+len(close_tag):]

        search_start = index_start
        index_start = s.find(open_tag, search_start)

    return s


class AttrDict(dict):
    __getattr__ = dict.__getitem__

    def __setattr__(self, key, value):
        self[key] = value
