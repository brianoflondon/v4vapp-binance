from binance.spot import Spot as Client  # type: ignore

from v4vapp_binance.binance import (
    BinanceErrorBadConnection,
    get_balances,
    get_client,
    get_current_price,
    get_quote,
)


def test_get_client():
    client = get_client()
    assert client is not None
    assert type(client) is Client

    client = get_client(testnet=True)
    assert client is not None
    assert type(client) is Client


def test_get_current_price_mainnet():
    price = get_current_price("BTCUSDT")
    assert price is not None
    assert type(price) is dict
    assert "ask_price" in price
    assert "bid_price" in price
    assert "current_price" in price
    assert float(price["ask_price"]) > 0.0
    assert float(price["bid_price"]) > 0.0
    assert float(price["current_price"]) > 0.0


def test_get_balances_mainnet():
    try:
        balances = get_balances(["BTC", "HIVE"])
        assert balances is not None
        assert type(balances) is dict

        assert balances["BTC"] >= 0.0
        assert balances["HIVE"] >= 0.0
        if "BTC" in balances:
            assert balances["SATS"] >= 0.0
    except BinanceErrorBadConnection as ex:
        # this will be called if the IP address is not
        # whitelisted on Binance
        assert ex is not None
        print("IP Address not whitelisted")


def test_get_pairs():
    client = get_client()
    pairs = client.exchange_info()
    for pair in pairs["symbols"]:
        if "HIVE" in pair["symbol"]:
            print(pair["symbol"])


def test_get_quote():
    quote = get_quote(
        from_asset="HIVEBTC", to_asset="BTC", from_amount=10, testnet=False
    )
    print(quote)
