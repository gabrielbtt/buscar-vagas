# Project Memory: Busca Vagas (Estágio/Trainee Engenharia Elétrica - BH)

## Contexto Geral
Este projeto é um localizador de vagas de emprego (MVP) que coleta dados de diversas fontes, filtra por pontuação e envia alertas por e-mail.

## Estado Atual (2026-04-11)
- O MVP foi validado e está 100% operacional.
- Configurações de SMTP integradas com `gasbiel04@gmail.com`.
- Suporte a Playwright MCP configurado.
- Estrutura de múltiplos perfis de busca iniciada.

## Metas Principais
1. **Perfis Ativos**: Engenharia Elétrica (Estágio/Trainee, BH e Região, foco em Automação/Projetos).
2. **Fontes Premium**: Integração com Gupy via Playwright.
3. **Interface**: Melhorar acessibilidade com fontes maiores e controle de perfis ativado/desativado.

## Histórico de Decisões
- Optado por usar Playwright MCP para contornar proteções antibot em sites como Gupy.
- Perfis de busca definidos em `profile.py` e persistidos em `ui-settings.json`.
- Exclusão explícita de automação tipo n8n/no-code para focar em Engenharia Industrial (CLP/IHM).

## Próximos Passos (Plano de Ação)
1. Concluir a instalação do Playwright MCP.
2. Refatorar backend para múltiplos perfis ativos.
3. Implementar conector Gupy.
4. Ajustar dashboard visualmente.

---
*Assinado: Gemini CLI Agent (2026-04-11)*
