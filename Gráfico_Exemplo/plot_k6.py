"""
Script para analisar CSV gerado pelo k6:
- Mostra no terminal resumo estatístico de algumas métricas, incluindo número médio de requisições (sem gráfico)
- Gera gráficos da duração e tempo bloqueado das requisições ao longo do tempo, com estilo clean e legenda
- Tempo é mostrado em segundos desde o início do teste para facilitar análise

Para usar, rode o script na pasta com resultado.csv.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def print_resumo_metric(df, metric_name):
    df_metric = df[df['metric_name'] == metric_name]
    if df_metric.empty:
        print(f"\nMétrica '{metric_name}' não encontrada no dataset.")
        return None
    
    durations = df_metric['metric_value']
    
    # definir unidade conforme métrica
    if metric_name == 'http_reqs':
        unidade = "reqs (contagem)"
    else:
        unidade = "ms"
        
    resumo = {
        'Média': durations.mean(),
        'Mediana': durations.median(),
        'Min': durations.min(),
        'Máx': durations.max(),
        'P95': np.percentile(durations, 95),
        'P99': np.percentile(durations, 99)
    }
    print(f"\nResumo da métrica '{metric_name}':")
    for k, v in resumo.items():
        print(f"  {k}: {v:.2f} {unidade}")
    return resumo

def plot_metric_over_time(df, metric_name, ylabel, color='#1f77b4'):
    df_metric = df[df['metric_name'] == metric_name].copy()
    if df_metric.empty:
        print(f"\nMétrica '{metric_name}' não encontrada no dataset. Não será gerado gráfico.")
        return
    
    df_metric['relative_time'] = df_metric['timestamp'] - df_metric['timestamp'].min()
    df_grouped = df_metric.groupby(df_metric['relative_time'].astype(int)).metric_value.mean().reset_index()

    plt.figure(figsize=(14,7))
    plt.plot(df_grouped['relative_time'], df_grouped['metric_value'],
             marker='o', linestyle='-', color=color, linewidth=2, label=f'{metric_name} médio')
    plt.title(f"{ylabel} ao longo do tempo", fontsize=16, fontweight='bold')
    plt.xlabel("Tempo desde o início do teste (segundos)", fontsize=14)
    plt.ylabel(ylabel, fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{metric_name}.png")
    plt.show()

def main():
    df = pd.read_csv("resultado.csv")

    print_resumo_metric(df, 'http_req_duration')
    plot_metric_over_time(df, 'http_req_duration', 'Duração média das requisições (ms)', '#1f77b4')

    print_resumo_metric(df, 'http_req_blocked')
    plot_metric_over_time(df, 'http_req_blocked', 'Tempo médio bloqueado das requisições (ms)', '#ff7f0e')

if __name__ == "__main__":
    main()
