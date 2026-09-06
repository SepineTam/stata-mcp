"""Tests for per-instance DataFrame reuse."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from stata_mcp.data_info.base import DataInfoBase


class CountingDataInfo(DataInfoBase):
    """Small handler that exposes how often format parsing runs."""

    def __init__(self, data_path: Path, cache_dir: Path, *, head: int = 2) -> None:
        self.read_count = 0
        super().__init__(
            data_path,
            cache_dir=cache_dir,
            is_cache=False,
            string_keep_number=10,
            decimal_places=3,
            hash_length=12,
            metrics=("obs", "mean", "stderr", "min", "max"),
            head=head,
        )

    def _read_data(self) -> pd.DataFrame:
        self.read_count += 1
        return pd.DataFrame(
            {
                "group": ["a", "b", "a"],
                "value": [1.0, 2.0, 3.0],
            }
        )


class RetryDataInfo(CountingDataInfo):
    """Fail the first parse so caching behavior can be verified."""

    def _read_data(self) -> pd.DataFrame:
        self.read_count += 1
        if self.read_count == 1:
            raise RuntimeError("first parse failed")
        return pd.DataFrame({"value": [1.0]})


def _source_file(tmp_path: Path, name: str = "sample.csv") -> Path:
    path = tmp_path / name
    path.write_text("group,value\na,1\nb,2\na,3\n", encoding="utf-8")
    return path


def test_info_parses_dataframe_once_for_summary_filter_and_preview(
    tmp_path: Path,
) -> None:
    data_info = CountingDataInfo(_source_file(tmp_path), tmp_path / "cache")

    result = data_info.info

    assert result["overview"]["obs"] == 3
    assert result["head"] == [
        {"group": "a", "value": 1.0},
        {"group": "b", "value": 2.0},
    ]
    assert data_info.read_count == 1
    assert data_info._dataframe_read_count == 1


def test_repeated_df_access_returns_same_instance(tmp_path: Path) -> None:
    data_info = CountingDataInfo(_source_file(tmp_path), tmp_path / "cache")

    first = data_info.df
    second = data_info.df

    assert first is second
    assert data_info.read_count == 1


def test_dataframe_cache_is_not_shared_between_handlers(tmp_path: Path) -> None:
    source = _source_file(tmp_path)
    first = CountingDataInfo(source, tmp_path / "cache-first", head=0)
    second = CountingDataInfo(source, tmp_path / "cache-second", head=0)

    _ = first.df
    _ = second.df

    assert first.read_count == 1
    assert second.read_count == 1
    assert first.df is not second.df


def test_failed_parse_is_retried_instead_of_cached(tmp_path: Path) -> None:
    data_info = RetryDataInfo(_source_file(tmp_path), tmp_path / "cache")

    with pytest.raises(RuntimeError, match="first parse failed"):
        _ = data_info.df

    result = data_info.df

    assert result["value"].tolist() == [1.0]
    assert data_info.read_count == 2
    assert data_info._dataframe_read_count == 2
