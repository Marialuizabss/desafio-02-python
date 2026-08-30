"""Carregamento centralizado das configurações."""
from __future__ import annotations
from pathlib import Path
import json
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]

def load_config(path: str | Path | None = None) -> dict:
    """Carrega as configurações do projeto a partir do arquivo JSON."""
    load_dotenv(ROOT / ".env")
    target = Path(path) if path else ROOT / "config.json"
    with target.open(encoding="utf-8") as stream:
        cfg = json.load(stream)
    cfg["_root"] = str(ROOT)
    return cfg

def resolve(root: str | Path, relative: str | Path) -> Path:
    """Resolve um caminho relativo em relação ao diretório raiz informado."""
    path = Path(relative)
    return path if path.is_absolute() else Path(root) / path
