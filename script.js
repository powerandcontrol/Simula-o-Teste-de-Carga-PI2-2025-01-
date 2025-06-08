import http from 'k6/http';
import { check, sleep } from 'k6';

const ceps = [
  "01001000",
  "20040002",
  "30140071",
  "70040900",
  "88010001"
];

export let options = {
  stages: [
    { duration: '10s', target: 10 },
    { duration: '20s', target: 50 },
    { duration: '10s', target: 0 },
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
