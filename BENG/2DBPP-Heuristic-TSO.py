# Heuristic coded by:
# Oscar Garza Hinojosa
# Derek Alejandro Sauceda Morales
# Guillermo Vladimir Flores Báez
# Fernando Yahir García Dávila
import os
import math
import time
import json
import logging
from dataclasses import dataclass
from typing import List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

@dataclass
class Rect:
    id: str
    w: int
    h: int
    x: int = 0
    y: int = 0
    rotated: bool = False

    @property
    def area(self) -> int:
        return self.w * self.h


class Bin:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.placements: List[Rect] = []
        self.candidates: List[Tuple[int, int]] = [(0, 0)]

    def _check_overlap(self, r1: Rect, r2: Rect) -> bool:
        if (r2.x >= r1.x + r1.w or
            r1.x >= r2.x + r2.w or
            r2.y >= r1.y + r1.h or
            r1.y >= r2.y + r2.h):
            return False
        return True

    def can_place(self, candidate: Rect) -> bool:
        return all(not self._check_overlap(existing, candidate) for existing in self.placements)

    def place(self, obj: Rect) -> bool:
        for rotated in (False, True):
            w, h = obj.w, obj.h
            if rotated:
                if obj.w == obj.h:
                    continue
                w, h = obj.h, obj.w

            for x, y in sorted(self.candidates, key=lambda p: (p[1], p[0])):
                if x + w > self.width or y + h > self.height:
                    continue
                candidate = Rect(obj.id, w, h, x, y, rotated)
                if self.can_place(candidate):
                    self.placements.append(candidate)
                    new_positions = [(x + w, y), (x, y + h)]
                    for nx, ny in new_positions:
                        if nx < self.width and ny < self.height and (nx, ny) not in self.candidates:
                            self.candidates.append((nx, ny))
                    return True
        return False


def read_objects(filename: str) -> Tuple[int, int, List[Rect]]:
    objects: List[Rect] = []
    with open(filename, 'r') as f:
        lines = [ln.strip() for ln in f if ln.strip()]

    m = int(lines[0].split()[0])
    bin_w, bin_h = map(int, lines[1].split())

    for ln in lines[2:]:
        parts = ln.split()
        if len(parts) < 3:
            continue
        id_, w_s, h_s = parts[:3]
        try:
            w, h = int(w_s), int(h_s)
        except ValueError:
            logging.warning(f"Skipping malformed line: '{ln}'")
            continue
        objects.append(Rect(id_, w, h))

    if len(objects) != m:
        logging.warning(f"Declared {m} objects, but parsed {len(objects)}")
    return bin_w, bin_h, objects


def area_verification(objects: List[Rect], bin_w: int, bin_h: int) -> Tuple[int, int, int]:
    total_area = sum(o.area for o in objects)
    container_area = bin_w * bin_h
    min_bins = math.ceil(total_area / container_area)
    return total_area, container_area, min_bins


def bin_packing(objects: List[Rect], bin_w: int, bin_h: int) -> List[Bin]:
    sorted_objs = sorted(objects, key=lambda o: o.area, reverse=True)
    bins: List[Bin] = []

    for obj in sorted_objs:
        placed = False
        for b in bins:
            if b.place(obj):
                placed = True
                break
        if not placed:
            new_bin = Bin(bin_w, bin_h)
            if new_bin.place(obj):
                bins.append(new_bin)
            else:
                logging.error(f"Object {obj.id} does not fit in an empty bin.")
    return bins


def local_search_first_improvement(bins: List[Bin], bin_w: int, bin_h: int) -> List[Bin]:
    import copy
    bins = copy.deepcopy(bins)
    for i in range(len(bins)):
        bin_i = bins[i]
        for r in bin_i.placements[:]:
            for j in range(len(bins)):
                if i == j:
                    continue
                target = bins[j]
                bin_i.placements.remove(r)
                if target.place(r):
                    if not bin_i.placements:
                        bins = [b for idx, b in enumerate(bins) if idx != i]
                    return bins
                bin_i.placements.append(r)
    return bins


