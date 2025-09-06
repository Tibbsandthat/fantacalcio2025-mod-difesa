#!/usr/bin/env python3
"""Generate aggregated players database from Excel sources.

Reads seasonal Excel files from multiple sources and produces a single
`players_database.json` with average, min and max prices for each player
grouped by role.
"""
from pathlib import Path
import json

try:
    import pandas as pd
except ImportError:  # pragma: no cover - environment without pandas
    pd = None

SOURCES = {
    "fantaboom": "fantaboom_2025_26.xlsx",
    "fantaclassic": "fantaclassic_2025_26.xlsx",
    "profeta": "profeta_2025_26.xlsx",
    "sos_fanta": "sos_fanta_2025_26.xlsx",
}


def load_source(path: Path) -> 'pd.DataFrame':
    df = pd.read_excel(path)
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={"nome": "name", "ruolo": "role", "prezzo": "price"})
    return df[["name", "role", "price"]]


def main() -> None:
    if pd is None:
        raise SystemExit("pandas is required to run this script")

    frames = []
    for source, filename in SOURCES.items():
        path = Path(filename)
        if not path.exists():
            continue
        df = load_source(path)
        df["source"] = source
        frames.append(df)

    if not frames:
        raise SystemExit("no source data found")

    data = pd.concat(frames)
    grouped = data.groupby(["name", "role"]).agg({"price": ["mean", "min", "max"]})

    result = {}
    for (name, role), row in grouped.iterrows():
        avg = round(row[("price", "mean")], 1)
        min_p = int(row[("price", "min")])
        max_p = int(row[("price", "max")])
        result.setdefault(role, []).append(
            {
                "nome": name,
                "prezzi": {"min": min_p, "max": max_p, "avg": avg},
                "allPrices": data[(data.name == name) & (data.role == role)]["price"].tolist(),
            }
        )

    with Path("players_database.json").open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":  # pragma: no cover
    main()
