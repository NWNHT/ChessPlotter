import asyncio
from stockfish import Stockfish
import time

from chessproc import pgnproc
from chessproc.GameAnalysis import GameAnalysis

if __name__ == '__main__':
	start = time.perf_counter()
	# Create sf
	sf = Stockfish(path='/opt/homebrew/bin/stockfish')

	# Get pgn string
	duda = (pgnproc.get_parquet_by_username('Polish_fighter3000')
		       .query('White == "Hikaru" | Black == "Hikaru"')
		       .iloc[3])

	# Create gameanalysis object
	g = GameAnalysis(pgn=duda.pgn, verbose=True, check_cache=False)
	print("created object")


	print("Starting Analysis")
	print(g.analysis)
	print("Ending Analysis")

	print("Starting Save")
	g.save_analysis()
	print("File Saved")


	print(time.perf_counter() - start)

