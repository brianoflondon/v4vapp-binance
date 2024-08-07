from pprint import pprint

import pytest
import requests  # type: ignore

from v4vapp_binance.binance import (
    BinanceErrorLowBalance,
    get_balances,
    get_current_price,
    place_order,
    place_order_now,
)


# This fixture will return True if the Binance Testnet is down and False otherwise
@pytest.fixture(scope="module")
def binance_testnet_down():
    response = requests.get("https://testnet.binance.vision/api/v3/ping")
    return response.status_code != 200


def test_get_current_price_testnet(binance_testnet_down):
    if binance_testnet_down:
        pytest.skip("Binance Testnet is down, skipping test")
    price = get_current_price("BTCUSDT", testnet=True)
    assert price is not None
    assert type(price) is dict
    assert "ask_price" in price
    assert "bid_price" in price
    assert "current_price" in price
    assert float(price["ask_price"]) > 0.0
    assert float(price["bid_price"]) > 0.0
    assert float(price["current_price"]) > 0.0


def test_get_balances_testnet(binance_testnet_down):
    if binance_testnet_down:
        pytest.skip("Binance Testnet is down, skipping test")
    balances = get_balances(["BTC", "HIVE"], testnet=True)
    assert balances is not None
    assert type(balances) is dict
    assert balances["BTC"] > 0.0
    assert balances["HIVE"] > 0.0
    if "BTC" in balances:
        assert balances["SATS"] >= 0.0


def test_place_order_testnet(binance_testnet_down):
    if binance_testnet_down:
        pytest.skip("Binance Testnet is down, skipping test")
    price = get_current_price("HIVEBTC", testnet=True)
    balances = get_balances(["BTC", "HIVE"], testnet=True)
    if "BTC" in balances:
        balances["sats"] = round(balances["BTC"] * 1e8, 0)
    # round the quantity to 1 decimal place
    quantity = balances["HIVE"] * 0.1
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


# parameterize this test with buy and sell


@pytest.mark.parametrize("side", ["BUY", "SELL"])
def test_place_order_now_testnet(side, binance_testnet_down):
    if binance_testnet_down:
        pytest.skip("Binance Testnet is down, skipping test")
    ans = place_order_now(
        from_asset="HIVE",
        to_asset="BTC",
        quantity=100,
        side=side,
        price="now",
        testnet=True,
        minimum_order=True
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


@pytest.mark.parametrize("side", ["BUY", "SELL"])
def test_place_order_now_minimums_testnet(side, binance_testnet_down):
    if binance_testnet_down:
        pytest.skip("Binance Testnet is down, skipping test")
    ans = place_order_now(
        from_asset="HIVE",
        to_asset="BTC",
        quantity=1,
        side=side,
        price="now",
        testnet=True,
        minimum_order=False,
    )
    pprint(ans)
    assert "LOT_SIZE" in ans.get("error") or "NOTIONAL" in ans.get("error")
    ans = place_order_now(
        from_asset="HIVE",
        to_asset="BTC",
        quantity=1,
        side=side,
        price="now",
        testnet=True,
        minimum_order=True,
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


def test_balance_error_testnet(binance_testnet_down):
    if binance_testnet_down:
        pytest.skip("Binance Testnet is down, skipping test")
    balance = get_balances(["BTC", "HIVE"], testnet=True)

    # Check that place_order_now raises a specific error
    with pytest.raises(
        BinanceErrorLowBalance
    ):  # Replace ExpectedError with the actual error class
        place_order_now(
            from_asset="HIVE",
            to_asset="BTC",
            quantity=balance["HIVE"] + 1,
            side="SELL",
            price="now",
            testnet=True,
        )
