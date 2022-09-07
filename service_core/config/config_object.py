class Obj(object):
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
               setattr(self, a, [Obj(x) if isinstance(x, dict) else x for x in b])
            else:
               setattr(self, a, Obj(b) if isinstance(b, dict) else b)