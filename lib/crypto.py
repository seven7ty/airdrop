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
        self.explorer_url: str = CONFIG.mainnet_explorer_url if not self.testnet else CONFIG.testnet_explorer_url
        self.contract_address: EthereumAddress = (CONFIG.mainnet_contract_address if not
                                                  self.testnet else CONFIG.testnet_contract_address)
        self.w3: Web3 = Web3(provider=Web3.HTTPProvider(self.rpc_url))
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.transaction_count: int = self.w3.eth.get_transaction_count(CONFIG.env('SPENDING_ADDRESS'))
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
                        gas_limit: int = 100000) -> TxHash:
        tx = self.contract.functions.transfer(to, int(amount * 10 ** CONFIG.token_decimals)).buildTransaction({
            'gas': gas_limit,
            'gasPrice': self.w3.eth.gas_price,
            'nonce': self.transaction_count
        })
        signed_tx = self.w3.eth.account.sign_transaction(tx, CONFIG.env('SPENDING_PRIVATE_KEY'))
        tx_hash = self.w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        self.transaction_count += 1
        return tx_hash.hex()

    async def transfer_erc20(self,
                             to: EthereumAddress,
                             amount: Union[int, float]) -> TxHash:
        return await self._run_in_executor(functools.partial(self._transfer_erc20,
                                                             to=to,
                                                             amount=amount))

    def explorer(self, hash_: str, type_: str = 'tx') -> str:
        return f'{self.explorer_url}/{type_}/{hash_}'

    async def get_erc20_balance(self, address: EthereumAddress) -> float:
        return round(await self._run_in_executor(
            lambda: self.contract.functions.balanceOf(address).call()) / 10 ** CONFIG.token_decimals, 18)


CRYPTO: _Crypto = _Crypto()
