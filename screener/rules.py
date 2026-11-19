"""Terapkan aturan filter berupa ekspresi teks, mis. "close > sma_50"."""
import pandas as pd


def apply_rules(table: pd.DataFrame, rules: list[str]) -> pd.DataFrame:
    result = table
    for rule in rules:
        result = result.query(rule)
    return result
