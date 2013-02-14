class test(list):

    @classmethod
    def get_class(cls):
        return cls

    def __init__(self, x):
        self.x = 5
        list.__init__(self, x)

    @classmethod
    def alternate(cls, it):
        return cls(it)
