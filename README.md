# busca-vagas

Aplicacao para buscar vagas de estagio e trainee aderentes ao perfil do usuario e enviar alertas por email.

## Playwright MCP

Instale e exponha um servidor local do Playwright MCP antes de habilitar fontes dinamicas. A aplicacao usa scraping HTTP por padrao e escala para Playwright MCP quando a pagina exige renderizacao em navegador.

Com Kilo, o MCP ja fica configurado em `kilo.json`. O servidor pode ser iniciado com `npx @playwright/mcp@latest --port 8931 --host 127.0.0.1 --headless`.

## Desenvolvimento local

1. Instale dependencias com `python -m pip install -e .`
2. Execute os testes com `pytest -v`
3. Rode a API com `python -m uvicorn app.main:app --reload`

## Execucao automatica

1. Configure `.env` com SMTP, a fonte HTTP (`COMPANY_PAGE_SOURCE_ENABLED` / `COMPANY_PAGE_SOURCE_URL`) e os limites de matching/alerta.
2. `SEARCH_INTERVAL_MINUTES` funciona como baseline de bootstrap; depois disso a cadencia persistida em `.kilo/ui-settings.json` passa a ser a referencia operacional.
3. Rode a aplicacao; o scheduler registra um ciclo automatico com o intervalo carregado das settings atuais.
4. O estado recuperavel do projeto fica em `.kilo/project-context.md`.
5. As configuracoes operacionais persistidas ficam em `.kilo/ui-settings.json`.

## Deployment

Use um host com runtime Python, banco persistente quando necessario e credenciais SMTP para envio de email.
