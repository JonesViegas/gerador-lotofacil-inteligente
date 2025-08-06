import flask
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import random
from collections import Counter
import io
import base64
import os
import json

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

# --- CONFIGURAÇÕES E CONSTANTES ---
BOLAS = [f'Bola{i}' for i in range(1, 16)]
NUMEROS_DISPONIVEIS = list(range(1, 26))
MOLDURA = [1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25]
MIOLO = [7, 8, 9, 12, 13, 14, 17, 18, 19]
ANALISE_TECNICAS = {
    'frequencia': {'nome': 'Frequência Histórica'}, 'atraso': {'nome': 'Números Atrasados'},
    'par_impar': {'nome': 'Filtro Par/Ímpar (7-9 de cada)'}, 'soma_dezenas': {'nome': 'Filtro Soma (185-205)'},
    'moldura_miolo': {'nome': 'Filtro Moldura/Miolo (8-11 na moldura)'}
}
CAMINHO_CONTADOR = 'contador.txt'
CAMINHO_STATS_GERADOR = 'gerador_stats.json'

# --- CACHE GLOBAL PARA PERFORMANCE ---
DF_GLOBAL, STATS_GLOBAL = None, {}
PLOT_URL_GLOBAL, STATS_PLOT_URL_GLOBAL = None, None
HISTORICAL_SETS = []

def load_data():
    try:
        caminho = os.path.join(os.path.dirname(__file__), 'Lotofácil.xlsx')
        df = pd.read_excel(caminho, sheet_name='LOTOFÁCIL')
        return df[['Concurso', 'Data Sorteio'] + BOLAS]
    except Exception as e:
        print(f"ERRO CRÍTICO: Não foi possível carregar 'Lotofácil.xlsx'. Detalhes: {e}")
        return None

def atualizar_e_obter_visitas():
    total_visitas = 0
    try:
        if not os.path.exists(CAMINHO_CONTADOR):
            with open(CAMINHO_CONTADOR, 'w') as f: f.write('0')
        with open(CAMINHO_CONTADOR, 'r') as f:
            total_visitas = int(f.read().strip() or 0)
    except (IOError, ValueError) as e:
        print(f"Alerta: Não foi possível ler o contador ({e}). Reiniciando para 0.")
        total_visitas = 0
    total_visitas += 1
    with open(CAMINHO_CONTADOR, 'w') as f: f.write(str(total_visitas))
    return total_visitas

def ler_estatisticas_gerador():
    default_stats = {"total_gerados": 0, "total_exitosos": 0}
    if not os.path.exists(CAMINHO_STATS_GERADOR): return default_stats
    try:
        with open(CAMINHO_STATS_GERADOR, 'r') as f: return json.load(f)
    except (IOError, json.JSONDecodeError): return default_stats

def salvar_estatisticas_gerador(stats_data):
    try:
        with open(CAMINHO_STATS_GERADOR, 'w') as f: json.dump(stats_data, f, indent=4)
    except IOError as e: print(f"ERRO CRÍTICO: Não foi possível salvar estatísticas: {e}")

def analisar_estatisticas_adicionais(df):
    if df is None: return {}
    stats = {'par_impar': [], 'soma': [], 'moldura_miolo': []}
    for _, row in df.iterrows():
        jogo = row[BOLAS].values
        impares = sum(1 for n in jogo if n % 2 != 0)
        stats['par_impar'].append(f"{impares}Í / {15-impares}P")
        stats['soma'].append(sum(jogo))
        moldura_count = sum(1 for n in jogo if n in MOLDURA)
        stats['moldura_miolo'].append(f"{moldura_count}M / {15-moldura_count}m")
    return {'par_impar': Counter(stats['par_impar']).most_common(5), 'soma_dist': stats['soma'], 'moldura_miolo': Counter(stats['moldura_miolo']).most_common(5)}

