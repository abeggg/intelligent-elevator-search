from pathlib import Path
import runpy
n=runpy.run_path(str(Path(__file__).resolve().parents[1]/'elevadores_busca.py'))
expected={'Facil':[(12,76),(12,76),(12,38),(12,37),(12,21),(12,13),(12,20)],'Media':[(50,2231),(50,2231),(50,839),(50,648),(50,328),(67,99),(50,235)],'Dificil':[(92,10445),(92,10445),(92,5688),(92,3283),(92,1792),(123,228),(92,1370)]}
for name,instance in n['INSTANCIAS'].items():
    for (algorithm,fn),target in zip(n['ALGORITMOS'].items(),expected[name]):
        r=fn(instance);assert (r['custo'],r['nos'])==target,(name,algorithm,r)
        state=n['estado'](instance['andar'],(),instance['demandas'])
        for action in r['caminho']:
            candidates=dict(n['sucessores'](state,instance['capacidade']))
            assert action in candidates
            state=candidates[action]
            assert len(state[1])<=instance['capacidade']
        assert n['meta'](state)
print('All 21 report costs/node counts matched; every returned plan replayed successfully')
