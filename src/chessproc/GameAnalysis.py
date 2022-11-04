import chess
import chess.pgn
from functools import cached_property
import io
from multiprocessing import Pool
import pandas as pd
import re
from stockfish import Stockfish
from typing import List


class GameAnalysis:

    def __init__(self, sf: Stockfish, pgn: str, sf_depth: int = 10, verbose: bool = False) -> None:
        self.sf_depth = sf_depth
        self.sf = sf
        self.sf.set_depth(self.sf_depth)
        self.pgn = pgn
        self.verbose = verbose

        # Initialize the game object
        self.game = pgn
        self.identifier = self.pgnheaders['Link'].split('/')[-1]
    
    @property
    def game(self):
        return self._game
    
    @game.setter
    def game(self, pgn):
        try:
            self._game = chess.pgn.read_game(io.StringIO(pgn))
        except Exception as e:
            print(f"Error creating game object: {e}")
    
    @property
    def pgnheaders(self):
        return dict(self.game.headers)
    
    @cached_property
    def analysis(self):
        
        # Initialize all lists
        moves = []
        MoveNumber = []
        wb = []
        BestMove = []
        BestMoveEval = []
        TopMoves = []
        MoveRank = []
        MoveCorr = []
        MoveEval = []
        EvalDifference = []

        # Parse clock
        re_clock = re.compile(r'[0-9]*[.]+ [a-zA-Z0-9+#=/-]* \{\[%clk ([0-9:.]*)\]\}')
        clock = re_clock.findall(self.pgn)

        # Computing the best moves
        uci_moves = self.game.mainline_moves()
        uci_moves_list = list(uci_moves)
        move_sets = [uci_moves_list[:x] for x in range(1, len(uci_moves_list) + 1)]
        with Pool() as p:
            evals = list(p.map(compute, move_sets))
        

        for i, move in enumerate(self.game.mainline_moves()):
            if self.verbose:
                print(f"Move Number: {i}, Move: {move}")

            # Note the move and related information
            moves.append(move.uci())
            
            MoveNumber.append(i // 2 + 1)
            wb.append("B" if (i % 2) else "W")

            # Calculate the evaluation and best moves
            TopMoves.append(evals[i][1])                    # Changed
            BestMove.append(TopMoves[-1][0]["Move"])
            if TopMoves[-1][0]["Mate"]:
                BestMoveEval.append(100)
            else:
                BestMoveEval.append(TopMoves[-1][0]["Centipawn"])

            # If move is found in list
            # - set move rank and eval from list
            # Else
            # - make move and get evaluation
            # - set move rank to None
            for idx, potential_move in enumerate([x["Move"] for x in TopMoves[-1]]):
                # If the move matches one of the top "n" moves
                if potential_move == moves[-1]:
                    MoveRank.append(idx)
                    break                               # Changed
            else:
                # TODO: There is a potential bug here where there are more than five paths to mate, getting the evaluation could return a non-number
                MoveRank.append(6)
            
            MoveEval.append(evals[i][0]['value'])           # Changed
            
            # If there is mate, then 
            EvalDifference.append(abs(MoveEval[-1] - BestMoveEval[-1]))
            MoveCorr.append(None)
        
        return pd.DataFrame(data={"MoveNumber": MoveNumber, 
                                  "WB": wb, 
                                  "Move": moves, 
                                  "Clock": clock,
                                  "MoveEval": MoveEval, 
                                  "BestMove": BestMove, 
                                  "BestMoveEval": BestMoveEval, 
                                  "TopMoves": TopMoves, 
                                  "MoveRank": MoveRank, 
                                  "MoveCorr": MoveCorr,
                                  "MoveLoss": EvalDifference})
    
    def save_analysis(self):
        """Save analysis for future access, can check directory for matching id before analyzing"""
        pass
        

def compute(moves: List[str]):
    print(f"Starting for move: {len(moves)}")
    # Initialize sf
    sf = Stockfish(path='/opt/homebrew/bin/stockfish')
    sf.set_depth(18)

    # Make all moves given except one
    uci_moves = [x.uci() for x in moves]
    sf.make_moves_from_current_position(uci_moves[:-1])

    # Evaluate top 5 moves
    top_5 = sf.get_top_moves(5)

    # Make the final move
    sf.make_moves_from_current_position([uci_moves[-1]])

    # Get an evaluation if not in the top 5
    pos_eval = sf.get_evaluation()

    # Return the evaluation and the top 5 list
    return (pos_eval, top_5)

# for i in range(len(moves)):
#     with Pool(len(moves)) as p:
#         p.map(compute, move_sets)

# move_sets = [moves[:x] for x in range(1, len(moves) + 1)]

