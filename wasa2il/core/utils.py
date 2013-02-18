

class AttrDict(dict):
	__getattr__ = dict.__getitem__

	def __setattr__(self, key, value):
		self[key] = value
