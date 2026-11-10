#!/usr/bin/env python3
"""Recovered from Appendix A of Kauan Abegg's elevator search report.

PDF line wrapping and indentation were restored. Algorithms, successor order,
instances and priority keys follow the appendix; this is not an original .py file.
"""
from collections import deque
from heapq import heappush, heappop
from time import perf_counter
import argparse
import csv
import itertools
import math
import statistics


def estado(andar, dentro, esperando):
    return (int(andar), tuple(sorted(dentro)), tuple(sorted(tuple(x) for x in esperando)))


def meta(s):
    _, dentro, esperando = s
    return len(dentro) == 0 and len(esperando) == 0


def sucessores(s, capacidade):
    andar, dentro, esperando = s
    resposta = []
    if andar < 50:
        resposta.append(('UP', (andar + 1, dentro, esperando)))
    if andar > 1:
        resposta.append(('DOWN', (andar - 1, dentro, esperando)))
    if andar in dentro:
        novo_dentro = list(dentro)
        novo_dentro.remove(andar)
        resposta.append((f'OUT({andar})', (andar, tuple(novo_dentro), esperando)))
    if len(dentro) < capacidade:
        destinos_ja_gerados = set()
        for indice, (origem, destino) in enumerate(esperando):
            if origem == andar and destino not in destinos_ja_gerados:
                destinos_ja_gerados.add(destino)
                novo_esperando = list(esperando)
                novo_esperando.pop(indice)
                novo_dentro = list(dentro)
                novo_dentro.append(destino)
                novo_dentro.sort()
                resposta.append((f'IN({origem}->{destino})', (andar, tuple(novo_dentro), tuple(novo_esperando))))
    return resposta


def posicoes_relevantes(s):
    _, dentro, esperando = s
    p = list(dentro)
    for origem, destino in esperando:
        p.extend([origem, destino])
    return p


def h0(s):
    return 0


def h1(s):
    andar, _, _ = s
    return max((abs(andar - x) for x in posicoes_relevantes(s)), default=0)


def h2(s):
    _, dentro, esperando = s
    p = posicoes_relevantes(s)
    deslocamento = (max(p) - min(p)) if p else 0
    return deslocamento + len(dentro) + len(esperando)


def h3(s):
    andar, dentro, esperando = s
    p = posicoes_relevantes(s)
    if p:
        menor, maior = min(p), max(p)
        deslocamento = maior - menor + min(abs(andar - menor), abs(andar - maior))
    else:
        deslocamento = 0
    return deslocamento + len(dentro) + 2 * len(esperando)


def prioridade_atendimento(s, capacidade):
    andar, dentro, esperando = s
    pode_sair = andar in dentro
    pode_entrar = len(dentro) < capacidade and any(origem == andar for origem, _ in esperando)
    return 0 if (pode_sair or pode_entrar) else 1


def distancia_relevante_mais_proxima(s):
    andar, _, _ = s
    return min((abs(andar - x) for x in posicoes_relevantes(s)), default=0)


def reconstruir(parent, objetivo):
    caminho, atual = [], objetivo
    while parent[atual][0] is not None:
        anterior, acao = parent[atual]
        caminho.append(acao)
        atual = anterior
    caminho.reverse()
    return caminho


def bfs(andar_inicial, capacidade, demandas):
    inicial = estado(andar_inicial, (), demandas)
    fila = deque([inicial])
    parent = {inicial: (None, None)}
    expandidos, inicio = 0, perf_counter()
    while fila:
        atual = fila.popleft()
        if meta(atual):
            caminho = reconstruir(parent, atual)
            return dict(custo=len(caminho), nos=expandidos, tempo_ms=(perf_counter()-inicio)*1000, caminho=caminho)
        expandidos += 1
        for acao, prox in sucessores(atual, capacidade):
            if prox not in parent:
                parent[prox] = (atual, acao)
                fila.append(prox)
    return None


