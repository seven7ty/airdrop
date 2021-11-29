from typing import TypeVar


__all__: tuple = ('EthereumAddress', 'TxHash')

EthereumAddress: TypeVar = TypeVar('EthereumAddress', str, bytes)
TxHash: TypeVar = TypeVar('TxHash', str, bytes)
