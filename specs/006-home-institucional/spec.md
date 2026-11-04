# Feature Specification: Home e páginas institucionais

**Feature Branch**: `006-home-institucional` · **Created**: 2026-11-04 · **Status**: Draft

**Input**: "006-home-institucional: home com todas as seções da referência, montada a partir de conteúdo editável no admin (banners, diferenciais, passos, prazos/campanhas, portfólio, depoimentos, FAQ), mais as páginas Sobre, Contato, Novidades, Termos e Privacidade."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Home com todas as seções (Priority: P1)
O visitante encontra, na ordem da referência: hero com selo de coleções, título com destaque, CTAs e cards de prova; vitrine por categoria em trilhos ("Acabou de chegar" + categorias marcadas); próximas coleções + banner da coleção principal; portfólio de projetos com "Ver mais"; tiles das categorias com contagem; "Como funciona" em 4 passos; faixa de prazos; "Por que nós" + depoimentos; FAQ em acordeão.

**Acceptance Scenarios**:
1. **Given** conteúdo cadastrado, **When** a home abre, **Then** as 9 seções aparecem na ordem acima, cada uma com um `h2`, e a página tem um único `h1` (o do hero).
2. **Given** nenhuma coleção com prazo, **When** a home abre, **Then** a faixa de prazos não mostra cards e o CTA continua.
3. **Given** nenhum depoimento ativo, **When** a home abre, **Then** a parte de depoimentos não aparece (nada inventado).
4. **Given** mais de 8 projetos no portfólio, **When** "Ver mais projetos" é clicado, **Then** os demais aparecem e o botão vira "Ver menos".
5. **Given** o FAQ, **When** uma pergunta é clicada, **Then** a resposta abre sem fechar as outras.

### User Story 2 - Equipe edita a home sem programador (Priority: P1)
No admin, a equipe edita banner do hero, cards de prova, diferenciais, passos, textos de cada seção, portfólio, depoimentos e FAQ, com ordem e ativação.

### User Story 3 - Páginas institucionais (Priority: P2)
Sobre, Termos de uso e Política de privacidade são páginas editáveis com seções (as legais com sumário lateral e âncoras numeradas). Contato mostra canais e horário vindos da configuração, um formulário de mensagem (gravado como lead com origem "Contato", com consentimento, honeypot e limite de taxa) e o FAQ de contato. Novidades lista os produtos mais recentes com destaque dos 3 últimos, chips por categoria e "Carregar mais".

### Edge Cases
- Sem banner ativo: hero com textos padrão e `[DEFINIR]`.
- Página institucional inativa: 404.
- Contato sem WhatsApp configurado: card mostra `[DEFINIR]`.
- Mapa: não carrega iframe de terceiros; só link "Abrir rota" (LGPD).

## Requirements *(mandatory)*
- **FR-001**: Home composta só de dados editáveis + catálogo (nenhum texto de negócio fixo além de defaults genéricos).
- **FR-002**: Entidades editáveis: Banner, Diferencial (cards de prova e "por que nós"), Passo, Texto de seção, Projeto do portfólio, Depoimento, Pergunta frequente, Página (com seções).
- **FR-003**: Vitrine e tiles usam categorias marcadas para a home e contagens reais.
- **FR-004**: Contato grava a mensagem como lead (origem contato) e notifica a equipe.
- **FR-005**: Novidades: produtos ordenados do mais novo, 20 por vez, "Carregar mais" sem recarregar (com link de página como fallback).
- **FR-006**: Conteúdo de demonstração carregável por comando, marcado como demonstração, sem depoimentos e sem dados reais inventados.

## Success Criteria *(mandatory)*
- **SC-001**: Home sem CLS perceptível (≤ 0,1), ao contrário da referência (0,13).
- **SC-002**: Todas as seções editáveis pelo admin.
- **SC-003**: Home, Sobre, Contato, Novidades, Termos e Privacidade sem rolagem horizontal em 390 px.

## Assumptions
- Textos institucionais reais são pendência P3/P5/P18; o demo usa textos genéricos e `[DEFINIR]`.