def busca_prioridade(andar_inicial, capacidade, demandas, heuristica, gulosa=False, direcional=False):
    inicial = estado(andar_inicial, (), demandas)
    g, parent, fechados = {inicial: 0}, {inicial: (None, None)}, {}
    contador, heap = itertools.count(), []

    def prioridade(s, gs):
        hs = heuristica(s)
        if gulosa:
            return (hs, gs, next(contador))
        f = gs + hs
        if direcional:
            return (f, prioridade_atendimento(s, capacidade), distancia_relevante_mais_proxima(s), gs, next(contador))
        return (f, gs, next(contador))

    heappush(heap, (prioridade(inicial, 0), 0, inicial))
    expandidos, inicio = 0, perf_counter()
    while heap:
        _, g_da_entrada, atual = heappop(heap)
        if g_da_entrada != g.get(atual):
            continue
        if atual in fechados and fechados[atual] <= g_da_entrada:
            continue
        fechados[atual] = g_da_entrada
        if meta(atual):
            caminho = reconstruir(parent, atual)
            return dict(custo=len(caminho), nos=expandidos, tempo_ms=(perf_counter()-inicio)*1000, caminho=caminho)
        expandidos += 1
        for acao, prox in sucessores(atual, capacidade):
            novo_g = g_da_entrada + 1
            if novo_g < g.get(prox, math.inf):
                g[prox] = novo_g
                parent[prox] = (atual, acao)
                heappush(heap, (prioridade(prox, novo_g), novo_g, prox))
    return None


INSTANCIAS = {
    'Facil': dict(andar=1, capacidade=2, demandas=[(2,5),(4,1)]),
    'Media': dict(andar=6, capacidade=3, demandas=[(25,8),(6,14),(16,7),(13,2)]),
    'Dificil': dict(andar=6, capacidade=3, demandas=[(25,8),(6,14),(16,7),(13,2),(30,45)]),
}
ALGORITMOS = {
    'BFS': lambda i: bfs(i['andar'],i['capacidade'],i['demandas']),
    'A* h0': lambda i: busca_prioridade(i['andar'],i['capacidade'],i['demandas'],h0),
    'A* h1': lambda i: busca_prioridade(i['andar'],i['capacidade'],i['demandas'],h1),
    'A* h2': lambda i: busca_prioridade(i['andar'],i['capacidade'],i['demandas'],h2),
    'A* h3': lambda i: busca_prioridade(i['andar'],i['capacidade'],i['demandas'],h3),
    'Gulosa h3': lambda i: busca_prioridade(i['andar'],i['capacidade'],i['demandas'],h3,gulosa=True),
    'A*D': lambda i: busca_prioridade(i['andar'],i['capacidade'],i['demandas'],h3,direcional=True),
}


def executar(repeticoes=7):
    linhas, caminhos = [], {}
    for nome_instancia, instancia in INSTANCIAS.items():
        print(f'\n=== Instancia {nome_instancia} ===')
        for nome_algoritmo, funcao in ALGORITMOS.items():
            execucoes = [funcao(instancia) for _ in range(repeticoes)]
            base = execucoes[0]
            tempo_mediano = statistics.median(x['tempo_ms'] for x in execucoes)
            linhas.append(dict(instancia=nome_instancia, algoritmo=nome_algoritmo, custo=base['custo'], nos_expandidos=base['nos'], tempo_mediano_ms=round(tempo_mediano,4)))
            caminhos[(nome_instancia,nome_algoritmo)] = base['caminho']
            print(f"{nome_algoritmo:10s} | custo={base['custo']:3d} | nos={base['nos']:6d} | tempo mediano={tempo_mediano:8.4f} ms")
    return linhas, caminhos


def salvar_csv(linhas, arquivo):
    with open(arquivo,'w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['instancia','algoritmo','custo','nos_expandidos','tempo_mediano_ms'])
        writer.writeheader()
        writer.writerows(linhas)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--repeticoes',type=int,default=7)
    parser.add_argument('--csv',default='resultados_elevadores.csv')
    args=parser.parse_args()
    linhas,caminhos=executar(max(1,args.repeticoes))
    salvar_csv(linhas,args.csv)
    print(' -> '.join(caminhos[('Facil','A* h3')]))


if __name__=='__main__':
    main()
