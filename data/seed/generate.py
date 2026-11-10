"""Synthetic dataset generator for RM Copilot.

Everything here is fake. Output is deterministic for a given --seed and --as-of date.

Writes to data/seed/output/:
  dataset.json  business tables (RMs, customers, products, holdings, interactions)
  truth.json    ground-truth KYC signals planted in interaction text, used by evals/

Usage:
  python data/seed/generate.py --customers 300 --seed 42
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from faker import Faker

OUT_DIR = Path(__file__).parent / "output"

CITIES = ["上海", "北京", "深圳", "杭州", "广州", "成都", "南京", "苏州", "武汉", "厦门"]
OCCUPATIONS = [
    "企业主",
    "企业高管",
    "医生",
    "律师",
    "金融从业者",
    "互联网从业者",
    "公务员",
    "退休人士",
    "自由职业",
]
RISK_LEVELS = ["R1", "R2", "R3", "R4", "R5"]
CHANNELS = ["电话", "企微", "面谈", "活动"]

# category -> (risk level, name suffixes, has maturity)
PRODUCT_SPECS = {
    "现金管理": ("R1", ["日日盈", "现金宝", "活期增利"], False),
    "固收": ("R2", ["稳健 6 个月", "安享 1 年", "信用债精选", "纯债 3 号"], True),
    "权益": ("R4", ["成长精选", "价值优选", "科技创新", "红利增强"], False),
    "另类": ("R5", ["量化中性", "私募股权 FOF", "CTA 策略"], True),
    "保险": ("R2", ["终身寿险", "年金险", "重疾险"], False),
}

# KYC signal -> phrases a customer might say. Planted into interactions; recorded in truth.json.
SIGNALS: dict[str, list[str]] = {
    "子女教育": [
        "孩子明年准备出国读书，想提前规划一笔教育金",
        "女儿在考虑去英国读研，学费要早点准备",
    ],
    "养老规划": ["快退休了，想看看养老怎么安排比较稳", "最近在想退休后的现金流问题"],
    "企业经营": ["公司今年在扩产线，现金流有点紧", "厂里刚接了个大单，下半年回款会比较多"],
    "风险厌恶": ["上次权益产品回撤让我挺难受的，还是稳一点好", "不想再碰波动大的产品了"],
    "资产配置海外": ["想配置一点美元资产分散风险", "听说香港保险不错，想了解一下"],
    "传承规划": ["想了解一下家族信托，给孩子做个安排", "父母年纪大了，在考虑财富传承的事"],
    "购房计划": ["打算明年换一套大点的房子", "在看学区房，首付可能要动一部分资金"],
}

NEUTRAL_LINES = [
    "例行回访，客户表示近期没有新的资金安排",
    "发送了本周市场观点，客户已读",
    "确认了下次见面时间",
    "客户询问了持仓产品的最新净值",
    "邀请客户参加下月的投资策略会",
    "客户反馈 App 查询收益不太方便",
]


def tier_for(aum: float) -> str:
    if aum < 500_000:
        return "普通"
    if aum < 3_000_000:
        return "黄金"
    if aum < 10_000_000:
        return "铂金"
    return "钻石"


def generate(n_customers: int, seed: int, as_of: date) -> tuple[dict, dict]:
    rng = random.Random(seed)
    fake = Faker("zh_CN")
    fake.seed_instance(seed)

    rms = []
    for i in range(8):
        rms.append(
            {
                "id": f"RM{i + 1:03d}",
                "name": fake.name(),
                "team": f"财富{i // 4 + 1}组",
                "role": "manager" if i % 4 == 0 else "rm",
            }
        )
    serving_rms = [r for r in rms if r["role"] == "rm"]

    products = []
    for category, (risk, names, _) in PRODUCT_SPECS.items():
        for name in names:
            products.append(
                {
                    "id": f"P{len(products) + 1:03d}",
                    "name": f"{name}{'' if category == '保险' else '理财'}",
                    "category": category,
                    "risk_level": risk,
                }
            )
    has_maturity = {p["id"]: PRODUCT_SPECS[p["category"]][2] for p in products}

    customers, holdings, interactions = [], [], []
    truth: dict[str, dict] = {}

    for c_idx in range(n_customers):
        cid = f"C{c_idx + 1:05d}"
        occupation = rng.choice(OCCUPATIONS)
        age = rng.randint(58, 75) if occupation == "退休人士" else rng.randint(28, 62)
        birth = as_of.replace(year=as_of.year - age) - timedelta(days=rng.randint(0, 364))
        onboarded = as_of - timedelta(days=rng.randint(60, 365 * 8))
        rm = rng.choice(serving_rms)

        # Holdings: log-normal amounts so a few customers dominate AUM, like real books.
        aum = 0.0
        for _ in range(rng.randint(1, 5)):
            p = rng.choice(products)
            amount = round(min(rng.lognormvariate(13, 1.1), 30_000_000), -3) or 10_000
            start = onboarded + timedelta(days=rng.randint(0, max(1, (as_of - onboarded).days)))
            maturity = None
            if has_maturity[p["id"]]:
                # Spread maturities from -30 to +180 days around as_of: some due soon.
                maturity = as_of + timedelta(days=rng.randint(-30, 180))
            holdings.append(
                {
                    "id": f"H{len(holdings) + 1:06d}",
                    "customer_id": cid,
                    "product_id": p["id"],
                    "amount": amount,
                    "start_date": start.isoformat(),
                    "maturity_date": maturity.isoformat() if maturity else None,
                }
            )
            aum += amount

        planted = rng.sample(list(SIGNALS), k=rng.choice([0, 1, 1, 2, 2, 3]))
        evidence: list[dict] = []
        n_inter = rng.randint(3, 12)
        signal_slots = set(rng.sample(range(n_inter), k=min(len(planted), n_inter)))
        signal_iter = iter(planted)
        for i_idx in range(n_inter):
            occurred = datetime.combine(
                as_of - timedelta(days=rng.randint(1, 540)), datetime.min.time()
            ) + timedelta(hours=rng.randint(9, 20), minutes=rng.randint(0, 59))
            iid = f"I{len(interactions) + 1:07d}"
            if i_idx in signal_slots:
                signal = next(signal_iter)
                phrase = rng.choice(SIGNALS[signal])
                content = f"客户提到：{phrase}。{rng.choice(NEUTRAL_LINES)}。"
                evidence.append({"signal": signal, "interaction_id": iid, "phrase": phrase})
            else:
                content = f"{rng.choice(NEUTRAL_LINES)}。"
            interactions.append(
                {
                    "id": iid,
                    "customer_id": cid,
                    "rm_id": rm["id"],
                    "channel": rng.choice(CHANNELS),
                    "occurred_at": occurred.isoformat(timespec="minutes"),
                    "content": content,
                }
            )

        customers.append(
            {
                "id": cid,
                "name": fake.name(),
                "gender": rng.choice(["男", "女"]),
                "birth_date": birth.isoformat(),
                "city": rng.choice(CITIES),
                "occupation": occupation,
                "tier": tier_for(aum),
                "risk_level": rng.choice(RISK_LEVELS),
                "aum": round(aum, 2),
                "rm_id": rm["id"],
                "onboarded_at": onboarded.isoformat(),
                "tags": [],  # filled later by the KYC agent, never by the generator
            }
        )
        truth[cid] = {"signals": sorted(planted), "evidence": evidence}

    dataset = {
        "meta": {"seed": seed, "as_of": as_of.isoformat(), "customers": n_customers},
        "relationship_managers": rms,
        "products": products,
        "customers": customers,
        "holdings": holdings,
        "interactions": interactions,
    }
    return dataset, {"meta": dataset["meta"], "customers": truth}


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--customers", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--out", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    dataset, truth = generate(args.customers, args.seed, args.as_of)
    args.out.mkdir(parents=True, exist_ok=True)
    for name, payload in (("dataset.json", dataset), ("truth.json", truth)):
        (args.out / name).write_text(json.dumps(payload, ensure_ascii=False, indent=1), "utf-8")

    print(
        f"wrote {len(dataset['customers'])} customers, {len(dataset['holdings'])} holdings, "
        f"{len(dataset['interactions'])} interactions -> {args.out}"
    )


if __name__ == "__main__":
    main()
