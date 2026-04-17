from typing import TypeAlias, Sequence


SudukoBoard: TypeAlias = list[list[int]] | list[list[str]]

def make_suduko_board(base: int) -> SudukoBoard:
    from random import sample
    
    side: int = base*base
    squares: int = side*side
    empties: int = squares * 3//4
    
    def pattern(row: int, col: int) -> int: 
        return (base*(row%base)+row//base+col)%side

    def shuffle(s: Sequence[int]) -> Sequence[int]: 
        return sample(s,len(s))
     
    rBase: range = range(base) 
    rows: list[int] = [ g*base + r for g in shuffle(rBase) for r in shuffle(rBase) ] 
    cols: list[int] = [ g*base + c for g in shuffle(rBase) for c in shuffle(rBase) ]
    nums: Sequence[int] = shuffle(range(1,side+1))

    board: SudukoBoard = [ [nums[pattern(r,c)] for c in cols] for r in rows ]
    
    for p in sample(range(squares),empties):
        board[p//side][p%side] = 0
        
    return board


def print_board(board: SudukoBoard, base: int) -> None:
    side: int = base*base
    
    def expandLine(line: str) -> str:
        return line[0]+line[5:9].join([line[1:5]*(base-1)]*base)+line[9:13]
    
    line0: str = expandLine("╔═══╤═══╦═══╗")
    line1: str = expandLine("║ . │ . ║ . ║")
    line2: str = expandLine("╟───┼───╫───╢")
    line3: str = expandLine("╠═══╪═══╬═══╣")
    line4: str = expandLine("╚═══╧═══╩═══╝")

    symbol: str = " 1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    nums: SudukoBoard = [ [""]+[symbol[n] for n in row] for row in board ]
    
    print(line0)
    for r in range(1,side+1):
        print( "".join(n+s for n,s in zip(nums[r-1],line1.split("."))) )
        print([line2,line3,line4][(r%side==0)+(r%base==0)])