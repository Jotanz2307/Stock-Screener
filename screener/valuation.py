"""Rumus valuasi harga wajar."""
import math


def graham_value(eps, bvps) -> float:
    """Harga wajar Graham = akar(22.5 x EPS x BVPS).

    Hanya berlaku jika EPS dan BVPS positif; selain itu hasilnya NaN
    (perusahaan rugi atau ekuitas negatif tidak punya harga wajar Graham).
    """
    if eps is None or bvps is None:
        return math.nan
    eps, bvps = float(eps), float(bvps)
    if math.isnan(eps) or math.isnan(bvps) or eps <= 0 or bvps <= 0:
        return math.nan
    return math.sqrt(22.5 * eps * bvps)
