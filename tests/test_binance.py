from binance.spot import Spot as Client  # type: ignore

from v4vapp_binance.binance import get_balances, get_client, get_current_price


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


def test_get_balances():
    balances = get_balances(["BTC", "HIVE"])
    assert balances is not None
    assert type(balances) is dict
    if len(balances) == 0:
        # this will be called if the IP address is not
        # whitelisted on Binance
        pass
    else:
        assert len(balances) == 2
        assert balances["BTC"] >= 0.0
        assert balances["HIVE"] >= 0.0

    balances = get_balances(["BTC", "HIVE"], testnet=True)
    assert balances is not None
    assert type(balances) is dict
    assert len(balances) == 2
    assert balances["BTC"] > 0.0
    assert balances["HIVE"] > 0.0
