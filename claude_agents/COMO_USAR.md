# TradingAgents para Claude.ai — Guia de Instalação e Uso

Sem servidor. Sem API key. Funciona em desktop e mobile.

---

## Arquivos disponíveis

```
orquestrador.md          ← instrução principal do Project (cole aqui)
agentes/
  analista_mercado.md    ← análise técnica
  analista_noticias.md   ← notícias e macro
  analista_sentimento.md ← sentimento e redes sociais
  analista_fundamentos.md ← fundamentos financeiros
  pesquisador_bull.md    ← argumento otimista
  pesquisador_bear.md    ← argumento pessimista
  gestor_pesquisa.md     ← síntese do debate Bull/Bear
  trader.md              ← proposta de transação
  risco_agressivo.md     ← análise de risco agressiva
  risco_conservador.md   ← análise de risco conservadora
  risco_neutro.md        ← análise de risco neutra
  gestor_portfolio.md    ← decisão final
```

---

## Instalação — Opção A: Projeto único (recomendado)

Esta é a forma mais simples. O orquestrador executa todo o pipeline em uma conversa só.

**Passo 1:** No Claude.ai, crie um novo Project chamado "TradingAgents".

**Passo 2:** Cole o conteúdo de `orquestrador.md` nas **Custom Instructions** (Instruções Personalizadas) do projeto.

**Passo 3:** Faça upload dos arquivos da pasta `agentes/` como **Knowledge** (Conhecimento) do projeto. Isso permite que o orquestrador os referencie se precisar de detalhes de um papel específico.

**Passo 4:** Ative a pesquisa web no projeto (necessária para dados em tempo real).

**Pronto.** Agora basta abrir o projeto e digitar:
> "Analise PETR4"
> "Analise BTC-USD para 2026-05-15"
> "Análise rápida NVDA"

---

## Instalação — Opção B: Projetos separados por agente

Use esta opção se quiser usar os agentes individualmente, sem o pipeline completo. Útil para análises focadas.

Para cada arquivo em `agentes/`, crie um Project separado no Claude.ai com o conteúdo do arquivo como Custom Instructions. Exemplos:

| Project | Arquivo | Uso |
|---|---|---|
| "Analista Técnico" | `analista_mercado.md` | só análise de preço/indicadores |
| "Analista de Notícias" | `analista_noticias.md` | só notícias e macro |
| "Analista de Fundamentos" | `analista_fundamentos.md` | só fundamentos |
| "Debate de Investimento" | `pesquisador_bull.md` + `pesquisador_bear.md` | debate Bull/Bear |
| "Gestor de Portfólio" | `gestor_portfolio.md` | só a decisão final |

---

## Uso no mobile

Os projetos do Claude.ai funcionam normalmente no app mobile (iOS e Android). Basta abrir o app, selecionar o projeto "TradingAgents" e digitar o pedido. A pesquisa web também está disponível no mobile.

---

## Avaliação: Orquestrador único vs. Skills multiagênticas

### Por que o orquestrador único é melhor para este caso

| Critério | Orquestrador único | Skills multiagênticas |
|---|---|---|
| Funciona no Claude.ai web | ✅ Sim | ❌ Não (só Claude Code CLI) |
| Funciona no mobile | ✅ Sim | ❌ Não |
| Requer servidor/API | ❌ Não | ⚠️ Depende |
| Execução paralela dos analistas | ❌ Sequencial | ✅ Paralelo |
| Qualidade dos dados | ⚠️ Web search (boa) | ✅ yfinance direto (excelente) |
| Configuração necessária | Mínima (colar prompt) | Alta (CLI + Python + API) |

**Skills multiagênticas** (via Claude Code CLI) permitiriam rodar os 4 analistas em paralelo, reduzindo o tempo total de análise. Mas exigem Claude Code instalado, acesso ao Python local e uma API key — e **não funcionam no mobile**.

**Conclusão:** Para o objetivo de usar via Claude.ai em desktop e mobile sem API, o orquestrador único é claramente superior. As skills multiagênticas seriam um enhancement válido apenas se você quiser rodar o pipeline completo pelo terminal com mais velocidade.

---

## Dicas de uso

- **Ações brasileiras:** pode digitar sem o `.SA` (ex: "analise PETR4" funciona)
- **Cripto:** pode digitar o símbolo simples (ex: "analise BTC") ou o par completo (ex: "analise BTC-USD")
- **Data:** se não especificar, o orquestrador usa a data de hoje
- **Análise parcial:** use os comandos "só técnica TICKER", "só notícias TICKER" etc. para análises mais rápidas
- **Pesquisa web:** certifique-se de que a pesquisa web está ativada no projeto para que os agentes obtenham dados reais

---

## Aviso regulatório

As análises geradas são para fins educacionais e de pesquisa. Não constituem recomendação de investimento. Decisões de compra e venda são de responsabilidade exclusiva do investidor.
