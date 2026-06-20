# scripts/export_ergast_constructors.py

from fastf1.ergast import Ergast
import json


def export_unique_constructor_names(
    start_year: int = 2018,
    end_year: int = 2025,
    output_file: str = "ergast_constructor_names.json"
):
    ergast = Ergast()

    unique_names = set()

    for year in range(start_year, end_year + 1):
        try:
            print(f"Processing {year}...")

            standings = ergast.get_constructor_standings(
                season=year
            )

            if not standings.content:
                continue

            df = standings.content[0]

            for _, row in df.iterrows():
                name = str(
                    row["constructorName"]
                ).strip()

                if name:
                    unique_names.add(name)

        except Exception as e:
            print(
                f"Failed {year}: {e}"
            )

    names = sorted(unique_names)

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            names,
            f,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Saved {len(names)} constructor names "
        f"to {output_file}"
    )


if __name__ == "__main__":
    export_unique_constructor_names()