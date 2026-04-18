from __future__ import annotations
from typing import TYPE_CHECKING, TypeAlias, Callable, Iterable, TypeVar
import random, math

if TYPE_CHECKING:
    from .suduko_game import  SudukoBoard
    
    
Moth: TypeAlias = list[int]

T = TypeVar("T")
P = TypeVar("P")

def cmap(func: Callable[[P], T], iterable: Iterable[P]) -> list[T]:
    return list(map(func, iterable))

def evaluate_fitness(moth: Moth, base: int) -> int:
    side: int = base * base
    fitness: int = 0
    
    # Sum of duplicate digits in rows
    for r in range(side):
        fitness += side - len(set(moth[r*side : (r+1)*side]))
        
    # Sum of duplicate digits in columns
    for c in range(side):
        fitness += side - len(set([moth[r*side + c] for r in range(side)]))
        
    # Sum of duplicate digits in subgrids
    for sr in range(base):
        for sc in range(base):
            subgrid: list[int] = []
            for r in range(base):
                for c in range(base):
                    subgrid.append(moth[(sr*base + r)*side + (sc*base + c)])
            fitness += side - len(set(subgrid))
            
    return fitness


def optimize_sudoku_mfo(initial_board: SudukoBoard, base: int, n_moths: int = 100, max_iter: int = 1000) -> SudukoBoard:
    side: int = base * base
    b: float = 1.0  # Constant defining the shape of the logarithmic spiral
    
    # Step 1: Flatten board and identify fixed constraints
    fixed_indices: set[int] = set()
    flat_initial: Moth = []
    
    for r in range(side):
        for c in range(side):
            val: int = int(initial_board[r][c])
            flat_initial.append(val)
            if val != 0:
                fixed_indices.add(r * side + c)
                
    # Initialize moth population (randomizing only the empty cells)
    moths: list[Moth] = []
    for _ in range(n_moths):
        new_moth: Moth = []
        for i in range(side * side):
            new_moth.append(
                flat_initial[i] if i in fixed_indices else random.randint(1, side)
            )
        moths.append(new_moth)
        
    flames: list[Moth] = []
    flame_fitness: list[int] = []
    
    # Step 2 & 3: Iterate through algorithm
    for t in range(1, max_iter + 1):
        
        # Evaluate fitness for all moths
        om: list[int] = cmap(lambda m: evaluate_fitness(m, base), moths)
        
        # Sort current moths by fitness
        sorted_pairs = sorted(zip(om, moths), key=lambda x: x[0])
        sorted_om: list[int] = cmap(lambda p: p[0], sorted_pairs)
        sorted_moths: list[Moth] = cmap(lambda p: list(p[1]), sorted_pairs)
        
        # Update flames based on best historical solutions
        if t == 1:
            flames = sorted_moths
            flame_fitness = sorted_om
        else:
            merged_pairs: list[tuple[int, Moth]] = sorted(zip(flame_fitness + om, flames + moths), key=lambda x: x[0])
            flames = cmap(lambda p: list(p[1]), merged_pairs[:n_moths])
            flame_fitness = cmap(lambda p: p[0], merged_pairs[:n_moths])
            
        # Perfect solution found
        if flame_fitness[0] == 0:
            print(f"Solution found at iteration {t}!")
            break
            
        # Compute active flame count to balance exploration vs. exploitation
        active_flames: int = max(1, math.floor(n_moths - t * ((n_moths - 1) / max_iter)))
        
        # Update moth positions
        for i in range(n_moths):
            for k in range(side * side):
                # Do not modify original puzzle clues
                if k in fixed_indices:
                    continue
                    
                # Assign to corresponding flame
                flame_idx: int = i if i < active_flames else active_flames - 1
                flame_val: int = flames[flame_idx][k]
                moth_val: int = moths[i][k]
                
                # Distance to flame
                D_i: float = abs(flame_val - moth_val)
                
                # Random uniform variable for spiral
                tau: float = random.uniform(-1, 1)
                
                # Calculate logarithmic spiral
                new_val_float: float = ( 
                    D_i * math.exp(b * tau) * math.cos(2 * math.pi * tau) + flame_val
                )
                
                # Clip bounds and discretize into Sudoku valid integers
                new_val: int = int(round(new_val_float))
                new_val = max(1, min(side, new_val))
                
                moths[i][k] = new_val
                
    # Reconstruct 2D board from the best flame (Best solution found)
    best_moth: Moth = flames[0]
        
    return cmap(lambda r: best_moth[r*side : (r+1)*side], range(side))