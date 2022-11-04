from stockfish import Stockfish

sf = Stockfish(path='/opt/homebrew/bin/stockfish')

sf.set_depth(10)
# sf.set_fen_position('4r1k1/5ppp/1p1b1p2/4q3/1P6/7P/2Q2PP1/3R2K1 w - - 3 26') # Black advantage
sf.set_fen_position('4r1k1/5ppp/1pQb1p2/4q3/1P6/7P/5PP1/3R2K1 b - - 4 26') # Black mate in 2

print(sf.get_top_moves(5))
# print(sf.get_evaluation())
