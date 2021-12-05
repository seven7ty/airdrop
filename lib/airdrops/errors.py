__all__: tuple = ('AirdropNotFound', 'AirdropEnded')


class AirdropNotFound(Exception):
    pass


class AirdropEnded(Exception):
    pass
