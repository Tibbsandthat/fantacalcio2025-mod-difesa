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
    "2025_26": {
        "fantaboom": "fantaboom_2025_26.xlsx",
        "fantaclassic": "fantaclassic_2025_26.xlsx",
        "profeta": "profeta_2025_26.xlsx",
        "sos_fanta": "sos_fanta_2025_26.xlsx",
    },
    "2024_25": {
        "fantaboom": "fantaboom_2024_25.xlsx",
        "fantaclassic": "fantaclassic_2024_25.xlsx",
        "profeta": "profeta_2024_25.xlsx",
        "sos_fanta": "sos_fanta_2024_25.xlsx",
    },
}


def load_source(path: Path) -> 'pd.DataFrame':
    df = pd.read_excel(path)
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(
        columns={
            "nome": "name",
            "ruolo": "role",
            "squadra": "team",
            "prezzo": "price",
            "gol": "goals",
            "goal": "goals",
            "assist": "assists",
            "ass": "assists",
            "minuti": "minutes",
            "min": "minutes",
            "media": "rating",
            "mv": "rating",
            "commento": "comm",
        }
    )
    for col in ["team", "goals", "assists", "minutes", "rating", "comm"]:
        if col not in df.columns:
            df[col] = 0 if col not in ("team", "comm") else ""
    return df[["name", "team", "role", "price", "goals", "assists", "minutes", "rating", "comm"]]


def main() -> None:
    if pd is None:
        raise SystemExit("pandas is required to run this script")

    frames = []
    for season, sources in SOURCES.items():
        for source, filename in sources.items():
            path = Path(filename)
            if not path.exists():
                continue
            df = load_source(path)
            df["source"] = source
            df["season"] = season
            frames.append(df)

    if not frames:
        raise SystemExit("no source data found")

    data = pd.concat(frames)

    result = {}
    for (name, role), grp in data.groupby(["name", "role"]):
        prices = grp["price"].astype(float)
        avg = round(prices.mean(), 1)
        min_p = int(prices.min())
        max_p = int(prices.max())
        player = {
            "nome": name,
            "team": grp.iloc[0].get("team", ""),
            "prezzi": {"min": min_p, "max": max_p, "avg": avg},
            "allPrices": {},
            "performance": {},
            "notes": {"comm": ""},
        }
        fallback_comm = ""
        for _, row in grp.iterrows():
            year = str(row["season"]).split("_")[0]
            player["allPrices"][f"{row['source']}_{year}"] = int(row["price"])
            player["performance"].setdefault(
                row["season"],
                {
                    "goals": int(row.get("goals", 0) or 0),
                    "assists": int(row.get("assists", 0) or 0),
                    "minutes": int(row.get("minutes", 0) or 0),
                    "rating": float(row.get("rating", 0) or 0),
                },
            )
            comm = row.get("comm")
            if row["source"] == "sos_fanta" and isinstance(comm, str) and comm:
                player["notes"]["comm"] = comm
            elif not fallback_comm and isinstance(comm, str) and comm:
                fallback_comm = comm
        if not player["notes"]["comm"] and fallback_comm:
            player["notes"]["comm"] = fallback_comm

        for season in SOURCES.keys():
            player["performance"].setdefault(
                season,
                {"goals": 0, "assists": 0, "minutes": 0, "rating": 0},
            )

        result.setdefault(role, []).append(player)

    with Path("players_database.json").open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":  # pragma: no cover
    main()
