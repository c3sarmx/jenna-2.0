from unittest.mock import MagicMock, patch

import pytest

from app.services.business_settings import mark_review_sync_run


def test_mark_review_sync_run_updates_timestamp():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.return_value = (
        "2026-09-24T06:00:00+00:00",
    )

    with patch(
        "app.services.business_settings.get_connection",
        return_value=connection,
    ):
        result = mark_review_sync_run(4)

    assert result == "2026-09-24T06:00:00+00:00"

    cursor.execute.assert_called_once_with(
        """
                UPDATE business_settings
                SET
                    review_sync_last_run_at = NOW()
                WHERE business_id = %s
                RETURNING review_sync_last_run_at;
                """,
        (4,),
    )

    connection.commit.assert_called_once()
    connection.close.assert_called_once()


def test_mark_review_sync_run_raises_when_settings_do_not_exist():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value

    cursor.fetchone.return_value = None

    with patch(
        "app.services.business_settings.get_connection",
        return_value=connection,
    ):
        with pytest.raises(
            ValueError,
            match="business settings not found",
        ):
            mark_review_sync_run(999)

    connection.commit.assert_not_called()
    connection.close.assert_called_once()
