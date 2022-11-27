import chess
import chess.pgn
import io
from stockfish import Stockfish

sf = Stockfish(path='/opt/homebrew/bin/stockfish')

# with open('./example_pgn.txt', 'r') as fh:
	# game = chess.pgn.read_game(fh)

pgn = """[Event "Let's Play!"]
[Site "Chess.com"]
[Date "2021.03.28"]
[Round "-"]
[White "jesterjmf"]
[Black "girthyPolak"]
[Result "1-0"]
[CurrentPosition "r1bqkb1r/pppppQn1/2n4p/4P1p1/2BP4/2P1B2N/PP3PPP/RN2K2R b KQkq - 0 10"]
[Timezone "UTC"]
[ECO "B02"]
[ECOUrl "https://www.chess.com/openings/Alekhines-Defense-Normal-Variation-3.Bc4"]
[UTCDate "2021.03.28"]
[UTCTime "17:13:22"]
[WhiteElo "1719"]
[BlackElo "789"]
[TimeControl "1/864000"]
[Termination "jesterjmf won by checkmate"]
[StartTime "17:13:22"]
[EndDate "2021.03.30"]
[EndTime "17:59:51"]
[Link "https://www.chess.com/game/daily/323055632"]

1. e4 {[%clk 235:31:07]} 1... Nf6 {[%clk 236:06:29]} 2. e5 {[%clk 239:03:07]} 2... Nd5 {[%clk 237:25:36]} 3. Bc4 {[%clk 239:54:37]} 3... Nf4 {[%clk 239:56:06]} 4. Qf3 {[%clk 228:04:15]} 4... Ne6 {[%clk 238:41:59]} 5. d4 {[%clk 233:25:19]} 5... g6 {[%clk 239:37:22]} 6. Nh3 {[%clk 239:57:23]} 6... h6 {[%clk 237:45:08]} 7. Be3 {[%clk 239:52:24]} 7... Nc6 {[%clk 239:54:21]} 8. c3 {[%clk 239:57:37]} 8... g5 {[%clk 239:08:22]} 9. Qh5 {[%clk 231:20:06]} 9... Ng7 {[%clk 236:20:52]} 10. Qxf7# {[%clk 239:11:21]} 1-0"""

fh = io.StringIO(pgn)

game = chess.pgn.read_game(fh)

first_move = game.next()

uci = first_move.uci()
print(uci)
print(first_move.san())
print(first_move.clock())
print(first_move.board().fen())

sf.set_depth(10)
# sf.set_fen_position('4r1k1/5ppp/1p1b1p2/4q3/1P6/7P/2Q2PP1/3R2K1 w - - 3 26') # Black advantage
sf.set_fen_position('3r4/7n/5k2/5pp1/3P1K2/3BPPP1/7P/8 w - - 0 46') # black mate
# sf.set_fen_position('4r1k1/5ppp/1pQb1p2/4q3/1P6/7P/5PP1/3R2K1 b - - 4') # Black mate in 2
# sf.set_fen_position('r1bqk1nr/pppp1Qpp/2n5/2b1p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 4') # white mate

print(sf.get_top_moves(5))
# print('\n\n')
print(sf.get_evaluation())
