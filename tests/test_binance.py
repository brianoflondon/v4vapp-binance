from binance.spot import Spot as Client

from v4vapp_binance.binance import get_client, get_current_price


def test_get_client():
    client = get_client()
    assert client is not None
    assert type(client) is Client

    client = get_client(testnet=True)
    assert client is not None
    assert type(client) is Client


def test_get_current_price():
    price = get_current_price("BTCUSDT")
    assert price is not None
    assert type(price) is dict
    assert "ask_price" in price
    assert "bid_price" in price
    assert "current_price" in price
    assert float(price["ask_price"]) > 0.0
    assert float(price["bid_price"]) > 0.0
    assert float(price["current_price"]) > 0.0

    price = get_current_price("BTCUSDT", testnet=True)
    assert price is not None
    assert type(price) is dict
    assert "ask_price" in price
    assert "bid_price" in price
    assert "current_price" in price
    assert float(price["ask_price"]) > 0.0
    assert float(price["bid_price"]) > 0.0
    assert float(price["current_price"]) > 0.0