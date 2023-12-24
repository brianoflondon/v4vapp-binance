import logging
import os

from binance.error import ClientError
from binance.spot import Spot as Client
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
