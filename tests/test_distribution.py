import asyncio
import json
from datetime import datetime, timedelta, timezone

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

from src.core.services.stats.v1 import stats
from src.database.postgre import POOL
from src.handlers.v1.stats import get_pool_distribution
from src.handlers.v1.utils.parsers import parse_pool_distribution
from src.middlewares.logger import error_handler

AT = datetime(2026, 11, 4, 17, 9, 23, tzinfo=timezone.utc)
ADDR = "bc1qaddress"


def req(query: str):
    return make_mocked_request("GET", f"/v1/{ADDR}/distribution{query}", match_info={"address": ADDR})


def rows(*weights, ts=AT - timedelta(minutes=10)):
    return [{"workername": n, "avg_weight": w, "timestamp": ts} for n, w in weights]


class FakePG:
    def __init__(self, result):
        self.result, self.calls = result, []

    async def fetch(self, query, *args):
        self.calls.append(args)
        return self.result


@pytest.fixture
def fake_pg():
    def install(result):
        POOL.set(FakePG(result))
        return POOL.pool

    yield install
    POOL.set(None)


# --- parsing de `at`

@pytest.mark.parametrize("value", [
    "2026-11-04T17:09:23Z",
    "2026-11-04T17:09:23+00:00",
    "2026-11-04T18:09:23+01:00",
    "2026-11-04T18:09:23 01:00",  # '+' non encodé dans l'URL
    "2026-11-04T17:09:23.000Z",
])
def test_at_accepts_iso_with_timezone_and_normalizes_to_utc(value):
    params = parse_pool_distribution(req(f"?at={value}"))
    assert params.at == AT
    assert params.at.utcoffset() == timedelta(0)
    assert params.address == ADDR


@pytest.mark.parametrize("query", [
    "",
    "?at=",
    "?at=hier",
    "?at=1730740163",  # timestamp unix : non supporté
    "?at=2026-11-04T17:09:23",  # pas de fuseau : ambigu
    "?at=2999-01-01T00:00:00Z",  # futur
])
def test_at_rejects_invalid(query):
    with pytest.raises(web.HTTPBadRequest):
        parse_pool_distribution(req(query))


# --- calcul de la répartition

def test_parts_are_fractions_summing_to_one_sorted_desc():
    result = stats.build_distribution(rows(("a", 25.0), ("b", 50.0), ("c", 25.0)), AT)
    assert [e["workername"] for e in result] == ["b", "a", "c"]  # part desc, puis nom
    assert [e["part"] for e in result] == [0.5, 0.25, 0.25]
    assert sum(e["part"] for e in result) == pytest.approx(1.0)


def test_scale_independent():
    pct = stats.build_distribution(rows(("a", 30.0), ("b", 70.0)), AT)
    frac = stats.build_distribution(rows(("a", 0.3), ("b", 0.7)), AT)
    assert [e["part"] for e in pct] == pytest.approx([e["part"] for e in frac])


def test_renormalizes_when_weights_do_not_sum_to_100():
    result = stats.build_distribution(rows(("a", 10.0), ("b", 10.0)), AT)
    assert sum(e["part"] for e in result) == pytest.approx(1.0)


def test_null_weight_counts_as_zero():
    result = stats.build_distribution(rows(("a", None), ("b", 5.0)), AT)
    assert {e["workername"]: e["part"] for e in result} == {"b": 1.0, "a": 0.0}


def test_deterministic_tie_break():
    assert [e["workername"] for e in stats.build_distribution(rows(("z", 1), ("a", 1)), AT)] == ["a", "z"]


def test_no_rows_is_not_found():
    with pytest.raises(stats.DistributionNotFound):
        stats.build_distribution([], AT)


def test_stale_sample_is_not_found():
    old = rows(("a", 1.0), ts=AT - stats.DISTRIBUTION_MAX_SAMPLE_AGE - timedelta(seconds=1))
    with pytest.raises(stats.DistributionNotFound):
        stats.build_distribution(old, AT)


def test_sample_at_max_age_is_accepted():
    assert stats.build_distribution(rows(("a", 1.0), ts=AT - stats.DISTRIBUTION_MAX_SAMPLE_AGE), AT)


def test_all_zero_weights_is_not_found():
    with pytest.raises(stats.DistributionNotFound):
        stats.build_distribution(rows(("a", 0.0), ("b", 0.0)), AT)


# --- service + route

def test_service_passes_params_to_sql(fake_pg):
    pg = fake_pg(rows(("a", 100.0)))
    result = asyncio.run(stats.get_distribution_at(parse_pool_distribution(req("?at=2026-11-04T17:09:23Z"))))
    assert pg.calls == [(ADDR, AT, stats.DISTRIBUTION_BATCH_WINDOW)]
    assert result[0]["part"] == 1.0


def call_route(query: str):
    return asyncio.run(error_handler(req(query), get_pool_distribution))


def test_route_200_contract(fake_pg):
    fake_pg(rows(("asic1", 75.0), ("asic2", 25.0)))
    resp = call_route("?at=2026-11-04T17:09:23Z")
    assert resp.status == 200
    assert json.loads(resp.text) == [
        {"workername": "asic1", "part": 0.75, "sampled_at": "2026-11-04T16:59:23+00:00"},
        {"workername": "asic2", "part": 0.25, "sampled_at": "2026-11-04T16:59:23+00:00"},
    ]


def test_route_400_bad_at(fake_pg):
    fake_pg([])
    resp = call_route("?at=nope")
    assert resp.status == 400
    assert json.loads(resp.text) == {"error": "at must be a valid ISO 8601 date"}


def test_route_404_when_no_data(fake_pg):
    fake_pg([])
    resp = call_route("?at=2026-11-04T17:09:23Z")
    assert resp.status == 404
    assert "no data" in json.loads(resp.text)["error"]
