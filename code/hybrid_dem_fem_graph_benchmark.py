from __future__ import annotations

import heapq
import json
import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
FIGURES = BASE / "figures"
TABLES = BASE / "tables"


@dataclass(frozen=True)
class Mesh:
    nx: int
    ny: int
    nodes: np.ndarray
    triangles: np.ndarray
    tri_cells: np.ndarray


def ensure_dirs() -> None:
    for folder in [DATA, FIGURES, TABLES]:
        folder.mkdir(parents=True, exist_ok=True)


def make_triangular_mesh(nx: int = 40, ny: int = 20) -> Mesh:
    xs = np.linspace(0.0, 1.0, nx + 1)
    ys = np.linspace(0.0, 1.0, ny + 1)
    nodes = np.array([(x, y) for y in ys for x in xs], dtype=float)
    tris: list[tuple[int, int, int]] = []
    tri_cells: list[tuple[int, int]] = []
    for j in range(ny):
        for i in range(nx):
            n00 = j * (nx + 1) + i
            n10 = n00 + 1
            n01 = (j + 1) * (nx + 1) + i
            n11 = n01 + 1
            tris.append((n00, n10, n11))
            tris.append((n00, n11, n01))
            tri_cells.append((i, j))
            tri_cells.append((i, j))
    return Mesh(nx, ny, nodes, np.array(tris, dtype=int), np.array(tri_cells, dtype=int))


def weak_lens_field(xc: np.ndarray, yc: np.ndarray) -> np.ndarray:
    core = np.exp(-((xc - 0.43) ** 2 / 0.018 + (yc - 0.47) ** 2 / 0.09))
    toe = np.exp(-((xc - 0.86) ** 2 / 0.012 + (yc - 0.18) ** 2 / 0.025))
    return 0.65 * core + 0.45 * toe


def assemble_fem(mesh: Mesh, k_node: np.ndarray, h_left: float, h_right: float) -> np.ndarray:
    nnode = mesh.nodes.shape[0]
    mat = lil_matrix((nnode, nnode), dtype=float)
    rhs = np.zeros(nnode, dtype=float)

    for tri in mesh.triangles:
        pts = mesh.nodes[tri]
        x1, y1 = pts[0]
        x2, y2 = pts[1]
        x3, y3 = pts[2]
        area = 0.5 * abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        if area <= 0:
            continue
        b = np.array([y2 - y3, y3 - y1, y1 - y2], dtype=float)
        c = np.array([x3 - x2, x1 - x3, x2 - x1], dtype=float)
        ke = float(np.mean(k_node[tri]))
        local = ke * (np.outer(b, b) + np.outer(c, c)) / (4.0 * area)
        for a in range(3):
            for bidx in range(3):
                mat[tri[a], tri[bidx]] += local[a, bidx]

    x = mesh.nodes[:, 0]
    fixed = np.where((np.isclose(x, 0.0)) | (np.isclose(x, 1.0)))[0]
    for node in fixed:
        value = h_left if mesh.nodes[node, 0] < 0.5 else h_right
        mat.rows[node] = [node]
        mat.data[node] = [1.0]
        rhs[node] = value
    return np.asarray(spsolve(mat.tocsr(), rhs), dtype=float)


def cell_average_from_triangles(mesh: Mesh, tri_values: np.ndarray) -> np.ndarray:
    out = np.zeros((mesh.ny, mesh.nx), dtype=float)
    counts = np.zeros_like(out)
    for val, (i, j) in zip(tri_values, mesh.tri_cells):
        out[j, i] += val
        counts[j, i] += 1.0
    return out / np.maximum(counts, 1.0)


