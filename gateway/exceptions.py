class IcePirateException(Exception):
    def __init__(self, msg, sub_msg=None, *args, **kwargs):
        self.sub_msg = sub_msg
        super(IcePirateException, self).__init__(msg, *args, **kwargs)
