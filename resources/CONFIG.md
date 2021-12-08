# Config files
`.json` files located in the `config/` directory are used to store non-confidential,
non-sensitive configuration data for the bot to use. In this repository,
it's all simply filled in with development values used by me,
but below you'll find instructions about how to fill these values in yourself.

## `networks.json`
- `use_testnet` (boolean) - Whether to connect to the testnet or mainnet
- `mainnet_rpc_url` (string) - The URL of the mainnet Polygon RPC server
- `testnet_rpc_url` (string) - The URL of the testnet Polygon RPC server 
- `mainnet_explorer_url` (string) - The URL of the mainnet Polygon explorer
- `testnet_explorer_url` (string) - The URL of the testnet Polygon explorer

If you set mainnet values, testnet ones can be omitted safely if `use_testnet` is `false` and vice versa.

## `addresses.json`
- `mainnet_contract_address` (string) - The contract address of the token to use if using the mainnet
- `testnet_contract_address` (string) - The contract address of the token to use if using the testnet

## `discord.json`
- `admins` (array of int(18)) - An array of Discord user IDs that are allowed to use the bot's "spending functions"
- `debug_guild` (int(18)) - The Discord guild ID where commands are hot-reloaded

## `token.json`
- `token_symbol` (string) - The symbol of the token 
- `token_decimals` (int) - The number of decimals of the token, if omitted, it will be automatically fetched
- `token_name` (string) - The name of the token 
- `token_color` (string(hex_color)) - The color that resembles the token, used in embeds

