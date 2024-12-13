# Jupiter-Solana
Jupiter-Solana is a Python library for interacting with the Jupiter aggregator on the Solana blockchain.

## Features
* Token swapping
* Limit orders

## Installation
`pip install jupiter`

## Quick Start
```python
from solana.rpc.api import Client
from jupiter-solana import Jupiter

# Initialize Solana client
client = Client("YOUR_CUSTOM_RPC_URL")

# Initialize Jupiter
jupiter = Jupiter(client)

# Get a quote
quote = jupiter.quote(
    input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    output_mint="So11111111111111111111111111111111111111112",  # SOL
    amount=1000000  # 1 USDC
)

# Execute a swap
transaction_hash = jupiter.execute_swap(
    input_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
    output_mint="So11111111111111111111111111111111111111112",  # SOL
    amount=1000000  # 1 USDC
)
```

## Features

### Quoting
Get the best swap route for a token pair:

```python
quote = jupiter.quote(input_mint, output_mint, amount)
```

### Swapping
Execute a token swap:

```python
transaction_hash = jupiter.execute_swap(input_mint, output_mint, amount)
```

### Limit Orders
Place a limit order:

```python
transaction_hash = jupiter.execute_limit_order(input_mint, output_mint, in_amount, out_amount)
```

Cancel limit orders:

```python
transaction_hash = jupiter.cancel_limit_orders(orders)
```

Refer to the method docstrings for detailed information on parameters and usage.

## Disclaimer
This library is in alpha and is not stable - it should not be used in production. By using this library you assume all risks of loss of your funds.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License and is a hard-fork of [0xtaodev jupiter-solana-sdk](https://github.com/0xTaoDev/jupiter-python-sdk)
