import argparse
from collections import defaultdict

import numpy as np
import pandas as pd


def ajustar_ids(
    csv_path: str,
    max_ids: int = 700,
    seed: int = 42,
) -> None:
    """
    Limita a `max_ids` IDs únicos, propagando 1:1 por IP.
    - Prioriza IPs que ya tenían algún Id_usuario no vacío.
    - Si hay menos de `max_ids` IPs con ID previo, completa con IPs sin ID.
    - Se seleccionan hasta `max_ids` IPs, se asigna un ID único U00{n} a cada una,
      y se propaga a todas sus filas.
    - El resto de IPs queda con Id_usuario vacío.
    - Matriculado se recalcula: máximo 1 True por IP con ID, evitando la primera
      visita si hay varias; el resto False.
    - No se tocan otras columnas.
    """
    rng = np.random.default_rng(seed)

    df = pd.read_csv(csv_path)

    # Identificar IPs elegibles (tenían algún Id_usuario no vacío)
    mask_id = df["Id_usuario"].notna() & (df["Id_usuario"].astype(str).str.strip() != "")
    ips_with_id = df.loc[mask_id, "IP_usuario"].dropna().unique().tolist()
    
    # Si hay menos de max_ids IPs con ID, completar con IPs sin ID
    todas_las_ips = df["IP_usuario"].dropna().unique().tolist()
    ips_sin_id = [ip for ip in todas_las_ips if ip not in ips_with_id]
    
    # Priorizar IPs que ya tenían ID, luego completar con las que no tenían
    rng.shuffle(ips_with_id)
    rng.shuffle(ips_sin_id)
    
    ips_selected = ips_with_id[:max_ids]
    faltantes = max_ids - len(ips_selected)
    if faltantes > 0 and ips_sin_id:
        ips_selected.extend(ips_sin_id[:faltantes])
    
    # Generar pool de IDs únicos para las IPs seleccionadas
    ids_pool = [f"U00{n}" for n in range(len(ips_selected))]
    ip_to_id = dict(zip(ips_selected, ids_pool))

    # Propagar ID por IP; resto vacío
    df["Id_usuario"] = df["IP_usuario"].map(ip_to_id)
    df.loc[df["Id_usuario"].isna(), "Id_usuario"] = ""

    # Recalcular Matriculado: una sola fila True por IP con ID, evitando la primera
    df["Matriculado"] = False
    mask_assigned = df["Id_usuario"].astype(str).str.strip() != ""
    for ip, grp in df[mask_assigned].groupby("IP_usuario"):
        idxs = grp.index.to_list()
        if len(idxs) == 1:
            choice = idxs[0]
        else:
            choice_pool = idxs[1:] if len(idxs) > 1 else idxs
            choice = rng.choice(choice_pool)
        df.at[choice, "Matriculado"] = True

    df.to_csv(csv_path, index=False)

    ips_con_id_previo = len([ip for ip in ips_selected if ip in ips_with_id])
    ips_nuevas = len(ips_selected) - ips_con_id_previo
    print(
        f"[OK] Guardado: {csv_path}\n"
        f"  IPs seleccionadas: {len(ips_selected)} (máx {max_ids})\n"
        f"    - IPs con ID previo: {ips_con_id_previo}\n"
        f"    - IPs nuevas (sin ID previo): {ips_nuevas}\n"
        f"  IDs únicos asignados: {len(ids_pool)}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ajusta Immune_metricas v2 a un máximo de IDs únicos."
    )
    parser.add_argument(
        "--csv",
        default="metricas_immune/Immune_metricas_v2.csv",
        help="Ruta al CSV a ajustar (por defecto metricas_immune/Immune_metricas_v2.csv)",
    )
    parser.add_argument(
        "--max-ids",
        type=int,
        default=700,
        help="Máximo de IDs únicos a asignar (por defecto 700)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semilla para reproducibilidad (por defecto 42)",
    )
    args = parser.parse_args()

    ajustar_ids(args.csv, max_ids=args.max_ids, seed=args.seed)

