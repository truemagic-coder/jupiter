import base64
import requests
from solders import message
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.system_program import transfer, TransferParams

from solana.rpc.api import Client
    
class Jupiter():
    
    ENDPOINT_APIS_URL = {
        "QUOTE": "https://quote-api.jup.ag/v6/quote?",
        "SWAP": "https://quote-api.jup.ag/v6/swap",
        "OPEN_ORDER": "https://jup.ag/api/limit/v1/createOrder",
        "CANCEL_ORDERS": "https://jup.ag/api/limit/v1/cancelOrders",
        "QUERY_OPEN_ORDERS": "https://jup.ag/api/limit/v1/openOrders?wallet=",
        "QUERY_ORDER_HISTORY": "https://jup.ag/api/limit/v1/orderHistory",
        "QUERY_TRADE_HISTORY": "https://jup.ag/api/limit/v1/tradeHistory"
    }
    
    def __init__(
        self,
        client: Client,
        quote_api_url: str="https://quote-api.jup.ag/v6/quote?",
        swap_api_url: str="https://quote-api.jup.ag/v6/swap",
        open_order_api_url: str="https://jup.ag/api/limit/v1/createOrder",
        cancel_orders_api_url: str="https://jup.ag/api/limit/v1/cancelOrders",
        query_open_orders_api_url: str="https://jup.ag/api/limit/v1/openOrders?wallet=",
        query_order_history_api_url: str="https://jup.ag/api/limit/v1/orderHistory",
        query_trade_history_api_url: str="https://jup.ag/api/limit/v1/tradeHistory",
    ):
        self.rpc = client
        
        self.ENDPOINT_APIS_URL["QUOTE"] = quote_api_url
        self.ENDPOINT_APIS_URL["SWAP"] = swap_api_url
        self.ENDPOINT_APIS_URL["OPEN_ORDER"] = open_order_api_url
        self.ENDPOINT_APIS_URL["CANCEL_ORDERS"] = cancel_orders_api_url
        self.ENDPOINT_APIS_URL["QUERY_OPEN_ORDERS"] = query_open_orders_api_url
        self.ENDPOINT_APIS_URL["QUERY_ORDER_HISTORY"] = query_order_history_api_url
        self.ENDPOINT_APIS_URL["QUERY_TRADE_HISTORY"] = query_trade_history_api_url
    
    def quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int=None,
        swap_mode: str="ExactIn",
        only_direct_routes: bool=False,
        as_legacy_transaction: bool=False,
        exclude_dexes: list=None,
        max_accounts: int=None,
        platform_fee_bps: int=None
    ) -> dict:
        quote_url = self.ENDPOINT_APIS_URL['QUOTE'] + "inputMint=" + input_mint + "&outputMint=" + output_mint + "&amount=" + str(amount) + "&swapMode=" + swap_mode + "&onlyDirectRoutes=" + str(only_direct_routes).lower() + "&asLegacyTransaction=" + str(as_legacy_transaction).lower()
        if slippage_bps:
            quote_url += "&slippageBps=" + str(slippage_bps)
        if exclude_dexes:
            quote_url += "&excludeDexes=" + ','.join(exclude_dexes)
        if max_accounts:
            quote_url += "&maxAccounts=" + str(max_accounts)
        if platform_fee_bps:
            quote_url += "&plateformFeeBps=" + platform_fee_bps
        
        quote_response = requests.get(url=quote_url).json()
        try:
            quote_response['routePlan']
            return quote_response
        except Exception:
            raise Exception(quote_response['error'])

    def swap(
        self,
        input_mint: str,
        output_mint: str,
        amount: int=0,
        quoteResponse: str=None,
        wrap_unwrap_sol: bool=True,
        slippage_bps: int=1,
        swap_mode: str="ExactIn",
        prioritization_fee_lamports: int=None,
        only_direct_routes: bool=False,
        as_legacy_transaction: bool=False,
        exclude_dexes: list=None,
        max_accounts: int=None,
        platform_fee_bps: int=None
    ) -> str:
        if quoteResponse is None:
            quoteResponse = self.quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            slippage_bps=slippage_bps,
            swap_mode=swap_mode,
            only_direct_routes=only_direct_routes,
            as_legacy_transaction=as_legacy_transaction,
            exclude_dexes=exclude_dexes,
            max_accounts=max_accounts,
            platform_fee_bps=platform_fee_bps
            )
        transaction_parameters = {
            "quoteResponse": quoteResponse,
            "userPublicKey": self.keypair.pubkey().__str__(),
            "wrapAndUnwrapSol": wrap_unwrap_sol
        }
        if prioritization_fee_lamports:
            transaction_parameters.update({"prioritizationFeeLamports": prioritization_fee_lamports})
        transaction_data = requests.post(url=self.ENDPOINT_APIS_URL['SWAP'], json=transaction_parameters).json()
        return transaction_data['swapTransaction']

    def open_order(
        self,
        input_mint: str,
        output_mint: str,
        in_amount: int=0,
        out_amount: int=0,
        expired_at: int=None
    ) -> dict:
        keypair = Keypair()
        transaction_parameters = {
            "owner": self.keypair.pubkey().__str__(),
            "inputMint": input_mint,
            "outputMint": output_mint,
            "outAmount": out_amount,
            "inAmount": in_amount,
            "base": keypair.pubkey().__str__()
        }
        if expired_at:
            transaction_parameters['expiredAt'] = expired_at
        transaction_data = requests.post(url=self.ENDPOINT_APIS_URL['OPEN_ORDER'], json=transaction_parameters).json()['tx']
        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature2 = keypair.sign_message(message.to_bytes_versioned(raw_transaction.message))
        return {"transaction_data": transaction_data, "signature2": signature2}
    
    def cancel_orders(
        self,
        orders: list=[]
    ) -> str:
        transaction_parameters = {
            "owner": self.keypair.pubkey().__str__(),
            "feePayer": self.keypair.pubkey().__str__(), 
            "orders": orders
        }
        transaction_data = requests.post(url=self.ENDPOINT_APIS_URL['CANCEL_ORDERS'], json=transaction_parameters).json()['tx']
        return transaction_data

    @staticmethod
    def query_open_orders(
        wallet_address: str,
        input_mint: str=None,
        output_mint: str=None
    ) -> list:
        query_openorders_url = "https://jup.ag/api/limit/v1/openOrders?wallet=" + wallet_address
        if input_mint:
            query_openorders_url += "inputMint=" + input_mint
        if output_mint:
            query_openorders_url += "outputMint" + output_mint
            
        list_open_orders = requests.get(query_openorders_url, timeout=30.0).json()
        return list_open_orders

    def execute_swap(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 50,
        fee_account: Pubkey = None
    ) -> str:
        quote = self.quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            slippage_bps=slippage_bps
        )
        
        swap_transaction = self.swap(
            quoteResponse=quote
        )
        
        decoded_transaction = VersionedTransaction.from_bytes(base64.b64decode(swap_transaction))
        
        if fee_account:
            decoded_transaction.message.instructions.append(
                transfer(
                    TransferParams(
                        from_pubkey=self.keypair.pubkey(),
                        to_pubkey=fee_account,
                        lamports=2000000
                    )
                )
            )
        
        signed_transaction = self.keypair.sign_message(message.to_bytes_versioned(decoded_transaction.message))
        decoded_transaction.signatures = [signed_transaction]
        
        transaction = self.rpc.send_transaction(decoded_transaction)
        return str(transaction.value)

    def execute_swap_with_meta(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = 50,
        fee_account: Pubkey = None
    ) -> dict:
        quote = self.quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            slippage_bps=slippage_bps
        )
        
        swap_transaction = self.swap(
            quoteResponse=quote
        )
        
        decoded_transaction = VersionedTransaction.from_bytes(base64.b64decode(swap_transaction))
        
        if fee_account:
            decoded_transaction.message.instructions.append(
                transfer(
                    TransferParams(
                        from_pubkey=self.keypair.pubkey(),
                        to_pubkey=fee_account,
                        lamports=2000000
                    )
                )
            )
        
        signed_transaction = self.keypair.sign_message(message.to_bytes_versioned(decoded_transaction.message))
        decoded_transaction.signatures = [signed_transaction]
        
        transaction = self.rpc.send_transaction(decoded_transaction)
        return {
            "transaction_hash": str(transaction.value),
            "input_mint": input_mint,
            "output_mint": output_mint,
            "amount": amount,
            "quote": quote
        }

    def execute_limit_order(
        self,
        input_mint: str,
        output_mint: str,
        in_amount: int,
        out_amount: int,
        expiry: int = None
    ) -> str:
        order_data = self.open_order(
            input_mint=input_mint,
            output_mint=output_mint,
            in_amount=in_amount,
            out_amount=out_amount,
            expired_at=expiry
        )
        
        decoded_transaction = VersionedTransaction.from_bytes(base64.b64decode(order_data['transaction_data']))
        
        signature1 = self.keypair.sign_message(message.to_bytes_versioned(decoded_transaction.message))
        decoded_transaction.signatures = [signature1, order_data['signature2']]
        
        transaction = self.rpc.send_transaction(decoded_transaction)
        return str(transaction.value)

    def cancel_limit_orders(self, orders: list) -> str:
        cancel_transaction = self.cancel_orders(orders)
        
        decoded_transaction = VersionedTransaction.from_bytes(base64.b64decode(cancel_transaction))
        
        signature = self.keypair.sign_message(message.to_bytes_versioned(decoded_transaction.message))
        decoded_transaction.signatures = [signature]
        
        transaction = self.rpc.send_transaction(decoded_transaction)
        return str(transaction.value)
