def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_list_customers_sorted_by_aum(client):
    body = client.get("/customers", params={"page_size": 10}).json()
    assert body["total"] == 30
    aums = [float(c["aum"]) for c in body["items"]]
    assert aums == sorted(aums, reverse=True)


def test_filter_by_tier(client):
    items = client.get("/customers", params={"tier": "黄金", "page_size": 100}).json()["items"]
    assert all(c["tier"] == "黄金" for c in items)


def test_customer_detail(client):
    cid = client.get("/customers").json()["items"][0]["id"]
    detail = client.get(f"/customers/{cid}").json()
    assert detail["id"] == cid
    assert detail["holdings"] and detail["interactions"]
    assert abs(sum(float(h["amount"]) for h in detail["holdings"]) - float(detail["aum"])) < 1


def test_customer_not_found(client):
    assert client.get("/customers/NOPE").status_code == 404


def test_generator_is_deterministic(generated):
    from datetime import date

    from tests.conftest import _load_generator

    again = _load_generator().generate(n_customers=30, seed=7, as_of=date(2026, 11, 1))
    assert again == generated


def test_truth_evidence_matches_interactions(generated):
    dataset, truth = generated
    by_id = {i["id"]: i for i in dataset["interactions"]}
    for cid, t in truth["customers"].items():
        assert {e["signal"] for e in t["evidence"]} == set(t["signals"])
        for e in t["evidence"]:
            assert by_id[e["interaction_id"]]["customer_id"] == cid
            assert e["phrase"] in by_id[e["interaction_id"]]["content"]
