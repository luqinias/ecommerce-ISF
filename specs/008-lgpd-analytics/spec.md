# Feature Specification: Consentimento de cookies e analytics

**Feature Branch**: `008-lgpd-analytics` · **Created**: 2026-11-04 · **Status**: Draft

**Input**: "008-lgpd-analytics: banner de cookies com opções 'só necessários' e 'aceitar todos'; GTM e Pixel carregados apenas após consentimento; IDs vindos de configuração."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visitante decide sobre cookies (Priority: P1)
Na primeira visita, um aviso flutuante explica o uso de cookies e oferece "Só os necessários" e "Aceitar todos", com o mesmo destaque visual, e "Saiba mais" (política, seção cookies). A escolha vale por 180 dias e pode ser mudada em "Preferências de cookies" no rodapé.

**Acceptance Scenarios**:
1. **Given** primeira visita, **When** a página abre, **Then** nenhum script de rastreamento é carregado e o aviso aparece.
2. **Given** "Só os necessários", **When** escolhido, **Then** o aviso some e nenhuma requisição ao GTM/Meta acontece, nem nas próximas páginas.
3. **Given** "Aceitar todos" e IDs configurados, **When** escolhido, **Then** GTM e Pixel são carregados imediatamente e nas próximas páginas.
4. **Given** consentimento dado, **When** o visitante muda para "Só os necessários", **Then** os cookies de medição conhecidos são apagados e a página recarrega sem rastreadores.
5. **Given** IDs vazios, **When** o visitante aceita, **Then** nada externo é carregado.

## Requirements *(mandatory)*
- **FR-001**: Nenhum recurso de terceiros (scripts, fontes, mapas) antes do consentimento.
- **FR-002**: IDs de GTM e Pixel vêm da configuração do site (admin), validados.
- **FR-003**: Escolha guardada em cookie próprio necessário (`isf_consent`, 180 dias, SameSite=Lax).
- **FR-004**: Revogação apaga cookies de medição (`_ga*`, `_gid`, `_gcl_au`, `_fbp`) e recarrega.
- **FR-005**: Política de privacidade descreve os cookies (seção com âncora `#cookies`).

## Success Criteria *(mandatory)*
- **SC-001**: 0 requisições a domínios de rastreamento antes do aceite (verificado por E2E).

## Assumptions
- IDs reais: pendência P19.
