from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias, Callable, Iterable, TypeVar
import random
import math

if TYPE_CHECKING:
    from .suduko_game import SudukoBoard
    
# A Moth is now a list of permutations (one for each 3x3 block)
Moth: TypeAlias = list[list[int]]

T = TypeVar("T")
P = TypeVar("P")

def cmap(func: Callable[[P], T], iterable: Iterable[P]) -> list[T]:
    return list(map(func, iterable))

def optimize_sudoku_mfo(initial_board: SudukoBoard, base: int, n_moths: int = 100, max_iter: int = 2000) -> SudukoBoard:
    side: int = base * base
    
    flat_initial: list[int] = []
    for r in range(side):
        for c in range(side):
            flat_initial.append(int(initial_board[r][c]))
            
    blocks_missing: dict[int, list[int]] = {}
    blocks_empty_idx: dict[int, list[int]] = {}
    
    for b_idx in range(side):
        blocks_missing[b_idx] = list(range(1, side + 1))
        blocks_empty_idx[b_idx] = []
        
    for r in range(side):
        for c in range(side):
            val: int = flat_initial[r * side + c]
            b_idx: int = (r // base) * base + (c // base)
            if val == 0:
                blocks_empty_idx[b_idx].append(r * side + c)
                continue
            if val in blocks_missing[b_idx]:
                blocks_missing[b_idx].remove(val)
                
    # Initialize Moths with random discrete permutations
    moths: list[Moth] = []
    for _ in range(n_moths):
        moth: Moth = []
        for b_idx in range(side):
            perm: list[int] = blocks_missing[b_idx].copy()
            random.shuffle(perm)
            moth.append(perm)
        moths.append(moth)

    def decode(discrete_moth: Moth) -> list[int]:
        discrete: list[int] = flat_initial.copy()
        for b_idx in range(side):
            empty_idx: int = blocks_empty_idx[b_idx]
            assigned_values: list[int] = discrete_moth[b_idx]
            for i, idx in enumerate(empty_idx):
                discrete[idx] = assigned_values[i]
        return discrete

    def evaluate_decoded(discrete: list[int]) -> int:
        fitness = 0
        for r in range(side):
            fitness += side - len(set(discrete[r*side : (r+1)*side]))
        for c in range(side):
            fitness += side - len(set([discrete[r*side + c] for r in range(side)]))
        return fitness

    flames: list[Moth] = []
    flame_fitness: list[int] = []
    
    # Run Discrete MFO Loop
    for t in range(1, max_iter + 1):
        discrete_boards: list[list[int]] = cmap(decode, moths)
        om: list[int] = cmap(evaluate_decoded, discrete_boards)
        
        sorted_pairs: list[tuple[int, Moth]] = sorted(zip(om, moths), key=lambda x: x[0])
        sorted_om: list[int] = cmap(lambda p: p[0], sorted_pairs)
        sorted_moths: list[list[list[int]]] = cmap(lambda p: list(p[1]), sorted_pairs)
        
        if t == 1:
            flames = sorted_moths
            flame_fitness = sorted_om
        else:
            merged_pairs: list[tuple[int, Moth]] = sorted(zip(flame_fitness + om, flames + moths), key=lambda x: x[0])
            flames = cmap(lambda p: list(p[1]), merged_pairs[:n_moths])
            flame_fitness = cmap(lambda p: p[0], merged_pairs[:n_moths])
            
        if t % 100 == 0:
            print(f"Iteration {t} | Best Fitness: {flame_fitness[0]}")
            
        if flame_fitness[0] == 0:
            print(f"Perfect solution found at iteration {t}!")
            break
            
        active_flames: int = max(1, math.floor(n_moths - t * ((n_moths - 1) / max_iter)))
        
        # Update Moth Positions (Using discrete swaps)
        for i in range(n_moths):
            flame_idx: int = i if i < active_flames else active_flames - 1
            target_flame: Moth = flames[flame_idx]
            
            new_moth: Moth = []
            for b_idx in range(side):
                # Mimic the spiral movement: take the flame's block and mutate it
                block: Moth = target_flame[b_idx].copy()
                n_missing: int = len(block)
                
                if n_missing > 1:
                    # As iterations increase, we apply fewer random swaps (spiraling closer)
                    max_swaps: int = n_missing // 2
                    current_max: int = max(1, math.ceil(max_swaps * (1 - t / max_iter)))
                    
                    num_swaps: int = random.randint(0, current_max)
                    
                    # 5% chance of major mutation to escape local optima
                    if random.random() < 0.05:
                        num_swaps = max_swaps
                        
                    for _ in range(num_swaps):
                        idx1, idx2 = random.sample(range(n_missing), 2)
                        block[idx1], block[idx2] = block[idx2], block[idx1]
                        
                new_moth.append(block)
            moths[i] = new_moth

    if flame_fitness[0] != 0:
        print(f"Algorithm finished. Best fitness found: {flame_fitness[0]}")

    best_discrete: list[int] = decode(flames[0])
    
    return cmap(lambda r: best_discrete[r*side : (r+1)*side], range(side))