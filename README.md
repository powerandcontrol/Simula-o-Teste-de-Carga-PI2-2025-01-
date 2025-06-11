# 📬 Consulta de CEP com Flask + Teste de Carga com k6

Este projeto consiste em uma **API Flask** para consulta de dados de CEPs armazenados em um banco SQLite, com **testes de carga utilizando [k6](https://k6.io/)** e **análise estatística dos resultados via Python**.

---

## 📦 Estrutura do Projeto

```plaintext
.
├── app.py                     # API Flask que expõe o endpoint /cep/<cep>
├── bd.py                      # Script para popular o banco SQLite (ceps.db)
├── ceps.db                    # Banco SQLite com dados de exemplo
├── script.js                  # Script de teste de carga com k6
├── plot_k6.py                 # Script para análise dos resultados (CSV)
├── package.json               # Script para executar o teste com k6
├── docs/
│   ├── plot.html              # Relatório HTML com links para resultados
│   ├── resultado.csv          # CSV com os dados de execução
│   ├── http_req_duration.png # Gráfico de duração das requisições
│   ├── http_req_blocked.png  # Gráfico de tempo bloqueado
│   └── http_reqs.png         # Gráfico de vazão
```

---

## 🚀 Como rodar a aplicação

1. **Instale os requisitos do backend:**

   ```bash
   pip install flask
   ```

2. **Crie o banco de dados (se necessário):**

   ```bash
   python bd.py
   ```

3. **Inicie o servidor Flask:**

   ```bash
   python app.py
   ```

> O servidor estará disponível em:  
> 🔗 **http://localhost:8000**

---

## 🔍 Exemplo de uso da API

**Consulta de um CEP:**

```
GET http://localhost:8000/cep/01001000
```

**Resposta esperada (exemplo):**

```json
{
  "cep": "01001000",
  "logradouro": "Praça da Sé",
  "complemento": "lado ímpar",
  "bairro": "Sé",
  "cidade": "São Paulo",
  "uf": "SP",
  "ibge": "3550308",
  "ddd": "11",
  "timestamp_consulta": "2025-06-08T14:32:17.123456"
}
```

---

## 📊 Teste de carga com k6

### 🔧 Pré-requisitos:

- Ter o [k6](https://k6.io/docs/getting-started/installation/) instalado

### ▶️ Execução:

```bash
npm run relatorio
```

Isso executará o `script.js`, testando o endpoint `/cep/<cep>` e gerando o arquivo `docs/resultado.csv`.

---

## 📈 Análise dos Resultados

1. **Instale as dependências Python:**

   ```bash
   pip install pandas matplotlib
   ```

2. **Execute o script de análise:**

   ```bash
   python plot_k6.py
   ```

Serão gerados:

- Estatísticas no terminal (média, mediana, P95, etc.)
- Imagens:
  - `docs/http_req_duration.png`
  - `docs/http_req_blocked.png`
  - `docs/http_reqs.png`

---

## 📄 Relatório Online

Acesse o relatório interativo em HTML para visualizar os resultados dos testes de carga, incluindo links para os gráficos gerados e o arquivo CSV:

🔗 **[Relatório de Resultados](https://powerandcontrol.github.io/Simula-o-Teste-de-Carga-PI2-2025-01-/plot.html)**

**Descrição:**  
Clique no link acima para ver o relatório diretamente no navegador. A página inclui:

- Links para os gráficos de duração, tempo bloqueado e vazão.
- Link para baixar o `resultado.csv`.
- Exemplo de estatísticas exibidas no terminal.

---

## ✅ Validações realizadas no teste (k6)

O script `script.js` testa:

- Status HTTP 200
- Existência do campo `logradouro`
- Tipo da `cidade` como string
- Validação da sigla `UF` dentro da lista esperada
- Presença do `timestamp`

---

## 🛠️ Tecnologias Utilizadas

- Python 3
- Flask
- SQLite
- JavaScript com k6
- Pandas e Matplotlib para análise
- HTML para relatório

---

## 📄 Licença

UNIRIO, CCET - Centro de Ciências Exatas e Tecnologia
