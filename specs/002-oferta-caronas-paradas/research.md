# Research — Feature 002

**Data**: 2026-11-22. Base: spec aprovada para planejamento, stack e código locais. Revisão técnica delegada somente leitura. Não houve pesquisa externa nem alteração de código.

## 1. Catálogo persistente

**Decision**: `RoutePoint` com código estável, nome de exibição e catálogo inicial por migração de dados reversível. Referências protegidas por FK PROTECT.
**Rationale**: oferece integridade e identidade comum ao futuro matching; mantém históricos sem depender de texto livre.
**Alternatives considered**: JSON em memória (sem integridade referencial); coordenadas/mapas (fora do recorte aprovado).

Catálogo demonstrativo inicial: `terminal-central`/Terminal Central, `bairro-america`/Bairro América, `campus-univille`/Campus Univille, `terminal-norte`/Terminal Norte. São rótulos públicos de demonstração, sem endereços ou informação de trajetos reais. Migração utiliza modelos históricos e códigos; não importa modelos vivos. Não oferecer edição de catálogo ao usuário.

## 2. Snapshot de veículo

**Decision**: modelo, cor e placa na própria oferta. Pré-preencher formulário com os dados da última oferta do autor (created_at e id decrescentes); usuário confere e envia os três campos obrigatórios.
**Rationale**: reutiliza informações sem alterar publicações anteriores, sem gestão de frota.
**Alternatives considered**: cadastro separado de veículos/perfil do motorista (complexidade sem requisito); FK mutável para veículo (mudanças retroativas).

Normalização: trim em campos textuais; placa também em maiúsculas. Não impor regex nacional nem alegar consulta a cadastro real.

## 3. Integridade e fronteira de escrita

**Decision**: serviço atômico com rechecagem de usuário sob bloqueio; CHECKs estruturais e UNIQUE no PostgreSQL; validação do itinerário completo no serviço.
**Rationale**: FK não prova papel/estado; CHECK não consulta outras tabelas; ordem contígua e unicidade incluindo extremos atravessam linhas.
**Alternatives considered**: limit_choices_to como segurança (insuficiente), triggers de domínio (desnecessários na PoC), NOW em CHECK (regra temporal inadequada para histórico).

`full_clean` não roda em bulk_create/QuerySet.update; publicar somente pelo serviço. Não alegar garantia SQL de papel, horário futuro ou unicidade de extremos contra paradas. Testar exatamente cada camada prometida.

## 4. Interface e autorização

**Decision**: Form + formset de paradas, ordem DOM/lista enviada; servidor gera posições 1..N. Botões de adicionar/remover linhas com JavaScript mínimo local, sem dependência, preservando ordem visível; teste adicional sem JS com formset pronto.
**Rationale**: listas reordenadas por nome/PK quebrariam o trajeto; sessão define autoria.
**Alternatives considered**: texto livre separado por vírgula (ambíguo), posições arbitrárias do cliente como fonte de verdade (inseguro).

Middleware acadêmico existente cuida de anônimo/pendente. Mixin próprio de motorista ativo usado em ambas as views, retornando 403 ao passageiro. Toda queryset filtra `driver=request.user` antes de aplicar qualquer entrada externa.

## 5. Medição

**Decision**: relatório e bloco de README separados da Feature 001; testar rides com pytest-cov/branch e limiar combinado e separado de linhas/ramificações >=80%; executar regressão de accounts antes de entrega.
**Rationale**: não misturar indicadores de features ou contar testes apenas coletados.
**Alternatives considered**: sobrescrever script/relatórios da Feature 001 (perde separação), declarar cobertura de templates via coverage.py (não mede HTML; usar testes de renderização).