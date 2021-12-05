__all__: tuple = ('shorten_address',)


def shorten_address(address: str) -> str:
    """
    Shorten an address by trimming off 60% and inserting "..." in the middle.
    :param address: The address to shorten
    :return: The shortened address
    """

    chunk: int = int(len(address) / 5)
    return f'{address[:chunk]}...{address[-chunk:]}'