def generate_charts(df, stats):
    plot_url, stats_plot_url = None, None
    if df is None: return None, None
    try:
        plt.figure(figsize=(12, 6)); sns.countplot(data=df[BOLAS].stack().reset_index(name='numero'), x='numero', order=NUMEROS_DISPONIVEIS, palette='viridis', hue='numero', legend=False)
        plt.title('Frequência Histórica dos Números Sorteados', fontsize=16); plt.xlabel('Número', fontsize=12); plt.ylabel('Quantidade de Vezes Sorteado', fontsize=12); plt.xticks(rotation=45)
        img = io.BytesIO(); plt.savefig(img, format='png', bbox_inches='tight'); img.seek(0); plot_url = base64.b64encode(img.getvalue()).decode('utf-8'); plt.close()
        plt.figure(figsize=(12, 6)); sns.histplot(data=stats.get('soma_dist', []), kde=True, bins=30)
        plt.axvline(185, color='red', linestyle='--', label='Filtro Mín. (185)'); plt.axvline(205, color='red', linestyle='--', label='Filtro Máx. (205)')
        plt.title('Distribuição da Soma dos 15 Números Sorteados', fontsize=16); plt.xlabel('Soma', fontsize=12); plt.ylabel('Frequência', fontsize=12); plt.legend()
        img = io.BytesIO(); plt.savefig(img, format='png', bbox_inches='tight'); img.seek(0); stats_plot_url = base64.b64encode(img.getvalue()).decode('utf-8'); plt.close()
    except Exception as e: print(f"Erro ao gerar gráficos: {e}")
    return plot_url, stats_plot_url

DF_GLOBAL = load_data()
if DF_GLOBAL is not None:
    print("Arquivo 'Lotofácil.xlsx' carregado com sucesso.")
    STATS_GLOBAL = analisar_estatisticas_adicionais(DF_GLOBAL)
    PLOT_URL_GLOBAL, STATS_PLOT_URL_GLOBAL = generate_charts(DF_GLOBAL, STATS_GLOBAL)
    HISTORICAL_SETS = [set(row) for row in DF_GLOBAL[BOLAS].values.tolist()]
    print(f"Análise de acertos pré-processada com {len(HISTORICAL_SETS)} sorteios.")

def analisar_frequencias(df): return df[BOLAS].stack().value_counts().to_dict() if df is not None else {}
def calcular_atrasos(df):
    if df is None or df.empty: return {}
    atrasos, ultimo_concurso_num = {}, df['Concurso'].max()
    for num in NUMEROS_DISPONIVEIS:
        ultimo_sorteio_com_num = df[df[BOLAS].isin([num]).any(axis=1)]['Concurso'].max()
        atrasos[num] = ultimo_concurso_num - (ultimo_sorteio_com_num if pd.notna(ultimo_sorteio_com_num) else 0)
    return atrasos

# --- ATUALIZADO: Lógica de geração de jogos completamente refeita ---
def gerar_jogos(pesos_base, qtd_jogos, filtros, game_size, include_nums, exclude_nums):
    jogos_filtrados = []
    
    # Validação inicial
    if len(include_nums) > game_size:
        return [] # Não é possível gerar um jogo se os números incluídos já excedem o tamanho

    # Prepara o conjunto de números disponíveis para a geração aleatória
    pool_numeros = list(set(pesos_base.keys()) - set(exclude_nums) - set(include_nums))
    
    # Filtra os pesos para corresponderem apenas aos números do pool
    pool_pesos = [pesos_base.get(num, 0) for num in pool_numeros]
    if sum(pool_pesos) == 0:
        # Fallback se todos os números com peso foram excluídos
        pool_pesos = np.ones(len(pool_numeros))
    
    pesos_normalizados = np.array(pool_pesos) / sum(pool_pesos)
    
    qtd_a_escolher = game_size - len(include_nums)
    if qtd_a_escolher > len(pool_numeros):
        return [] # Não há números suficientes no pool para completar o jogo

    jogos_gerados = set()
    for _ in range(qtd_jogos * 50): # Gera um pool para ter de onde filtrar
        if len(jogos_filtrados) >= qtd_jogos: break

        numeros_aleatorios = np.random.choice(pool_numeros, size=qtd_a_escolher, replace=False, p=pesos_normalizados)
        jogo_final = tuple(sorted(include_nums + list(numeros_aleatorios)))
        
        if jogo_final in jogos_gerados: continue
        jogos_gerados.add(jogo_final)

        # Aplica filtros apenas se o jogo for de 15 dezenas
        if game_size == 15:
            impares = sum(1 for n in jogo_final if n % 2 != 0)
            if 'par_impar' in filtros and not (7 <= impares <= 9): continue
            if 'soma_dezenas' in filtros and not (185 <= sum(jogo_final) <= 205): continue
            moldura_count = sum(1 for n in jogo_final if n in MOLDURA)
            if 'moldura_miolo' in filtros and not (8 <= moldura_count <= 11): continue
        
        jogos_filtrados.append(list(jogo_final))
            
    return jogos_filtrados

