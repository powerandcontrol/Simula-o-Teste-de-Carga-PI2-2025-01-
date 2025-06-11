"""
Script para analisar CSV gerado pelo k6:
- Mostra no terminal resumo estatístico de algumas métricas, incluindo número médio de requisições (sem gráfico)
- Gera gráficos da duração, tempo bloqueado e vazão das requisições ao longo do tempo, com estilo clean e legenda
- Inclui concorrência (VUs) como área sombreada com escala no eixo direito
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
    
    values = df_metric['metric_value']
    
    # Definir unidade conforme métrica
    if metric_name == 'http_reqs':
        unidade = "reqs (contagem)"
    else:
        unidade = "ms"
        
    resumo = {
        'Média': values.mean(),
        'Mediana': values.median(),
        'Min': values.min(),
        'Máx': values.max(),
        'P95': np.percentile(values, 95),
        'P99': np.percentile(values, 99)
    }
    print(f"\nResumo da métrica '{metric_name}':")
    for k, v in resumo.items():
        print(f"  {k}: {v:.2f} {unidade}")
    return resumo

def plot_metric_over_time(df, metric_name, ylabel, color='#1f77b4', throughput=False):
    df_metric = df[df['metric_name'] == metric_name].copy()
    if df_metric.empty:
        print(f"\nMétrica '{metric_name}' não encontrada no dataset. Não será gerado gráfico.")
        return
    
    df_metric['relative_time'] = df_metric['timestamp'] - df_metric['timestamp'].min()
    
    if throughput:
        # Calcular vazão (requisições por segundo)
        df_metric['time_bin'] = df_metric['relative_time'].astype(int)
        df_grouped = df_metric.groupby('time_bin')['metric_value'].sum().reset_index()
        df_grouped = df_grouped.rename(columns={'time_bin': 'relative_time'})  # Renomear para consistência
    else:
        df_grouped = df_metric.groupby(df_metric['relative_time'].astype(int))['metric_value'].mean().reset_index()

    # Preparar dados de concorrência (vus)
    df_vus = df[df['metric_name'] == 'vus'].copy()
    if df_vus.empty:
        print("Métrica 'vus' não encontrada. Concorrência não será plotada.")
        vus_available = False
    else:
        df_vus['relative_time'] = df_vus['timestamp'] - df_vus['timestamp'].min()
        df_vus_grouped = df_vus.groupby(df_vus['relative_time'].astype(int))['metric_value'].mean().reset_index()
        vus_available = True

    # Criar gráfico
    fig, ax1 = plt.subplots(figsize=(14,7))
    
    # Plotar métrica principal
    ax1.plot(df_grouped['relative_time'], df_grouped['metric_value'],
             marker='o', linestyle='-', color=color, linewidth=2, label=f'{metric_name} {"médio" if not throughput else "total"}')
    ax1.set_xlabel("Tempo desde o início do teste (segundos)", fontsize=14)
    ax1.set_ylabel(ylabel, fontsize=14, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Plotar concorrência (VUs) no eixo direito, se disponível
    if vus_available:
        ax2 = ax1.twinx()
        ax2.fill_between(df_vus_grouped['relative_time'], df_vus_grouped['metric_value'],
                         color='gray', alpha=0.2, label='Concorrência (VUs)')
        ax2.set_ylabel('Concorrência (VUs)', fontsize=14, color='gray')
        ax2.tick_params(axis='y', labelcolor='gray')

        # Combinar legendas
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=12)
    else:
        ax1.legend(fontsize=12)

    plt.title(f"{ylabel} ao longo do tempo", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{metric_name}.png")
    plt.show()

def main():
    df = pd.read_csv("resultado.csv")

    print_resumo_metric(df, 'http_req_duration')
    plot_metric_over_time(df, 'http_req_duration', 'Duração média das requisições (ms)', '#1f77b4')

    print_resumo_metric(df, 'http_req_blocked')
    plot_metric_over_time(df, 'http_req_blocked', 'Tempo médio bloqueado das requisições (ms)', '#ff7f0e')

    print_resumo_metric(df, 'http_reqs')
    plot_metric_over_time(df, 'http_reqs', 'Vazão (requisições por segundo)', '#2ca02c', throughput=True)

if __name__ == "__main__":
    main()