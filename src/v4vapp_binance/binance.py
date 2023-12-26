import logging
import os
from decimal import Decimal

from binance.error import ClientError  # type: ignore
from binance.spot import Spot as Client  # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")

testnet_api_key = os.getenv("TESTNET_API_KEY")
testnet_api_secret = os.getenv("TESTNET_SECRET_KEY")


def get_client(testnet: bool = False) -> Client:
    """
    Get a Binance API client
    """
    try:
        if testnet:
            client = Client(
                testnet_api_key,
                testnet_api_secret,
                base_url="https://testnet.binance.vision",
            )
        else:
            client = Client(
                api_key=api_key,
                api_secret=api_secret,
            )
        return client
    except Exception as e:
        logging.error(e)
        return None


def get_current_price(symbol: str, testnet: bool = False) -> dict:
    """
    Get current ask and bid prices for a symbol
    """
    client = get_client(testnet)

    price = {}
    ticker_info = client.book_ticker(symbol)
    price["ask_price"] = ticker_info["askPrice"]
    price["bid_price"] = ticker_info["bidPrice"]
    ticker_price = client.ticker_price(symbol)
    price["current_price"] = ticker_price["price"]
    return price


def get_balances(symbols: list, testnet: bool = False) -> dict:
    """
    Get balances for a list of symbols
    """
    try:
        client = get_client(testnet)
        account = client.account()
        balances = {symbol: 0.0 for symbol in symbols}  # Initialize all balances to 0.0
        for balance in account["balances"]:
            if balance["asset"] in symbols:
                balances[balance["asset"]] = float(balance["free"])
        if "BTC" in balances and balances["BTC"] > 0.0:
            balances["SATS"] = int(balances["BTC"] * 100_000_000)
        return balances
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return {}  # Return an empty dictionary instead of None


def get_open_orders_for_symbol(symbol: str, testnet: bool = False) -> list:
    """
    Get open orders for a specific symbol
    """
    client = get_client(testnet)
    open_orders = client.get_open_orders(symbol=symbol)
    return open_orders


def get_trades_for_symbol(symbol: str, testnet: bool = False) -> list:
    """
    Get trades for a specific symbol
    """
    client = get_client(testnet)
    trades = client.my_trades(symbol=symbol)
    return trades


def place_order_now(
    from_asset: str,
    to_asset: str,
    side: str,  # make this buy or sell with an enu,
    quantity: Decimal,
    price: str,
    order_id: str = "",
    testnet: bool = False,
) -> dict:
    """
    Place a new order, checks balances and places order if there are sufficient funds
    """
    balances = {
        "before": get_balances([from_asset, to_asset], testnet=testnet),
    }
    if price == "now":
        prices = get_current_price(f"{from_asset}{to_asset}", testnet=testnet)
        if side == "BUY":
            price_d = Decimal(prices["ask_price"])
        elif side == "SELL":
            price_d = Decimal(prices["bid_price"])

    ans = place_order(
        symbol=f"{from_asset}{to_asset}",
        side=side,
        quantity=quantity,
        price=price_d,
        order_id=order_id,
        testnet=testnet,
    )
    balances["after"] = get_balances([from_asset, to_asset], testnet=testnet)
    balances["delta"] = {  # Calculate the difference in balances
        k: balances["after"][k] - balances["before"][k] for k in balances["after"]
    }
    if "HIVE" in balances["after"]:
        balances["delta"]["SATS/HIVE"] = int(
            balances["delta"]["SATS"] / balances["delta"]["HIVE"]
        )
    if "BTC" in balances["delta"]:
        balances["delta"]["BTC"] = round(balances["delta"]["BTC"], 8)
    ans["prices"] = prices
    ans["balances"] = balances
    return ans


def place_order(
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal,
    testnet: bool = False,
    order_type: str = "LIMIT",
    time_in_force: str = "GTC",
    order_id: str = "",
) -> dict:
    """
    Place a new order
    """
    client = get_client(testnet)
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "timeInForce": time_in_force,
        "quantity": str(quantity),
        "price": str(price),
    }
    if order_id:
        params["newClientOrderId"] = order_id
    try:
        response = client.new_order(**params)
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return {"error": error.error_message}


def get_quote(
    from_asset: str, to_asset: str, from_amount: float, testnet: bool = False
) -> dict:
    """
    Get quote for a symbol
    Waiting for permission from Bianance to use this endpoint
    """
    client = Client(api_key=api_key, api_secret=api_secret)
    try:
        response = client.send_quote_request(
            fromAsset=from_asset,
            toAsset=to_asset,
            fromAmount=from_amount,
            validTime="10s",
            walletType="SPOT",
            recvWindow=5000,
        )
        logging.info(response)
        return response
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )
        return {"error": error.error_message}
