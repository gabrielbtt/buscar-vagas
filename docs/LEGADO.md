# Legado do Projeto

## O que e este app

Este projeto e um painel operacional para busca de vagas de emprego. O foco atual esta em coletar vagas de multiplas fontes, aplicar filtros e matching por perfil, e exibir resultados recentes de forma util para operacao manual.

O caso de uso principal hoje e busca de vagas de estagio/trainee com enfase em Engenharia Eletrica na regiao de Belo Horizonte, mas a estrutura ja suporta multiplos perfis.

## Arquitetura atual

- Backend em FastAPI
- Dashboard server-rendered em HTML/CSS/JS vanilla
- Persistencia local de configuracoes
- Persistencia local de vagas em SQLite
- Coleta por fontes configuraveis, incluindo fontes globais e fontes por perfil

## O que foi implementado

Nesta rodada, o projeto foi consolidado como um dashboard operacional mais robusto.

Principais melhorias:

- parsing defensivo do formulario de configuracoes
- suporte mais consistente a `global_sources`
- normalizacao de listas, URLs duplicadas, campos vazios e checkboxes ausentes
- compatibilidade mantida com campos legados de fontes
- reorganizacao do dashboard para separar resumo operacional, fontes globais, fontes legadas e perfis
- feedback mais claro na execucao manual de busca
- ampliacao da cobertura de testes para fluxos de UI e store de configuracoes

## Estado funcional atual

- o app sobe localmente por FastAPI/uvicorn
- a suite automatizada passou com `61` testes na ultima verificacao
- existe uma branch publicada com essa rodada: `feature/rodada-geral-robustez`
- o PR nao foi aberto automaticamente porque o ambiente nao tinha `gh` instalado

## Conceitos importantes

### Perfis

Perfis representam estrategias de busca. Cada perfil pode definir:

- palavras obrigatorias
- palavras preferenciais
- palavras bloqueadas
- locais alvo
- termos de remoto
- fontes manuais
- uso de conectores habilitados por perfil

### Fontes globais

`global_sources` e a lista principal de URLs compartilhadas pelo sistema. Ela convive com campos legados por compatibilidade, mas deve ser tratada como direcao principal da configuracao.

### Fontes legadas

Os campos `company_page_source_url` e `browser_page_source_url` foram mantidos para compatibilidade com fluxos anteriores.

## Limitacoes atuais

- varias fontes globais ainda dependem de parsing generico
- conectores dedicados para portais especificos ainda podem ser expandidos
- a qualidade de matching ainda pode ser refinada para reduzir ruido
- a abertura automatica de PR depende da instalacao do GitHub CLI no ambiente

## Proximos passos recomendados

1. criar conectores dedicados para fontes globais mais importantes
2. melhorar classificacao e observabilidade das fontes no dashboard
3. refinar scoring e criterios de aderencia por perfil
4. revisar estrategia de busca em portais dinamicos como Gupy
5. preparar um fluxo de deploy/operacao mais padronizado

## Arquivos principais para entender o sistema

- `src/app/api/ui.py`
- `src/app/services/dashboard.py`
- `src/app/services/settings_store.py`
- `src/app/templates/dashboard.html`
- `src/app/static/dashboard.css`
- `src/app/static/dashboard.js`
- `tests/test_ui.py`
- `tests/services/test_settings_store.py`