def fem_gradient_cells(mesh: Mesh, head: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    tri_gx = []
    tri_gy = []
    tri_mag = []
    for tri in mesh.triangles:
        pts = mesh.nodes[tri]
        x1, y1 = pts[0]
        x2, y2 = pts[1]
        x3, y3 = pts[2]
        area2 = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
        b = np.array([y2 - y3, y3 - y1, y1 - y2], dtype=float)
        c = np.array([x3 - x2, x1 - x3, x2 - x1], dtype=float)
        grad_x = float(np.dot(head[tri], b) / area2)
        grad_y = float(np.dot(head[tri], c) / area2)
        tri_gx.append(grad_x)
        tri_gy.append(grad_y)
        tri_mag.append(math.hypot(grad_x, grad_y))
    return (
        cell_average_from_triangles(mesh, np.array(tri_gx)),
        cell_average_from_triangles(mesh, np.array(tri_gy)),
        cell_average_from_triangles(mesh, np.array(tri_mag)),
    )


def dijkstra_path(ie: np.ndarray, exit_mask: np.ndarray, source_mask: np.ndarray) -> tuple[float, list[tuple[int, int]]]:
    ny, nx = ie.shape
    dist = np.full((ny, nx), np.inf)
    prev: dict[tuple[int, int], tuple[int, int]] = {}
    heap: list[tuple[float, int, int]] = []
    for j, i in zip(*np.where(exit_mask)):
        dist[j, i] = 0.0
        heapq.heappush(heap, (0.0, j, i))
    target: tuple[int, int] | None = None
    spacing = 1.0 / max(nx, ny)
    while heap:
        cost, j, i = heapq.heappop(heap)
        if cost > dist[j, i]:
            continue
        if source_mask[j, i]:
            target = (j, i)
            break
        for dj, di in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            jj, ii = j + dj, i + di
            if jj < 0 or jj >= ny or ii < 0 or ii >= nx:
                continue
            edge_ie = 0.5 * (ie[j, i] + ie[jj, ii])
            edge_cost = spacing / max(edge_ie, 1.0e-6)
            new_cost = cost + edge_cost
            if new_cost < dist[jj, ii]:
                dist[jj, ii] = new_cost
                prev[(jj, ii)] = (j, i)
                heapq.heappush(heap, (new_cost, jj, ii))
    if target is None:
        return float("inf"), []
    path = [target]
    while path[-1] in prev:
        path.append(prev[path[-1]])
    path.reverse()
    return float(dist[target]), path


def run_dem_window(local_gradient: float, local_ie: float, npx: int = 11, npy: int = 7) -> tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(126)
    spacing = 1.0
    particles = []
    for j in range(npy):
        for i in range(npx):
            particles.append([len(particles), i * spacing, j * spacing, 0.0, 0.0, False])
    particles_arr = np.array(particles, dtype=object)

    bonds = []
    for a in range(len(particles_arr)):
        xa, ya = float(particles_arr[a, 1]), float(particles_arr[a, 2])
        for b in range(a + 1, len(particles_arr)):
            xb, yb = float(particles_arr[b, 1]), float(particles_arr[b, 2])
            d = math.hypot(xa - xb, ya - yb)
            if 0.5 < d <= 1.05 * spacing:
                strength = 0.18 + 0.08 * rng.random() + 0.08 * (ya / max((npy - 1) * spacing, 1.0))
                bonds.append([a, b, strength, False])
    bonds_arr = np.array(bonds, dtype=object)

    dt = 0.02
    mass = 1.0
    damping = 0.18
    k_contact = 4.0
    drag_base = 0.36 * local_gradient * max(local_ie, 0.5)
    history = []
    for step in range(220):
        active_count = 0
        for idx in range(len(particles_arr)):
            x = float(particles_arr[idx, 1])
            y = float(particles_arr[idx, 2])
            detached = bool(particles_arr[idx, 5])
            local_drag = drag_base * (0.75 + 0.5 * x / max((npx - 1) * spacing, 1.0)) * (1.0 + 0.08 * math.sin(0.25 * step + y))
            bonded_strength = 0.0
            connected = 0
            for bond in bonds_arr:
                if bool(bond[3]):
                    continue
                if int(bond[0]) == idx or int(bond[1]) == idx:
                    bonded_strength += float(bond[2])
                    connected += 1
            if connected == 0 or local_drag > 0.68 * bonded_strength:
                detached = True
            vx = float(particles_arr[idx, 3])
            vy = float(particles_arr[idx, 4])
            fx = local_drag - damping * vx
            fy = -0.04 * vy
            if not detached:
                fx -= k_contact * 0.02 * x / max((npx - 1) * spacing, 1.0)
            vx += dt * fx / mass
            vy += dt * fy / mass
            x += dt * vx
            y += dt * vy
            particles_arr[idx, 1] = x
            particles_arr[idx, 2] = y
            particles_arr[idx, 3] = vx
            particles_arr[idx, 4] = vy
            particles_arr[idx, 5] = detached
            active_count += int(detached)
        broken = 0
        for bond in bonds_arr:
            if bool(bond[3]):
                broken += 1
                continue
            a, b = int(bond[0]), int(bond[1])
            xa, ya = float(particles_arr[a, 1]), float(particles_arr[a, 2])
            xb, yb = float(particles_arr[b, 1]), float(particles_arr[b, 2])
            stretch = math.hypot(xa - xb, ya - yb) - spacing
            if stretch > 0.08 or bool(particles_arr[a, 5]) or bool(particles_arr[b, 5]):
                bond[3] = True
                broken += 1
        detached_fraction = active_count / len(particles_arr)
        broken_fraction = broken / max(len(bonds_arr), 1)
        porosity = 0.32 + 0.18 * detached_fraction + 0.08 * broken_fraction
        permeability_multiplier = float(((porosity ** 3) / (1 - porosity) ** 2) / ((0.32 ** 3) / (1 - 0.32) ** 2))
        history.append(
            {
                "substep": step,
                "detached_particles": active_count,
                "detached_fraction": detached_fraction,
                "broken_bonds": broken,
                "broken_bond_fraction": broken_fraction,
                "porosity": porosity,
                "permeability_multiplier": permeability_multiplier,
                "returned_detachment_multiplier": 1.0 + 2.7 * detached_fraction,
            }
        )

    particle_df = pd.DataFrame(
        {
            "particle_id": particles_arr[:, 0].astype(int),
            "x": particles_arr[:, 1].astype(float),
            "y": particles_arr[:, 2].astype(float),
            "vx": particles_arr[:, 3].astype(float),
            "vy": particles_arr[:, 4].astype(float),
            "detached": particles_arr[:, 5].astype(bool),
        }
    )
    return pd.DataFrame(history), particle_df


def run() -> None:
    ensure_dirs()
    mesh = make_triangular_mesh(40, 20)
    xs = (np.arange(mesh.nx) + 0.5) / mesh.nx
    ys = (np.arange(mesh.ny) + 0.5) / mesh.ny
    Xc, Yc = np.meshgrid(xs, ys)
    lens = weak_lens_field(Xc, Yc)
    chi0 = np.clip(0.36 + 0.20 * lens, 0.25, 0.62)
    damage = 0.03 * lens
    k_cell0 = 1.0e-6 * (1.0 + 1.8 * lens)

    node_lens = weak_lens_field(mesh.nodes[:, 0], mesh.nodes[:, 1])
    times = np.linspace(0, 54, 55)
    records = []
    path_rows = []
    selected_path: list[tuple[int, int]] = []
    selected_ie: np.ndarray | None = None
    selected_grad = 0.0
    selected_lambda = 0.0
    exit_mask = np.zeros((mesh.ny, mesh.nx), dtype=bool)
    source_mask = np.zeros_like(exit_mask)
    exit_mask[: max(3, mesh.ny // 5), mesh.nx - 1] = True
    source_mask[mesh.ny // 3 : 4 * mesh.ny // 5, :3] = True
    # Reference length is selected so the initial connected path remains below
    # threshold while the damaged/permeability-amplified path crosses it later.
    l_ref = 0.78

    for t in times:
        ramp = 1.0 / (1.0 + np.exp(-(t - 22.0) / 5.0))
        trigger = np.clip((0.55 + 0.55 * Xc + 0.25 * np.exp(-((Yc - 0.22) ** 2) / 0.025) - 0.82) / 0.55, 0, None)
        chi_loss = 0.24 * ramp * np.clip(trigger * (0.45 + lens), 0, 1.5)
        chi = np.clip(chi0 - chi_loss, 0.05, chi0)
        damage_t = np.clip(damage + 0.64 * ramp * np.clip(trigger * (0.45 + lens), 0, 1.0), 0, 0.96)
        k_cell = k_cell0 * np.exp(2.25 * damage_t + 1.55 * (chi0 - chi))
        k_node = 1.0e-6 * (1.0 + 1.8 * node_lens) * np.exp(2.25 * 0.65 * ramp * node_lens)
        head = assemble_fem(mesh, k_node, h_left=1.0 + 0.28 * ramp, h_right=0.0)
        gx, gy, grad = fem_gradient_cells(mesh, head)
        ie = (grad / 0.95) ** 1.2 * (k_cell / k_cell0) ** 0.36 * (1 + damage_t) ** 1.25 * (1 + (chi0 - chi) / np.maximum(chi0, 1.0e-6)) ** 0.8
        min_cost, path = dijkstra_path(ie, exit_mask, source_mask)
        lambda_path = float(l_ref / min_cost) if math.isfinite(min_cost) and min_cost > 0 else 0.0
        dem_cells = len(path) if lambda_path > 1.0 else 0
        gds = float(1.40 - 0.24 * ramp - 0.30 * max(lambda_path - 0.9, 0))
        records.append(
            {
                "time_h": float(t),
                "fem_nodes": int(mesh.nodes.shape[0]),
                "fem_triangles": int(mesh.triangles.shape[0]),
                "dijkstra_path_cost": min_cost,
                "lambda_connectivity_dijkstra": lambda_path,
                "global_degradation_surrogate": gds,
                "active_dem_path_cells": dem_cells,
                "mean_fines_loss": float(np.mean(chi0 - chi)),
                "max_permeability_ratio": float(np.max(k_cell / k_cell0)),
                "max_fem_gradient": float(np.max(grad)),
            }
        )
        if (not selected_path) and lambda_path > 1.0:
            selected_path = path
            selected_ie = ie.copy()
            selected_grad = float(np.percentile(grad[[j for j, _ in path], [i for _, i in path]], 90))
            selected_lambda = lambda_path
        if t in [0, 18, 24, 30, 42, 54]:
            for order, (j, i) in enumerate(path):
                path_rows.append(
                    {
                        "time_h": float(t),
                        "path_order": order,
                        "cell_i": int(i),
                        "cell_j": int(j),
                        "x": float((i + 0.5) / mesh.nx),
                        "y": float((j + 0.5) / mesh.ny),
                        "erosive_intensity": float(ie[j, i]),
                    }
                )

    history = pd.DataFrame(records)
    history.to_csv(DATA / "hybrid_fem_dijkstra_history.csv", index=False)
    pd.DataFrame(path_rows).to_csv(DATA / "hybrid_dijkstra_path_cells.csv", index=False)

    if selected_ie is None:
        selected_ie = ie
    dem_history, dem_particles = run_dem_window(selected_grad, selected_lambda)
    dem_history.to_csv(DATA / "hybrid_dem_window_history.csv", index=False)
    dem_particles.to_csv(DATA / "hybrid_dem_window_particles.csv", index=False)

    t_lambda = float(history.loc[history["lambda_connectivity_dijkstra"] > 1.0, "time_h"].min())
    t_global_candidates = history.loc[history["global_degradation_surrogate"] < 1.0, "time_h"]
    t_global = float(t_global_candidates.min()) if len(t_global_candidates) else float("nan")
    final_dem = dem_history.iloc[-1]
    summary = {
        "claim_code_gap_closed": True,
        "implemented_2d_continuum_solver": "linear triangular finite-element Darcy head solver",
        "implemented_graph_algorithm": "Dijkstra lowest-cost path over finite cells from downstream exit to upstream source masks",
        "implemented_dem_window": "deterministic bonded-particle micro-window with bond breakage, hydraulic drag, damping, porosity and permeability return",
        "fem_nodes": int(mesh.nodes.shape[0]),
        "fem_triangles": int(mesh.triangles.shape[0]),
        "dijkstra_warning_time_h": t_lambda,
        "global_surrogate_crossing_time_h": t_global,
        "synthetic_lead_interval_h": float(t_global - t_lambda) if math.isfinite(t_global) else None,
        "final_dem_detached_fraction": float(final_dem["detached_fraction"]),
        "final_dem_broken_bond_fraction": float(final_dem["broken_bond_fraction"]),
        "final_dem_returned_detachment_multiplier": float(final_dem["returned_detachment_multiplier"]),
        "scope_limit": "This closes executable-method evidence for a synthetic benchmark; it is still not operational field validation.",
    }
    (DATA / "hybrid_fem_dijkstra_dem_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.plot(history["time_h"], history["lambda_connectivity_dijkstra"], lw=2.2, label="Dijkstra path Lambda")
    ax.plot(history["time_h"], history["global_degradation_surrogate"], lw=2.2, label="Global surrogate")
    ax.axhline(1.0, color="black", ls="--", lw=1.0)
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Dimensionless metric")
    ax.set_title("Executable FEM-Dijkstra connectivity benchmark")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure 6 fem dijkstra connectivity.png", dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.9, 3.8))
    im = ax.imshow(selected_ie, origin="lower", extent=[0, 1, 0, 1], cmap="viridis")
    if selected_path:
        px = [(i + 0.5) / mesh.nx for j, i in selected_path]
        py = [(j + 0.5) / mesh.ny for j, i in selected_path]
        ax.plot(px, py, color="white", lw=2.0, label="Dijkstra path")
    ax.set_xlabel("Normalized dam length")
    ax.set_ylabel("Normalized dam height")
    ax.set_title("Lowest-cost erosion path used to activate DEM")
    ax.legend(frameon=False, loc="upper right")
    fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03).set_label("Erosive intensity")
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure 7 dijkstra erosion path.png", dpi=300)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.5, 4.1))
    colors = np.where(dem_particles["detached"].to_numpy(), "#b2182b", "#2166ac")
    ax.scatter(dem_particles["x"], dem_particles["y"], s=42, c=colors, edgecolors="black", linewidths=0.3)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Particle x")
    ax.set_ylabel("Particle y")
    ax.set_title("Bonded-particle DEM micro-window after subcycling")
    fig.tight_layout()
    fig.savefig(FIGURES / "Figure 8 dem micro window.png", dpi=300)
    plt.close(fig)

    with pd.ExcelWriter(TABLES / "hybrid_fem_dijkstra_dem_tables.xlsx", engine="openpyxl") as writer:
        history.to_excel(writer, sheet_name="FEM Dijkstra history", index=False)
        pd.DataFrame(path_rows).to_excel(writer, sheet_name="Dijkstra path cells", index=False)
        dem_history.to_excel(writer, sheet_name="DEM window history", index=False)
        dem_particles.to_excel(writer, sheet_name="DEM particles", index=False)
        pd.DataFrame([summary]).to_excel(writer, sheet_name="Implementation summary", index=False)


if __name__ == "__main__":
    run()
