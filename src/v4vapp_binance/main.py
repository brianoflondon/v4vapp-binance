import logging
import os
from decimal import ROUND_DOWN, ROUND_UP, Decimal
from pprint import pprint

from binance.error import ClientError
from binance.spot import Spot as Client
from dotenv import load_dotenv  # type: ignore

load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET_KEY")

testnet_api_key = os.getenv("TESTNET_API_KEY")
testnet_api_secret = os.getenv("TESTNET_SECRET_KEY")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(module)-14s %(lineno) 5d : %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)


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
    client = get_client(testnet)
    account = client.account()
    balances = {symbol: 0.0 for symbol in symbols}  # Initialize all balances to 0.0
    for balance in account["balances"]:
        if balance["asset"] in symbols:
            balances[balance["asset"]] = float(balance["free"])
    return balances


def get_open_orders_for_symbol(symbol: str, testnet: bool = False):
    """
    Get open orders for a specific symbol
    """
    client = get_client(testnet)
    open_orders = client.get_open_orders(symbol=symbol)
    return open_orders


def get_trades_for_symbol(symbol: str, testnet: bool = False):
    """
    Get trades for a specific symbol
    """
    client = get_client(testnet)
    trades = client.my_trades(symbol=symbol)
    return trades


def place_order(
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal,
    testnet: bool = False,
    order_type: str = "LIMIT",
    time_in_force: str = "GTC",
):
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
    try:
        response = client.new_order(**params)
        logging.info(response)
        pprint(response)
    except ClientError as error:
        logging.error(
            "Found error. status: {}, error code: {}, error message: {}".format(
                error.status_code, error.error_code, error.error_message
            )
        )


def run():
    trades = get_trades_for_symbol("HIVEBTC", testnet=False)
    pprint(trades)

    price = get_current_price("HIVEBTC")
    logging.info(price)
    balances = get_balances(["HIVE", "BTC"])
    logging.info("Main account balances:")
    logging.info(balances)
    logging.info("Testnet account balances:")
    balances = get_balances(["HIVE", "BTC"], testnet=True)
    logging.info(balances)

    logging.info("Open orders for HIVEBTC:")
    open_orders = get_open_orders_for_symbol("HIVEBTC", testnet=True)
    pprint(open_orders)

    # sell_price = Decimal(price["ask_price"])  # * Decimal(0.99)
    # sell_price = sell_price.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
    # place_order(
    #     symbol="HIVEBTC", side="SELL", quantity=100, price=sell_price, testnet=True
    # )
    # logging.info("Open orders for HIVEBTC:")
    # open_orders = get_open_orders_for_symbol("HIVEBTC", testnet=True)
    # pprint(open_orders)

    # logging.info("Testnet account balances:")
    # balances = get_balances(["HIVE", "BTC"], testnet=True)
    # logging.info(balances)

    buy_price = Decimal(price["bid_price"])  # * Decimal(1.01)
    buy_price = buy_price.quantize(Decimal("0.00000001"), rounding=ROUND_UP)
    place_order(
        symbol="HIVEBTC", side="BUY", quantity=300, price=buy_price, testnet=True
    )
    logging.info("Testnet account balances:")
    balances = get_balances(["HIVE", "BTC"], testnet=True)
    logging.info(balances)


if __name__ == "__main__":
    run()
