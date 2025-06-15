/**
 * Teste de carga escalonado com 3 fases:
 *
 * Fase 1 (Leve): até 50 VUs → ver estabilidade inicial
 * Fase 2 (Média): até 200 VUs → simular uso real
 * Fase 3 (Alta): até 600 VUs → testar resistência da API/localhost
 *
 * 💻 Configuração da máquina:
 * - Intel Core i5-1035G1 (4 núcleos / 8 threads)
 * - 11.8 GB RAM (c/ ~2.6 GB livre no momento)
 * - SSD, virtualização habilitada
 * - Objetivo: não travar, mas medir capacidade real
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

const ceps = [
  "01001000", // SP
  "20040002", // RJ
  "30140071", // MG
  "70040900", // DF
  "88010001"  // SC
];

export let options = {
  stages: [
    // Fase 1 - Leve (aquecimento)
    { duration: '30s', target: 20 },
    { duration: '30s', target: 50 },

    // Fase 2 - Média (uso realista)
    { duration: '30s', target: 100 },
    { duration: '45s', target: 200 },

    // Fase 3 - Alta (teste de estresse)
    { duration: '1m', target: 400 },
    { duration: '1m', target: 600 },

    // Fase final - redução progressiva
    { duration: '45s', target: 200 },
    { duration: '30s', target: 50 },
    { duration: '30s', target: 0 }
  ]
};

export default function () {
  let cep = ceps[Math.floor(Math.random() * ceps.length)];
  let res = http.get(`http://localhost:8000/cep/${cep}`);
  let body = JSON.parse(res.body);
  
  check(res, {
    'status é 200': (r) => r.status === 200,
    'logradouro existe': () => !!body.logradouro,
    'cidade é string': () => typeof body.cidade === 'string',
    'UF válida': () => ['SP', 'RJ', 'MG', 'DF', 'SC'].includes(body.uf),
    'timestamp presente': () => body.timestamp_consulta !== undefined
  });

  sleep(1);
}
