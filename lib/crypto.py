import discord
import asyncio
import functools
import concurrent.futures
from web3 import Web3
from typing import Union, Iterable
from . import CONFIG, DATABASE
from .types import TxHash, EthereumAddress

__all__: tuple = ('CRYPTO', 'BalanceTooLow')


class BalanceTooLow(Exception):
    def __init__(self, amount: float):
        super().__init__('Balance too low to send {0}{1}'.format(amount, CONFIG.token_symbol))
    pass


class _Crypto:
    def __init__(self):
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.testnet: bool = CONFIG.use_testnet
        self.rpc_url: str = CONFIG.mainnet_rpc_url if not self.testnet else CONFIG.testnet_rpc_url
        self.explorer_url: str = CONFIG.mainnet_explorer_url if not self.testnet else CONFIG.testnet_explorer_url
        self.contract_address: EthereumAddress = (CONFIG.mainnet_contract_address if not
                                                  self.testnet else CONFIG.testnet_contract_address)
        self.w3: Web3 = Web3(provider=Web3.HTTPProvider(self.rpc_url))
        self.spending_address: EthereumAddress = self.w3.toChecksumAddress(CONFIG.env('SPENDING_ADDRESS'))
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.transaction_count: int = self.w3.eth.get_transaction_count(self.spending_address)
        self.contract = self.w3.eth.contract(self.w3.toChecksumAddress(self.contract_address), abi=CONFIG.abi)
        self.decimals: int = CONFIG.get('token_decimals') or self.contract.functions.decimals().call()

    async def spending_balance(self) -> int:
        return await self.get_erc20_balance(self.spending_address)

    async def can_afford(self, amount: Union[int, float]) -> bool:
        return await self.spending_balance() >= amount

    @property
    def decimal_multiplier(self) -> int:
        return 10 ** self.decimals

    def to_contract_value(self, amount: Union[int, float]) -> int:
        return int(amount * self.decimal_multiplier)

    def to_human_value(self, amount: Union[int, float]) -> float:
        return round(amount / self.decimal_multiplier, self.decimals)

    def _run_in_executor(self, func):
        return self.loop.run_in_executor(self.executor, func)

    def _transfer_erc20(self,
                        to: EthereumAddress,
                        amount: Union[int, float],
                        gas_limit: int = 100000) -> TxHash:
        tx = self.contract.functions.transfer(to, amount).buildTransaction({
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
        if not await self.can_afford(amount):
            raise BalanceTooLow(self.to_human_value(amount))
        return await self._run_in_executor(functools.partial(self._transfer_erc20,
                                                             to=to,
                                                             amount=amount))

    def explorer(self, hash_: str, type_: str = 'tx') -> str:
        return f'{self.explorer_url}/{type_}/{hash_}'

    async def get_erc20_balance(self, address: EthereumAddress) -> int:
        return await self._run_in_executor(lambda: self.contract.functions.balanceOf(address).call())

    async def group_payout(self,
                           group: Union[discord.Role, Iterable[EthereumAddress]],
                           amount: Union[int, float]) -> list[TxHash]:
        if not await self.can_afford(amount):
            raise BalanceTooLow(self.to_human_value(amount))
        addresses: list[EthereumAddress] = list((await DATABASE.get_role_addresses(group)).values()) \
            if isinstance(group, discord.Role) else list(group)
        split: int = int(amount / len(addresses))
        return [await self.transfer_erc20(to=address, amount=split) for address in addresses]


CRYPTO: _Crypto = _Crypto()
