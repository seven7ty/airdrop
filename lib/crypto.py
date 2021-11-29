import asyncio
import functools
import concurrent.futures
from web3 import Web3
from typing import Union
from . import CONFIG
from .types import TxHash, EthereumAddress

__all__: tuple = ('CRYPTO',)


class _Crypto:
    def __init__(self):
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.testnet: bool = CONFIG.use_testnet
        self.rpc_url: str = CONFIG.mainnet_rpc_url if not self.testnet else CONFIG.testnet_rpc_url
        self.contract_address: EthereumAddress = (CONFIG.mainnet_contract_address if not
                                                  self.testnet else CONFIG.testnet_contract_address)
        self.w3: Web3 = Web3(provider=Web3.HTTPProvider(self.rpc_url))
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.contract = None

    def _run_in_executor(self, func):
        return self.loop.run_in_executor(self.executor, func)

    def _set_contract(self):
        self.contract = self.w3.eth.contract(self.w3.toChecksumAddress(self.contract_address), abi=CONFIG.abi)

    async def setup(self):
        await self._run_in_executor(self._set_contract)

    def _transfer_erc20(self,
                        to: EthereumAddress,
                        amount: Union[int, float],
                        gas_price: int,
                        gas_limit: int) -> TxHash:
        tx = self.contract.functions.transfer(to, self.w3.toWei(amount, 'ether')).buildTransaction({
            'gas': gas_limit,
            'gasPrice': self.w3.toWei(gas_price, 'gwei'),
            'nonce': self.w3.eth.get_transaction_count(CONFIG.env('SPENDING_ADDRESS'))
        })
        signed_tx = self.w3.eth.account.signTransaction(tx, CONFIG.env('SPENDING_PRIVATE_KEY'))
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return tx_hash.hex()

    async def transfer_erc20(self,
                             to: EthereumAddress,
                             amount: Union[int, float],
                             gas_price: int,
                             gas_limit: int) -> TxHash:
        return await self._run_in_executor(functools.partial(self._transfer_erc20,
                                                             to=to,
                                                             amount=amount,
                                                             gas_price=gas_price,
                                                             gas_limit=gas_limit))


CRYPTO: _Crypto = _Crypto()
