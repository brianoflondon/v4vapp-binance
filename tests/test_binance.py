from pprint import pprint

import pytest
from binance.spot import Spot as Client  # type: ignore

from v4vapp_binance.binance import (
    get_balances,
    get_client,
    get_current_price,
    get_quote,
    place_order,
    place_order_now,
)


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
        assert balances["BTC"] >= 0.0
        assert balances["HIVE"] >= 0.0
        if "BTC" in balances:
            assert balances["SATS"] >= 0.0

    balances = get_balances(["BTC", "HIVE"], testnet=True)
    assert balances is not None
    assert type(balances) is dict
    assert balances["BTC"] > 0.0
    assert balances["HIVE"] > 0.0
    if "BTC" in balances:
        assert balances["SATS"] >= 0.0


def test_place_order():
    price = get_current_price("HIVEBTC", testnet=True)
    balances = get_balances(["BTC", "HIVE"], testnet=True)
    if "BTC" in balances:
        balances["sats"] = round(balances["BTC"] * 1e8, 0)
    # round the quantity to 1 decimal place
    quantity = balances["HIVE"] * 0.01
    quantity = round(quantity, 0)

    ans = place_order(
        symbol="HIVEBTC",
        side="SELL",
        quantity=quantity,
        price=price["ask_price"],
        testnet=True,
    )
    assert ans is not None
    assert ans.get("error") is None
    balances_after = get_balances(["BTC", "HIVE"], testnet=True)
    if "BTC" in balances_after:
        balances_after["sats"] = balances_after["BTC"] * 1e8
    print()
    print(balances)
    print(balances_after)
    print({k: balances_after[k] - balances[k] for k in balances_after})


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


# parameterize this test with buy and sell


@pytest.mark.parametrize("side", ["BUY", "SELL"])
def test_place_order_now(side):
    ans = place_order_now(
        from_asset="HIVE",
        to_asset="BTC",
        quantity=20,
        side=side,
        price="now",
        testnet=True,
    )
    pprint(ans)
    assert ans is not None
    assert ans.get("error") is None
    assert ans.get("prices") is not None
    assert ans.get("balances") is not None
    assert ans.get("balances").get("before") is not None
    assert ans.get("balances").get("after") is not None
    assert ans.get("balances").get("delta") is not None
    assert ans.get("balances").get("delta").get("BTC") is not None
