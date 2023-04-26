from contextlib import redirect_stdout
import pstats

with open('stats.txt', 'w') as f:
    with redirect_stdout(f):
        stats = pstats.Stats("profiler.prof")

        stats.strip_dirs()
        #stats.sort_stats(-1)
        stats.sort_stats('time')
        stats.print_stats()