class ListWrapper(list):
    def __init__(self, var=[]):
        var[:] = map(ListWrapper.wrap, var)
        super().__init__(var)

    def append(self, elt):
        print("Warning => Mutating List")
        super().append(elt)

    @staticmethod
    def unwrap(var):
        if isinstance(var, ListWrapper):
            var[:] = map(ListWrapper.unwrap, var)
            var = list(var)
        return var

    @staticmethod
    def wrap(var):
        if isinstance(var, list):
            return ListWrapper(var)
        else:
            return var