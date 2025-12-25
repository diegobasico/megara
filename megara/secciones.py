from typing import Any

import duckdb

from etc.paths import local_paths


def check_result(df, profile_name) -> None:
    if df.is_empty():
        raise ValueError(f"Profile '{profile_name}' not found in wshmp")

    if df.height != 1:
        raise ValueError(f"Profile '{profile_name}' is not unique in wshmp")


def read_wshmp_section(profile_name: str):
    with duckdb.connect(local_paths.db / "sections.db") as conn:
        query = conn.execute(
            """
            select *
            from wsmhp
            where shape = ?
        """,
            [profile_name],
        )
        result = query.pl()

        check_result(result, profile_name)

        row: dict[str, Any] = result.row(0, named=True)

        return row


if __name__ == "__main__":
    pass
