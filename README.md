# Backend de autenticação SERPRO

Projeto FastAPI simples para expor um endpoint HTTP que executa a chamada `curl` de autenticação do SERPRO com certificado digital P12 baixado dinamicamente.

## Estrutura do projeto
- `app/main.py`: código-fonte do FastAPI e endpoint `/authenticate`.
- `requirements.txt`: dependências Python.
- `Dockerfile`: imagem pronta para EasyPanel ou outros orquestradores.

## Uso do endpoint
O endpoint POST `/authenticate` baixa o certificado P12 a partir de um link público e executa a mesma chamada `curl` fornecida, retornando a saída completa (headers + body) como texto simples.

### Parâmetros
Envie um JSON como o exemplo abaixo. Se variáveis de ambiente `CERT_URL` e `CERT_PASSWORD` forem definidas, os campos podem ser omitidos.

```json
{
  "cert_url": "https://seu-link-publico-no-supabase/arquivo_certificado.p12",
  "cert_password": "senha_certificado"
}
```

## Execução local
1. Crie e ative um ambiente virtual (opcional) e instale as dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Exporte as variáveis de ambiente para evitar enviar dados sensíveis em cada requisição:
   ```bash
   export CERT_URL="https://seu-link-publico-no-supabase/arquivo_certificado.p12"
   export CERT_PASSWORD="senha_certificado"
   ```
3. Inicie o servidor:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
4. Faça a chamada:
   ```bash
   curl -X POST http://localhost:8000/authenticate \
     -H "Content-Type: application/json" \
     -d '{"cert_url": "'$CERT_URL'", "cert_password": "'$CERT_PASSWORD'"}'
   ```

## Deploy no EasyPanel
1. Crie um novo serviço Docker apontando para este repositório.
2. Defina as variáveis de ambiente `CERT_URL` e `CERT_PASSWORD` no EasyPanel.
3. O Dockerfile já expõe a porta 8000 e inicia o servidor com Uvicorn; não são necessárias configurações adicionais.

## Observações
- O endpoint replica a chamada `curl` original, incluindo os headers e o `grant_type=client_credentials`.
- O certificado é baixado em um diretório temporário a cada requisição e não é persistido.
