import chess
import chess.pgn
from functools import cached_property
import io
from multiprocessing import Pool
import os
import pandas as pd
import re
from stockfish import Stockfish
from typing import List

global_game_directory = '/Users/lucasnieuwenhout/Documents/Programming/Python/Projects/ChessPlotter/pgns/ProcessedGames/'

class GameAnalysis:

    def __init__(self, pgn: str, 
                       sf_depth: int = 10, 
                       verbose: bool = False, 
                       check_cache: bool = True,
                       cache_directory: str = global_game_directory,
                       mate_eval_fill: int = 1000) -> None:

        # Settings
        self.sf_depth = sf_depth
        self.verbose = verbose
        self.check_cache = check_cache
        self.cache_directory = cache_directory
        self.mate_eval_fill = mate_eval_fill

        # Initialize the game object
        self.game = pgn

        # Game information
        self.pgn = pgn
        self.identifier = self.pgnheaders['Link'].split('/')[-1]
        self.white_player = self.pgnheaders['White']
        self.black_player = self.pgnheaders['Black']
        self.result = self.pgnheaders['Result']

    @property
    def game(self) -> chess.pgn.GameNode.game:
        return self._game
    
    @game.setter
    def game(self, pgn) -> None:
        try:
            self._game = chess.pgn.read_game(io.StringIO(pgn))
        except Exception as e:
            print(f"Error creating game object: {e}")
    
    @property
    def pgnheaders(self) -> dict:
        """Headers of the pgn file, taken from _game"""
        return dict(self.game.headers)
    
    @cached_property
    def analysis(self) -> pd.DataFrame:
        """Cached property analysis, dataframe with data and for each move"""

        # Check if the game has already been analyzed, if so, read
        if self.check_cache and self.identifier in [x.split('_')[0] for x in os.listdir(self.cache_directory)]:
            filename = self.cache_directory + [i for i in os.listdir(self.cache_directory) if i.split('_')[0] == self.identifier][0]
            print("Reading File")
            return pd.read_parquet(filename)
        
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
        MateIn = []

        # Parse clock
        # TODO: Only parse or only include clock if it is present, can test that it is the same length
        re_clock = re.compile(r'[0-9]*[.]+ [a-zA-Z0-9+#=/-]* \{\[%clk ([0-9:.]*)\]\}')
        clock = re_clock.findall(self.pgn)

        # Computing the best moves and evaluations
        uci_moves_list = list(self.game.mainline_moves())
        move_sets = [uci_moves_list[:x] for x in range(1, len(uci_moves_list) + 1)]
        with Pool() as p:
            evals = list(p.map(evaluate_position, move_sets))

        # Parse the moves and evaluations, creating lists for the dataframe
        for i, move in enumerate(self.game.mainline_moves()):
            if self.verbose:
                print(f"Move Number: {i}, Move: {move}")

            # Note the move and related information
            moves.append(move.uci())
            
            MoveNumber.append(i // 2 + 1)
            wb.append("B" if (i % 2) else "W")

            # Calculate the evaluation and best moves
            TopMoves.append(evals[i][1])
            BestMove.append(evals[i][1][0]["Move"]) # This takes the ith eval, second element of output tuple, first move, select Move

            BestMoveEval.append(evals[i][1][0]["Centipawn"] if (evals[i][1][0]["Centipawn"] is not None) else evals[i][1][0]["Mate"]/abs(evals[i][1][0]["Mate"] or 1) * self.mate_eval_fill)
            MateIn.append(TopMoves[-1][0]["Mate"])

            for idx, potential_move in enumerate([x["Move"] for x in TopMoves[-1]]):
                # If the move matches one of the top "n" moves
                if potential_move == moves[-1]:
                    MoveRank.append(idx)
                    break
            else:
                # TODO: There is a potential bug here where there are more than five paths to mate, getting the evaluation could return a non-number
                MoveRank.append(6)
            
            MoveEval.append(evals[i][0]['value'] if evals[i][0]['type'] == 'cp' else evals[i][0]['value']/(abs(evals[i][0]['value']) or 1) * self.mate_eval_fill)
            if MoveEval[-1] is not None and BestMoveEval[-1] is not None:
                EvalDifference.append(abs(MoveEval[-1] - BestMoveEval[-1]))
            else:
                EvalDifference.append(None)
            MoveCorr.append(None)
        
        df =  pd.DataFrame(data={"MoveNumber": MoveNumber, 
                                  "WB": wb, 
                                  "Move": moves, 
                                  "Clock": clock,
                                  "MoveEval": MoveEval, 
                                  "BestMove": BestMove, 
                                  "BestMoveEval": BestMoveEval, 
                                  "MateIn": MateIn,
                                  "TopMoves": TopMoves, 
                                  "MoveRank": MoveRank, 
                                  "MoveCorr": MoveCorr,
                                  "MoveLoss": EvalDifference})
        
        df.loc[df['MateIn'].notnull(), 'MoveLoss'] = None
        
        return df
    
    def save_analysis(self, directory: str = global_game_directory) -> None:
        """Save analysis for future access, can check directory for matching id before analyzing"""
        filename = directory + self.identifier + f"_{self.white_player}_{self.black_player}_{self.result}_{self.sf_depth}.parquet"
        try:
            self.analysis.to_parquet(filename)
        except Exception as e:
            print(f"Saving file analysis failed: {e}")
        

def evaluate_position(moves: List[str], depth: int = 18):
    """Evaluate a position give a list of moves"""
    print(f"Starting for move: {len(moves)}")
    # Initialize sf
    sf = Stockfish(path='/opt/homebrew/bin/stockfish')
    sf.set_depth(depth)

    # Make all moves given except one
    uci_moves = [x.uci() for x in moves]
    sf.make_moves_from_current_position(uci_moves[:-1])

    # Evaluate top 5 moves
    top_5 = sf.get_top_moves(5)

    # Make the final move
    sf.make_moves_from_current_position([uci_moves[-1]])

    # Some checking to avoid an extra evaluation move is inside the top 5
    for move in top_5:
        if move['Move'] == uci_moves[-1]:
            if move['Mate'] is None:
                pos_eval = {'type': 'cp', 'value': move['Centipawn']}
                break
            else:
                pos_eval = {'type': 'mate', 'value': move['Mate']}
                break
    else:
        pos_eval = sf.get_evaluation()

    # pos_eval returns the evaluation if there is no mate, or the mate number if there is, integer, black is negative

    # Return the evaluation and the top 5 list
    return (pos_eval, top_5)
