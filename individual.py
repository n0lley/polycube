class INDIVIDUAL:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError

    def mutate(self, *args, **kwargs):
        raise NotImplementedError

    def evaluate(self, *args, **kwargs):
        raise NotImplementedError