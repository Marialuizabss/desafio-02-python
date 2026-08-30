"""Indicadores, exportações e gráficos."""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def build_indicators(df: pd.DataFrame, erros_etapa: dict | None=None, erros_tipo: dict | None=None) -> dict:    
    """Calcula os principais indicadores dos atendimentos processados."""
    times=pd.to_numeric(df.get("tempo_minutos"),errors="coerce").dropna().to_numpy(dtype=float)
    paginas=df[["documento","pagina","metodo"]].dropna(subset=["documento","pagina"]).drop_duplicates(subset=["documento","pagina"])
    classificacoes=df.get("classificacao",pd.Series(dtype=str)).value_counts(dropna=False)
    categorias=df.get("categoria",pd.Series(dtype=str)).value_counts(dropna=False)
    status=df.get("status",pd.Series(dtype=str)).value_counts(dropna=False)
    municipios=df.get("municipio",pd.Series(dtype=str)).dropna().value_counts()
    ufs=df.get("uf",pd.Series(dtype=str)).dropna().value_counts()
    tempos_categoria=df.assign(tempo=pd.to_numeric(df.get("tempo_minutos"),errors="coerce")).groupby("categoria")["tempo"].mean().dropna()
    percentual_classificacao={str(k):float(v/len(df)*100) for k,v in classificacoes.items()} if len(df) else {}
    percentual_ocr=float((paginas["metodo"]=="ocr").mean()*100) if len(paginas) else 0.0
    return {
      "total_documentos":int(df["documento"].nunique()) if "documento" in df else 0,
      "total_paginas":int(len(paginas)),
      "total_registros":int(len(df)),
      "por_classificacao":classificacoes.to_dict(),
      "percentual_por_classificacao":percentual_classificacao,
      "por_categoria":categorias.to_dict(),
      "por_status":status.to_dict(),
      "por_municipio":municipios.to_dict(),
      "por_uf":ufs.to_dict(),
      "por_metodo_extracao":paginas["metodo"].value_counts().to_dict() if len(paginas) else {},
      "tempo_medio":float(np.mean(times)) if times.size else None,
      "tempo_mediano":float(np.median(times)) if times.size else None,
      "tempo_desvio_padrao":float(np.std(times)) if times.size else None,
      "categoria_maior_volume":categorias.idxmax() if not categorias.empty else None,
      "categoria_maior_tempo_medio":tempos_categoria.idxmax() if not tempos_categoria.empty else None,
      "percentual_ocr":percentual_ocr,
      "erros_por_etapa":erros_etapa or {},
      "erros_por_tipo":erros_tipo or {},
    }

def export_results(df: pd.DataFrame, output_dir: str | Path, csv_name: str, json_name: str, erros_etapa: dict | None=None, erros_tipo: dict | None=None) -> dict:    
    """Exporta os dados processados em CSV e os indicadores em JSON."""
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    indicators=build_indicators(df,erros_etapa,erros_tipo)
    df.to_csv(out/csv_name,index=False,encoding="utf-8")
    (out/json_name).write_text(json.dumps(indicators,ensure_ascii=False,indent=2,default=float),encoding="utf-8")
    return indicators

def generate_charts(df: pd.DataFrame, directory: str | Path) -> None:
    """Gera gráficos dos atendimentos por categoria, status e tempo médio."""
    path=Path(directory); path.mkdir(parents=True,exist_ok=True)
    plots=[("categoria","Atendimentos por categoria","atendimentos_categoria.png"),("status","Atendimentos por status","atendimentos_status.png")]
    for column,title,name in plots:
        ax=df[column].replace(r"^\s*$","Sem informação",regex=True).fillna("Sem informação").value_counts().sort_values().plot.barh(color="#1F4E78",figsize=(9,5))
        ax.set_title(title); ax.set_xlabel("Quantidade"); ax.set_ylabel(""); plt.tight_layout(); plt.savefig(path/name,dpi=160); plt.close()
    temp=df.assign(tempo=pd.to_numeric(df["tempo_minutos"],errors="coerce")).groupby("categoria")["tempo"].mean().dropna().sort_values()
    ax=temp.plot.barh(color="#D6A84B",figsize=(9,5)); ax.set_title("Tempo médio por categoria"); ax.set_xlabel("Minutos"); ax.set_ylabel(""); plt.tight_layout(); plt.savefig(path/"tempo_medio_categoria.png",dpi=160); plt.close()
