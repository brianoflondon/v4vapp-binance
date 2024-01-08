from unittest.mock import Mock, patch

import pytest
from binance.error import ClientError  # type: ignore

from v4vapp_binance.binance import BinanceErrorBadConnection, get_balances


def test_get_balances_account_failure():
    # Arrange
    mock_client = Mock()
    # mock_client.account.return_value = {"balances": []}
    mock_client.account.side_effect = ClientError(
        status_code=400,
        error_code=-2014,
        error_message="API-key format invalid.",
        header={},
    )

    with patch("v4vapp_binance.binance.get_client", return_value=mock_client):
        # Act and Assert
        with pytest.raises(BinanceErrorBadConnection):
            get_balances(["BTC"], testnet=True)
