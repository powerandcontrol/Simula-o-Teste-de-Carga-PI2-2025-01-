import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Mapeamento de nomes legíveis para exibição
NOMES_LEGAIS = {
    'http_req_duration': 'Duração média das requisições (ms)',
    'http_req_blocked': 'Tempo médio bloqueado das requisições (ms)',
    'http_reqs': 'Vazão de requisições (reqs por segundo)'
}

def print_resumo_metric(df, metric_name):
    df_metric = df[df['metric_name'] == metric_name]
    if df_metric.empty:
        print(f"\nMétrica '{metric_name}' não encontrada.")
        return None

    values = df_metric['metric_value']
    unidade = "reqs" if metric_name == 'http_reqs' else "ms"

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

def analisar_impacto_bloqueio(df):
    df_blocked = df[df['metric_name'] == 'http_req_blocked'].copy()
    if df_blocked.empty:
        print("Métrica 'http_req_blocked' não encontrada para análise.")
        return

    df_blocked['relative_time'] = df_blocked['timestamp'] - df_blocked['timestamp'].min()
    df_blocked['time_bin'] = (df_blocked['relative_time'] // 30) * 30

    resumo = df_blocked.groupby('time_bin')['metric_value'].mean().reset_index()

    print("\nTempo médio bloqueado por intervalo de 30s:")
    for _, row in resumo.iterrows():
        print(f"  {int(row['time_bin'])}s - {int(row['time_bin']+30)}s: {row['metric_value']:.2f} ms")

    maior = resumo.loc[resumo['metric_value'].idxmax()]
    t_ini, t_fim = int(maior['time_bin']), int(maior['time_bin']+30)
    print(f"\n➡️ Maior bloqueio: {t_ini}s - {t_fim}s com {maior['metric_value']:.2f} ms")

    df_reqs = df[df['metric_name'] == 'http_reqs'].copy()
    df_reqs['relative_time'] = df_reqs['timestamp'] - df_reqs['timestamp'].min()
    reqs_maior_bloqueio = df_reqs[
        (df_reqs['relative_time'] >= t_ini) & (df_reqs['relative_time'] < t_fim)
    ]['metric_value'].sum()
    print(f"➡️ Requisições nesse intervalo: {int(reqs_maior_bloqueio)} reqs")

    reqs_por_fase = df_reqs.groupby((df_reqs['relative_time'] // 30) * 30)['metric_value'].sum().reset_index()
    pico_reqs = reqs_por_fase.loc[reqs_por_fase['metric_value'].idxmax()]
    if int(pico_reqs['relative_time']) != t_ini:
        print(f"⚠️ Maior carga de requisições: {int(pico_reqs['relative_time'])}s - {int(pico_reqs['relative_time']+30)}s "
              f"com {int(pico_reqs['metric_value'])} reqs")

def plot_metric_over_time(df, metric_name, ylabel, color='#1f77b4', throughput=False):
    df_metric = df[df['metric_name'] == metric_name].copy()
    if df_metric.empty:
        print(f"\nMétrica '{metric_name}' ausente. Gráfico não gerado.")
        return

    df_metric['relative_time'] = df_metric['timestamp'] - df_metric['timestamp'].min()

    if throughput:
        df_metric['time_bin'] = df_metric['relative_time'].astype(int)
        df_grouped = df_metric.groupby('time_bin')['metric_value'].sum().reset_index()
        df_grouped = df_grouped.rename(columns={'time_bin': 'relative_time'})
    else:
        df_grouped = df_metric.groupby(df_metric['relative_time'].astype(int))['metric_value'].mean().reset_index()

    # Calcular P95 e P99 somente para métricas de latência/bloqueio
    show_percentiles = metric_name in ['http_req_duration', 'http_req_blocked']
    if show_percentiles:
        p95 = np.percentile(df_metric['metric_value'], 95)
        p99 = np.percentile(df_metric['metric_value'], 99)

    # Concorrência
    df_vus = df[df['metric_name'] == 'vus'].copy()
    vus_available = not df_vus.empty
    if vus_available:
        df_vus['relative_time'] = df_vus['timestamp'] - df_vus['timestamp'].min()
        df_vus_grouped = df_vus.groupby(df_vus['relative_time'].astype(int))['metric_value'].mean().reset_index()

    fig, ax1 = plt.subplots(figsize=(14, 7))
    ax1.plot(df_grouped['relative_time'], df_grouped['metric_value'], linestyle='-', color=color, linewidth=2,
             label=NOMES_LEGAIS.get(metric_name, metric_name))

    # Plotar linhas P95 e P99 só se for latência ou bloqueio
    if show_percentiles:
        ax1.axhline(p95, color='yellow', linestyle='--', linewidth=1.5, label='P95')
        ax1.axhline(p99, color='red', linestyle=':', linewidth=1.5, label='P99')

    ax1.set_xlabel("Tempo (s)", fontsize=14)
    ax1.set_ylabel(ylabel, fontsize=14, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.6)

    # Eixo X padronizado
    max_time = max(df_grouped['relative_time'].max(), 
                   df_vus_grouped['relative_time'].max() if vus_available else 0)
    x_max = (int(max_time / 10) + 1) * 10
    x_ticks = np.arange(0, x_max + 1, 10)
    ax1.set_xlim(0, x_max)
    ax1.set_xticks(x_ticks)
    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')

    # Concorrência VUs
    if vus_available:
        ax2 = ax1.twinx()
        ax2.fill_between(df_vus_grouped['relative_time'], df_vus_grouped['metric_value'],
                         color='gray', alpha=0.2, label='Concorrência (VUs)')
        ax2.set_ylabel('Concorrência (VUs)', fontsize=14, color='gray')
        ax2.tick_params(axis='y', labelcolor='gray')
        ax2.set_xlim(0, x_max)
        ax2.set_xticks(x_ticks)

        # Escalas iguais só para gráfico de vazão
        if throughput:
            y_min = min(df_grouped['metric_value'].min(), df_vus_grouped['metric_value'].min())
            y_max = max(df_grouped['metric_value'].max(), df_vus_grouped['metric_value'].max())
            ax1.set_ylim(y_min, y_max)
            ax2.set_ylim(y_min, y_max)

        # Legenda combinada
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=12)
    else:
        ax1.legend(fontsize=12)

    plt.title(f"{NOMES_LEGAIS.get(metric_name, metric_name)} ao longo do tempo", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f"{metric_name}.png")
    plt.show()

def main():
    df = pd.read_csv("resultado.csv")

    print_resumo_metric(df, 'http_req_duration')
    plot_metric_over_time(df, 'http_req_duration', NOMES_LEGAIS['http_req_duration'], '#1f77b4')

    print_resumo_metric(df, 'http_req_blocked')
    analisar_impacto_bloqueio(df)
    plot_metric_over_time(df, 'http_req_blocked', NOMES_LEGAIS['http_req_blocked'], '#ff7f0e')

    plot_metric_over_time(df, 'http_reqs', NOMES_LEGAIS['http_reqs'], '#2ca02c', throughput=True)

if __name__ == "__main__":
    main()
