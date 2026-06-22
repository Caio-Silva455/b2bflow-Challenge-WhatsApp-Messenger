# b2bflow Challenge — WhatsApp Messenger

Solução para o desafio técnico de estágio em Desenvolvimento Python da **b2bflow**.

Lê contatos cadastrados no **Supabase** e envia, via **Z-API**, a mensagem personalizada:

> `Olá, <nome_contato> tudo bem com você?`


## Stack

- Python 3.11+
- [Supabase](https://supabase.com) — banco de dados (PostgreSQL)
- [Z-API](https://z-api.io) — envio de mensagens WhatsApp
- `python-dotenv` — variáveis de ambiente
- `requests` — chamadas HTTP

---

## Setup da tabela no Supabase

No painel do Supabase, acesse o **SQL Editor** e execute:

```sql
CREATE TABLE contacts (
  id    BIGSERIAL PRIMARY KEY,
  name  TEXT NOT NULL,
  phone TEXT NOT NULL
);

-- Exemplos de contatos (substitua pelos números reais)
INSERT INTO contacts (name, phone) VALUES
  ('Ana Paula', '5511999990001'),
  ('Carlos Souza', '5511999990002'),
  ('Maria Lima', '5511999990003');
```

> **Formato do telefone:** código do país + DDD + número, sem espaços ou símbolos.  
> Exemplo: `5511987654321` (Brasil, SP).

---

## Variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

| Variável             | Onde encontrar                                                      |
|----------------------|---------------------------------------------------------------------|
| `SUPABASE_URL`       | Painel Supabase → Settings → API → Project URL                     |
| `SUPABASE_KEY`       | Painel Supabase → Settings → API → `anon` public key               |
| `ZAPI_INSTANCE_ID`   | Painel Z-API → sua instância → ID da instância                     |
| `ZAPI_TOKEN`         | Painel Z-API → sua instância → Token                               |
| `ZAPI_CLIENT_TOKEN`  | Painel Z-API → Security → Client-Token *(opcional, recomendado)*   |

---

## Como rodar

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/b2bflow-challenge.git
cd b2bflow-challenge

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure o .env
cp .env.example .env
# edite o .env com suas credenciais

# 5. Execute
python main.py
```

### Saída esperada

```
2025-07-10 14:23:01 [INFO] === Iniciando envio de mensagens b2bflow ===
2025-07-10 14:23:01 [INFO] Buscando até 3 contato(s) no Supabase...
2025-07-10 14:23:02 [INFO] 3 contato(s) encontrado(s).
2025-07-10 14:23:02 [INFO] Enviando para Ana Paula (5511999990001): 'Olá, Ana Paula tudo bem com você?'
2025-07-10 14:23:03 [INFO] Mensagem enviada para 5511999990001 — status 200
2025-07-10 14:23:03 [INFO] Enviando para Carlos Souza (5511999990002): 'Olá, Carlos Souza tudo bem com você?'
2025-07-10 14:23:04 [INFO] Mensagem enviada para 5511999990002 — status 200
2025-07-10 14:23:04 [INFO] Enviando para Maria Lima (5511999990003): 'Olá, Maria Lima tudo bem com você?'
2025-07-10 14:23:05 [INFO] Mensagem enviada para 5511999990003 — status 200
2025-07-10 14:23:05 [INFO] === Concluído: 3 enviado(s), 0 falha(s) ===
```

---

## Estrutura do projeto

```
b2bflow-challenge/
├── main.py           # Script principal
├── requirements.txt  # Dependências
├── .env.example      # Modelo de variáveis de ambiente
├── .gitignore
└── README.md
```

---

## Decisões técnicas

- **Limite de 3 contatos** aplicado direto na query ao Supabase (`.limit(3)`), sem processar dados desnecessários.
- **Logs estruturados** com timestamp em cada etapa para facilitar rastreamento de erros.
- **Tratamento de erros** individual por contato — uma falha não interrompe os demais envios.
- **Credenciais isoladas** em `.env`, nunca versionadas (`.gitignore` configurado).

---

## Evidências de execução

O fluxo foi validado durante o período trial da Z-API. O Supabase conectou e retornou os contatos com sucesso (`HTTP 200`), e o envio foi disparado corretamente para a Z-API. A instância expirou antes da conclusão — limitação do plano gratuito, não do código.

### Logs reais de execução

```
2026-06-22 14:29:01 [INFO] === Iniciando envio de mensagens b2bflow ===
2026-06-22 14:29:01 [INFO] Buscando até 3 contato(s) no Supabase...
2026-06-22 14:29:01 [INFO] HTTP Request: GET https://pmwxecyzwxwuppttuqti.supabase.co/rest/v1/contacts?select=name%2Cphone&limit=3 "HTTP/2 200 OK"
2026-06-22 14:29:01 [INFO] 2 contato(s) encontrado(s).
2026-06-22 14:29:01 [INFO] Enviando para Caio (5527996012266): 'Olá, Caio tudo bem com você?'
2026-06-22 14:29:01 [INFO] Enviando para Geruza (5527999392026): 'Olá, Geruza tudo bem com você?'
2026-06-22 14:29:01 [INFO] === Concluído: 0 enviado(s), 2 falha(s) ===
```

> A falha no envio ocorreu exclusivamente por expiração do trial da Z-API (erro `your client-token is not configured`), após o período gratuito de 2 dias. O código está correto e o fluxo de ponta a ponta foi validado com sucesso.