def local_search_best_improvement(bins: List[Bin], bin_w: int, bin_h: int) -> List[Bin]:
    import copy
    best_bins = copy.deepcopy(bins)
    best_score = len(bins)
    for i in range(len(bins)):
        for r in bins[i].placements:
            for j in range(len(bins)):
                if i == j:
                    continue
                candidate_bins = copy.deepcopy(bins)
                bin_i = candidate_bins[i]
                target = candidate_bins[j]
                bin_i.placements = [x for x in bin_i.placements if x.id != r.id]
                if target.place(r):
                    candidate_bins = [b for b in candidate_bins if b.placements]
                    if len(candidate_bins) < best_score:
                        best_score = len(candidate_bins)
                        best_bins = candidate_bins
    return best_bins


def plot_containers(bins: List[Bin]):
    n = len(bins)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5))
    if n == 1:
        axes = [axes]
    for idx, b in enumerate(bins):
        ax = axes[idx]
        ax.add_patch(patches.Rectangle((0, 0), b.width, b.height, linewidth=2, edgecolor='black', facecolor='none'))
        ax.set_xlim(0, b.width)
        ax.set_ylim(0, b.height)
        ax.set_aspect('equal')
        ax.set_title(f"Bin {idx+1}")
        for i, r in enumerate(b.placements):
            ax.add_patch(patches.Rectangle((r.x, r.y), r.w, r.h, linewidth=1, edgecolor='black', facecolor=f'C{i}', alpha=0.5))
            orient = 'R' if r.rotated else 'O'
            ax.text(r.x + r.w/2, r.y + r.h/2, f"{r.id} ({orient})", ha='center', va='center', fontsize=8)
    plt.tight_layout()
    plt.show()


def export_to_json(bins: List[Bin], min_bins: int, total_area: int, bin_area: int, gap: float, exec_time: float, filename: str="output.json"):
    result = {"bins_used": len(bins), "min_theoretical_bins": min_bins, "total_objects_area": total_area,
              "single_bin_area": bin_area, "gap_percentage": round(gap,2), "execution_time_seconds": round(exec_time,4), "bins": []}
    for i, b in enumerate(bins):
        result["bins"].append({"bin_number": i+1,
                                 "objects":[{"id":r.id, "width":r.w, "height":r.h, "x":r.x, "y":r.y, "rotated":r.rotated} for r in b.placements]})
    with open(filename, 'w') as f:
        json.dump(result, f, indent=4)
    logging.info(f"Detailed Results exported to: {filename}")


def main():
    filename = input("Enter full path of the instance file: ").strip().strip('"')
    if not os.path.isfile(filename): logging.error(f"File not found: {filename}"); return
    # Ejecutar packing inicial
    start = time.time()
    bin_w, bin_h, objs = read_objects(filename)
    total_area, cont_area, min_bins = area_verification(objs, bin_w, bin_h)
    bins_used = bin_packing(objs, bin_w, bin_h)
    gap = (len(bins_used)-min_bins)/min_bins*100
    pack_time = time.time() - start
    logging.info(f"Used {len(bins_used)} bins (packing time: {pack_time:.4f} s)")
    export_to_json(bins_used, min_bins, total_area, cont_area, gap, pack_time, filename="output_original.json")
    if len(bins_used)<=10: plot_containers(bins_used)
    else: logging.info("Graphical representation skipped: >10 bins")

    answer = input("Perform Local Search? (y/n): ").strip().upper()
    if answer!="Y":
        logging.info("Local search skipped.")
        return

    method = input("Specify Method: FirstImprovement or BestImprovement (fi/bi)? ").strip().lower()
    if method=="fi":
        # Medir tiempo de FirstImprovement
        t0 = time.time()
        improved = local_search_first_improvement(bins_used, bin_w, bin_h)
        ls_time = time.time() - t0
        mname = 'FirstImprovement'
    elif method=="bi":
        # Medir tiempo de BestImprovement
        t0 = time.time()
        improved = local_search_best_improvement(bins_used, bin_w, bin_h)
        ls_time = time.time() - t0
        mname = 'BestImprovement'
    else:
        logging.error("Unknown method; aborting local search.")
        return

    logging.info(f"Tiempo {mname}: {ls_time:.4f} s")

    if len(improved)<len(bins_used):
        logging.info("Local search found an improved solution.")
        igap = (len(improved)-min_bins)/min_bins*100
        export_to_json(improved, min_bins, total_area, cont_area, igap, ls_time, filename="output_improved.json")
        if len(improved)<=10: plot_containers(improved)
        else: logging.info("Improved graphical representation skipped: >10 bins")
    else:
        logging.info("No improvement found. Keeping original solution.")

if __name__=="__main__":
    main()
