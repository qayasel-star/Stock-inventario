"""Static acceptance checks for the StockPro browser prototype; not E2E tests."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "app" / "index.html").read_text(encoding="utf-8")


def test_required_modules_present():
    for module in ("dashboard", "inventory", "sales", "purchases", "movements", "suppliers", "analytics", "settings"):
        assert f'id="{module}"' in HTML


def test_stock_adjustment_guards_and_traceability():
    assert "Number.isSafeInteger(q)" in HTML
    assert "after<0" in HTML
    assert "!reason" in HTML
    assert "before,delta,after,reason" in HTML
    assert "stock_adjustment" in HTML


def test_sale_guards_and_historical_cost():
    assert "q>p.qty" in HTML
    assert "costAtSale:p.cost" in HTML
    assert "unitPrice:p.price" in HTML


def test_encrypted_backup_and_restore_guards():
    assert "AES-GCM" in HTML
    assert "PBKDF2" in HTML
    assert "iterations:310000" in HTML
    assert "backup-too-large" in HTML
    assert "invalid-movement" in HTML


def test_history_not_deletable():
    assert "Historical transactions cannot be deleted" in HTML
    assert "Los movimientos históricos no se eliminan" in HTML