def analisar_acertos_historicos(jogos):
    resultados = []
    for jogo in jogos:
        jogo_set = set(jogo)
        acertos = {'11': 0, '12': 0, '13': 0, '14': 0, '15': 0}
        for historico_set in HISTORICAL_SETS:
            hits = len(jogo_set.intersection(historico_set))
            if hits >= 11: acertos[str(hits)] += 1
        resultados.append({'numeros': jogo, 'acertos': acertos})
    return resultados

def parse_numeros_input(input_str):
    """Converte uma string '1, 2, 3' em uma lista de inteiros [1, 2, 3]"""
    if not input_str: return []
    try:
        # Remove vírgulas e divide por espaços
        numeros = [int(n) for n in input_str.replace(',', ' ').split() if n.isdigit()]
        # Garante que os números são válidos para a Lotofácil
        return sorted(list(set(n for n in numeros if 1 <= n <= 25)))
    except (ValueError, TypeError):
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    jogos, form_data = [], {}
    stats_gerador = ler_estatisticas_gerador()

    if request.method == 'POST':
        if 'limpar' in request.form:
            return redirect(url_for('index'))

        form_data = {
            'qtd_jogos': request.form.get('qtd_jogos', '1'),
            'game_size': request.form.get('game_size', '15'),
            'tecnicas_base': request.form.getlist('tecnicas_base'),
            'filtros': request.form.getlist('filtros'),
            'include_nums_str': request.form.get('include_nums', ''),
            'exclude_nums_str': request.form.get('exclude_nums', '')
        }
        
        # Converte e valida os inputs
        qtd_jogos = int(form_data['qtd_jogos'] or 1)
        game_size = int(form_data['game_size'] or 15)
        include_nums = parse_numeros_input(form_data['include_nums_str'])
        exclude_nums = parse_numeros_input(form_data['exclude_nums_str'])
        
        # Evita conflitos
        exclude_nums = list(set(exclude_nums) - set(include_nums))

        freq = analisar_frequencias(DF_GLOBAL); atrasos = calcular_atrasos(DF_GLOBAL)
        pesos = {num: 0 for num in NUMEROS_DISPONIVEIS}
        if 'frequencia' in form_data['tecnicas_base']:
            max_freq = max(freq.values(), default=1)
            for num in NUMEROS_DISPONIVEIS: pesos[num] += freq.get(num, 0) / max_freq
        if 'atraso' in form_data['tecnicas_base']:
            max_atraso = max(atrasos.values(), default=1)
            for num in NUMEROS_DISPONIVEIS: pesos[num] += atrasos.get(num, 0) / max_atraso
        if not form_data['tecnicas_base'] or sum(pesos.values()) == 0:
             pesos = {num: 1 for num in NUMEROS_DISPONIVEIS}

        jogos_gerados = gerar_jogos(pesos, qtd_jogos, form_data['filtros'], game_size, include_nums, exclude_nums)
        jogos = analisar_acertos_historicos(jogos_gerados)

        if jogos:
            jogos_exitosos = sum(1 for jogo_info in jogos if sum(jogo_info['acertos'].values()) > 0)
            stats_gerador['total_gerados'] += len(jogos)
            stats_gerador['total_exitosos'] += jogos_exitosos
            salvar_estatisticas_gerador(stats_gerador)
    else:
        form_data = {
            'qtd_jogos': '', 'game_size': '15', 'tecnicas_base': [], 'filtros': [],
            'include_nums_str': '', 'exclude_nums_str': ''
        }
    
    total_visitas = atualizar_e_obter_visitas()
    
    return render_template(
        'index.html',
        plot_url=PLOT_URL_GLOBAL, stats_plot_url=STATS_PLOT_URL_GLOBAL,
        jogos=jogos, form_data=form_data, tecnicas=ANALISE_TECNICAS,
        estatisticas=STATS_GLOBAL, dados_carregados=(DF_GLOBAL is not None),
        contador_visitas=total_visitas, stats_gerador=stats_gerador
    )

#if __name__ == '__main__':
#  app.run(debug=True)