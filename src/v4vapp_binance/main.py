import logging
import os
from decimal import ROUND_DOWN, ROUND_UP, Decimal
from pprint import pprint

from dotenv import load_dotenv  # type: ignore

from v4vapp_binance.binance import (
    get_balances,
    get_current_price,
    get_open_orders_for_symbol,
    get_trades_for_symbol,
    place_order,
)

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

    sell_price = Decimal(price["ask_price"])  # * Decimal(0.99)
    sell_price = sell_price.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
    place_order(
        symbol="HIVEBTC", side="SELL", quantity=100, price=sell_price, testnet=True
    )
    logging.info("Open orders for HIVEBTC:")
    open_orders = get_open_orders_for_symbol("HIVEBTC", testnet=True)
    pprint(open_orders)

    logging.info("Testnet account balances:")
    balances = get_balances(["HIVE", "BTC"], testnet=True)
    logging.info(balances)

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
