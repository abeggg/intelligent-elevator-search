# Intelligent Elevator Search

## Project Overview

State-space search for a capacity-constrained elevator, comparing BFS, A*, greedy search and an experimental domain-specific A* tie breaker.

## Problem Statement

Serve every (origin,destination) request in a 50-floor building using UP, DOWN, IN and OUT actions. Every action has unit cost; the objective is total operation count.

## Technologies Used

Python standard library only: deque, heapq, itertools, csv and statistics.

## Methodology

Canonical sorted tuples represent current floor, onboard destinations and waiting requests. BFS provides a unit-cost reference; informed methods use four lower-bound heuristics. Directional A* changes tie ordering while retaining f=g+h3 as its primary key.

## Architecture / Algorithms

h0=0; h1=farthest relevant-floor distance; h2=vertical span plus partial mandatory service count; h3=span + nearest endpoint distance + onboard count + twice waiting count. The directional variant prioritizes service opportunities and relevant-floor distance within equal-f ties.

## Experimental Setup

Three fixed synthetic instances; start/capacity/requests are stored in `INSTANCIAS`. The report uses medians over 9 runs. Preparation repeated all 21 instance/algorithm combinations 9 times.

## Results and Evaluation

| Instance | Optimal cost | BFS expanded | A* h3 expanded | Directional A* expanded |
|---|---:|---:|---:|---:|
| Easy | 12 | 76 | 21 | 20 |
| Medium | 50 | 2,231 | 328 | 235 |
| Hard | 92 | 10,445 | 1,792 | 1,370 |

Costs and expansion counts exactly matched the report. New timings are in [reproduced results](results/reproduced_2026-11-10.csv). Fewer expansions did **not** make Directional A* faster than A* h3 in these runs. Greedy search returned costs 67 and 123 on medium/hard instances.

## Installation and Usage

```bash
python elevadores_busca.py --repeticoes 9 --csv results/new-run.csv
```

The recovered script uses the original Portuguese CLI flag. [Original report](docs/original-report.pdf) contains the source appendix.

## Limitations and Future Improvements

The standalone original `.py` was not found. This review copy is transcribed from Appendix A with PDF wrapping/indentation repaired; algorithms, successor ordering, priority keys and instances were preserved. It is identified as recovered source. Three small instances do not establish broad performance. Multi-elevator control and the optional GenAI comparison were not implemented.

## Academic Context and Credits

UFSC Artificial Intelligence, Prof. Jomi F. Hübner. Academic report by Kauan Abegg, based on course state-space search concepts and Russell & Norvig. The supplied report cites course search examples, but the original external example code was not supplied for a line-by-line provenance comparison.

See [academic context](ACADEMIC_CONTEXT.md) and [publication review notes](PUBLICATION_NOTES.md).
