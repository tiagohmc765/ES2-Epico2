# Matriz de Rastreabilidade - Sprint 1 e Sprint 2

| ID | Requisito / Regra | Endpoint | Nível | Técnica | Resultado Esperado | Pré-condições |
|---|---|---|---|---|---|---|
| TU-AUTH-01 | RN-AUTH-01: password não é guardada em claro | lógica interna | Unidade | PE | hash diferente da password original | Nenhuma |
| TU-AUTH-02 | RN-AUTH-01: validação de password correta | lógica interna | Unidade | PE | verify devolve True | Nenhuma |
| TU-AUTH-03 | RN-AUTH-01: validação de password errada | lógica interna | Unidade | PE | verify devolve False | Nenhuma |
| TU-AUTH-04 | RN-AUTH-02: login válido | POST /auth/login | Unidade | PE | devolve access e refresh token | User mockado |
| TU-AUTH-05 | RN-AUTH-02: login com password errada | POST /auth/login | Unidade | PE | InvalidCredentials | User mockado |
| TU-AUTH-06 | RN-AUTH-02: login com user inexistente | POST /auth/login | Unidade | PE | InvalidCredentials | Repo mockado |
| TU-AUTH-07 | RN-AUTH-03: refresh token válido | POST /auth/refresh | Unidade | PE | devolve novo access token | JWT mockado |
| TU-AUTH-08 | RN-AUTH-03: usar access token como refresh | POST /auth/refresh | Unidade | PE | InvalidToken | JWT mockado |
| TU-AUTH-09 | RN-AUTH-03: refresh token de user inexistente | POST /auth/refresh | Unidade | PE | InvalidToken | Repo mockado |
| TU-AUTH-10 | RN-AUTH-04: perfil Admin autorizado | endpoints protegidos | Unidade | MC/DC | acesso permitido | User em memória |
| TU-AUTH-11 | RN-AUTH-04: Técnico em recurso Admin | endpoints protegidos | Unidade | MC/DC | AccessDenied | User em memória |
| TU-AUTH-12 | RN-AUTH-04: ausência de utilizador/token | endpoints protegidos | Unidade | MC/DC | AccessDenied | User None |
| TU-AUTH-13 | RN-AUTH-04: Responsável em recurso Resp/Admin | endpoints protegidos | Unidade | MC/DC | acesso permitido | User em memória |
| TU-ERROR-01 | RN-API-01: erro de validação estruturado | API errors | Unidade | PE | 400 JSON com error=VALIDATION_ERROR | Exceção simulada |
| TU-ERROR-02 | RN-API-02: credenciais inválidas estruturadas | API errors | Unidade | PE | 401 JSON com error=INVALID_CREDENTIALS | Exceção simulada |
| TU-ERROR-03 | RN-API-02: token expirado estruturado | API errors | Unidade | PE | 401 JSON com error=TOKEN_EXPIRED | Exceção simulada |
| TU-ERROR-04 | RN-API-02: token inválido estruturado | API errors | Unidade | PE | 401 JSON com error=INVALID_TOKEN | Exceção simulada |
| TU-ERROR-05 | RN-API-03: acesso negado estruturado | API errors | Unidade | PE | 403 JSON com error=ACCESS_DENIED | Exceção simulada |
| TU-ERROR-06 | RN-API-04: erro interno estruturado | API errors | Unidade | PE | 500 JSON com error=INTERNAL_ERROR | Exceção simulada |
| TU-JWT-01 | RN-AUTH-03: criar e decodificar access token | lógica interna | Unidade | PE | payload correto (sub, email, role, type=access) | Nenhuma |
| TU-JWT-02 | RN-AUTH-03: criar e decodificar refresh token | lógica interna | Unidade | PE | payload correto (sub, type=refresh) | Nenhuma |
| TU-JWT-03 | RN-AUTH-03: decode de token malformado | lógica interna | Unidade | PE | InvalidToken | Nenhuma |
| TU-JWT-04 | RN-AUTH-03: decode de token com assinatura inválida | lógica interna | Unidade | PE | InvalidToken | Nenhuma |
| TU-JWT-05 | RN-AUTH-03: decode de token expirado | lógica interna | Unidade | VL (TTL=-1) | TokenExpired | Nenhuma |
| TU-JWT-VL-01 | RN-AUTH-03: TTL abaixo do limite inferior | lógica interna | Unidade | VL (TTL=-1) | TokenExpired imediato | Nenhuma |
| TU-JWT-VL-02 | RN-AUTH-03: TTL no limite inferior | lógica interna | Unidade | VL (TTL=1) | token válido | Nenhuma |
| TU-JWT-VL-03 | RN-AUTH-03: TTL valor nominal | lógica interna | Unidade | VL (TTL=900) | token válido | Nenhuma |
| TU-JWT-VL-04 | RN-AUTH-03: TTL no limite superior | lógica interna | Unidade | VL (TTL=86400) | token válido | Nenhuma |
| TU-JWT-VL-05 | RN-AUTH-03: TTL acima do limite superior | lógica interna | Unidade | VL (TTL=86401) | token aceite (lacuna: falta validação de máximo) | Nenhuma |
| TU-REPO-01 | RN-AUTH-02: encontrar user por email existente | lógica interna | Unidade | PE | devolve user correto | Ficheiro JSON em tmp |
| TU-REPO-02 | RN-AUTH-02: encontrar user por email inexistente | lógica interna | Unidade | PE | devolve None | Ficheiro JSON vazio |
| TU-REPO-03 | RN-AUTH-03: encontrar user por id existente | lógica interna | Unidade | PE | devolve user correto | Ficheiro JSON em tmp |
| TU-REPO-04 | RN-AUTH-03: encontrar user por id inexistente | lógica interna | Unidade | PE | devolve None | Ficheiro JSON vazio |
| TU-REPO-05 | RN-USERS-01: persistir novo utilizador | lógica interna | Unidade | PE | user gravado em JSON | Ficheiro JSON vazio |
| TU-REPO-06 | RN-USERS-01: load sem ficheiro devolve lista vazia | lógica interna | Unidade | PE | [] | Ficheiro ausente |
| TU-REPO-07 | RN-USERS-01: load com ficheiro vazio devolve lista vazia | lógica interna | Unidade | PE | [] | Ficheiro vazio |
| TI-AUTH-01 | RN-AUTH-02: login com credenciais válidas (HTTP) | POST /auth/login | Integração | PE | 200 + access_token + refresh_token | Utilizador em ficheiro de teste |
| TI-AUTH-02 | RN-AUTH-02: login com password errada (HTTP) | POST /auth/login | Integração | PE | 401 INVALID_CREDENTIALS | Utilizador em ficheiro de teste |
| TI-AUTH-03 | RN-AUTH-02: login com utilizador inexistente (HTTP) | POST /auth/login | Integração | PE | 401 INVALID_CREDENTIALS | Ficheiro de teste sem o email |
| TI-AUTH-04 | RN-API-01: login sem campo password (HTTP) | POST /auth/login | Integração | PE | 400 VALIDATION_ERROR | Nenhuma |
| TI-AUTH-04b | RN-API-01: login sem campo email (HTTP) | POST /auth/login | Integração | PE | 400 VALIDATION_ERROR | Nenhuma |
| TI-AUTH-05 | RN-AUTH-03: refresh com token válido (HTTP) | POST /auth/refresh | Integração | PE | 200 + access_token | Utilizador autenticado |
| TI-AUTH-06 | RN-AUTH-03: refresh com access token (HTTP) | POST /auth/refresh | Integração | PE | 401 INVALID_TOKEN | Utilizador autenticado |
| TI-AUTH-07 | RN-API-01: refresh sem campo (HTTP) | POST /auth/refresh | Integração | PE | 400 VALIDATION_ERROR | Nenhuma |
| TI-USERS-01 | RN-AUTH-04: Admin lista utilizadores | GET /users | Integração | PE | 200 + lista de users | Admin autenticado |
| TI-USERS-02 | RN-AUTH-04: Técnico não lista utilizadores | GET /users | Integração | PE | 403 ACCESS_DENIED | Técnico autenticado |
| TI-USERS-03 | RN-AUTH-04: sem token não lista utilizadores | GET /users | Integração | PE | 403 ACCESS_DENIED | Nenhuma |
| TI-USERS-04 | RN-USERS-01: Admin cria utilizador válido | POST /users | Integração | PE | 201 + dados do novo user (sem password) | Admin autenticado |
| TI-USERS-05 | RN-USERS-01: Admin cria utilizador com role inválido | POST /users | Integração | PE | 400 VALIDATION_ERROR | Admin autenticado |
| TI-USERS-06 | RN-USERS-01: Admin cria utilizador com email duplicado | POST /users | Integração | PE | 400 VALIDATION_ERROR | Admin autenticado; user existente |
| TI-USERS-07 | RN-AUTH-04: Técnico não cria utilizadores | POST /users | Integração | PE | 403 ACCESS_DENIED | Técnico autenticado |
| TI-USERS-08 | RN-USERS-01: Admin obtém utilizador existente | GET /users/{id} | Integração | PE | 200 + dados do user | Admin autenticado |
| TI-USERS-09 | RN-USERS-01: Admin obtém utilizador inexistente | GET /users/{id} | Integração | PE | 404 NOT_FOUND | Admin autenticado |
| TI-USERS-10 | RN-USERS-01: Admin elimina utilizador existente | DELETE /users/{id} | Integração | PE | 204 | Admin autenticado |
| TI-USERS-11 | RN-USERS-01: Admin elimina utilizador inexistente | DELETE /users/{id} | Integração | PE | 404 NOT_FOUND | Admin autenticado |
| TI-USERS-12 | RN-AUTH-03: token inválido em GET /users | GET /users | Integração | PE | 401 INVALID_TOKEN | Nenhuma |
| TI-USERS-13 | RN-AUTH-03: token inválido em GET /users/{id} | GET /users/{id} | Integração | PE | 401 INVALID_TOKEN | Nenhuma |
| TI-USERS-14 | RN-AUTH-03: token inválido em DELETE /users/{id} | DELETE /users/{id} | Integração | PE | 401 INVALID_TOKEN | Nenhuma |
| TI-USERS-05b | RN-USERS-01: Admin cria utilizador sem campos obrigatórios | POST /users | Integração | PE | 400 VALIDATION_ERROR | Admin autenticado |

## Sprint 2 — Herbs (Importação CSV) e Plans (Criação)

| ID | Requisito / Regra | Endpoint | Nível | Técnica | Resultado Esperado | Pré-condições |
|---|---|---|---|---|---|---|
| TU-HERB-01 | RN-HERBS-01: linha com campos obrigatórios é válida | POST /herbs/import | Unidade | PE | classify_row devolve 'valid' | Nenhuma |
| TU-HERB-02 | RN-HERBS-01: linha sem name mas com family é parcial | POST /herbs/import | Unidade | PE | classify_row devolve 'partial' | Nenhuma |
| TU-HERB-03 | RN-HERBS-01: linha sem nenhum campo obrigatório é inválida | POST /herbs/import | Unidade | PE | classify_row devolve 'invalid' | Nenhuma |
| TU-HERB-04 | RN-HERBS-01: linha com name mas sem family é parcial | POST /herbs/import | Unidade | PE | classify_row devolve 'partial' | Nenhuma |
| TU-HERB-05 | RN-HERBS-01: linha só com campos opcionais é inválida | POST /herbs/import | Unidade | PE | classify_row devolve 'invalid' | Nenhuma |
| TU-HERB-06 | RN-HERBS-02: conteúdo vazio lança EmptyImportFile | POST /herbs/import | Unidade | PE | EmptyImportFile | Nenhuma |
| TU-HERB-07 | RN-HERBS-02: apenas cabeçalho sem linhas lança EmptyImportFile | POST /herbs/import | Unidade | PE | EmptyImportFile | Nenhuma |
| TU-HERB-08 | RN-HERBS-02: conteúdo só de espaços lança EmptyImportFile | POST /herbs/import | Unidade | PE | EmptyImportFile | Nenhuma |
| TU-HERB-09 | RN-HERBS-01: ficheiro com todas as linhas válidas | POST /herbs/import | Unidade | PE | totals.valid=2, partial=0, invalid=0 | Nenhuma |
| TU-HERB-10 | RN-HERBS-01: ficheiro com todas as linhas inválidas | POST /herbs/import | Unidade | PE | totals.valid=0, invalid=2 | Nenhuma |
| TU-HERB-11 | RN-HERBS-01: ficheiro misto conta corretamente | POST /herbs/import | Unidade | PE | totals: valid=1, partial=1, invalid=1 | Nenhuma |
| TU-HERB-12 | RN-HERBS-01: espaços extra em campos são normalizados | POST /herbs/import | Unidade | PE | name e family sem espaços | Nenhuma |
| TU-HERB-13 | RN-HERBS-01: ficheiro com uma única linha válida | POST /herbs/import | Unidade | PE | totals.total=1, valid=1 | Nenhuma |
| TU-PLAN-PE-01 | RN-PLANS-01: tipo regular aceite | POST /plans | Unidade | PE | validate_plan devolve plano com type=regular | Nenhuma |
| TU-PLAN-PE-02 | RN-PLANS-01: tipo emergencia aceite | POST /plans | Unidade | PE | validate_plan devolve plano com type=emergencia | Nenhuma |
| TU-PLAN-PE-03 | RN-PLANS-01: tipo pontual com autorização aceite | POST /plans | Unidade | PE | validate_plan devolve plano com authorized_by=3 | Nenhuma |
| TU-PLAN-PE-04 | RN-PLANS-01: tipo inválido rejeitado | POST /plans | Unidade | PE | PlanValidationError | Nenhuma |
| TU-PLAN-PE-05 | RN-PLANS-01: tipo vazio rejeitado | POST /plans | Unidade | PE | PlanValidationError | Nenhuma |
| TU-PLAN-PE-06 | RN-PLANS-01: campo cycle_days em falta | POST /plans | Unidade | PE | PlanValidationError com 'cycle_days' | Nenhuma |
| TU-PLAN-PE-07 | RN-PLANS-01: valor não numérico em temp_min | POST /plans | Unidade | PE | PlanValidationError com 'não numérico' | Nenhuma |
| TU-PLAN-PE-08 | RN-PLANS-01: campo temp_min em falta | POST /plans | Unidade | PE | PlanValidationError com 'temp_min' | Nenhuma |
| TU-PLAN-PE-09 | RN-PLANS-01: campo humidity_min em falta | POST /plans | Unidade | PE | PlanValidationError com 'humidity_min' | Nenhuma |
| TU-PLAN-PE-10 | RN-PLANS-01: campo luminosity_min em falta | POST /plans | Unidade | PE | PlanValidationError com 'luminosity_min' | Nenhuma |
| TU-PLAN-PE-11 | RN-PLANS-01: cycle_days não inteiro rejeitado | POST /plans | Unidade | PE | PlanValidationError com 'não inteiro' | Nenhuma |
| TU-PLAN-VL-TEMP-01 | RN-PLANS-02: temp_min=17 (abaixo mínimo) rejeitado | POST /plans | Unidade | VL | PlanValidationError | Nenhuma |
| TU-PLAN-VL-TEMP-02 | RN-PLANS-02: temp_min=18 (limite inferior) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-TEMP-03 | RN-PLANS-02: temp_min=23 (valor nominal) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-TEMP-04 | RN-PLANS-02: temp_max=28 (limite superior) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-TEMP-05 | RN-PLANS-02: temp_max=29 (acima máximo) rejeitado | POST /plans | Unidade | VL | PlanValidationError | Nenhuma |
| TU-PLAN-VL-HUM-01 | RN-PLANS-02: humidity_min=39 (abaixo mínimo) rejeitado | POST /plans | Unidade | VL | PlanValidationError | Nenhuma |
| TU-PLAN-VL-HUM-02 | RN-PLANS-02: humidity_min=40 (limite inferior) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-HUM-03 | RN-PLANS-02: humidity_min=60 (valor nominal) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-HUM-04 | RN-PLANS-02: humidity_max=80 (limite superior) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-HUM-05 | RN-PLANS-02: humidity_max=81 (acima máximo) rejeitado | POST /plans | Unidade | VL | PlanValidationError | Nenhuma |
| TU-PLAN-VL-LUX-01 | RN-PLANS-02: luminosity_min=4999 (abaixo mínimo) rejeitado | POST /plans | Unidade | VL | PlanValidationError | Nenhuma |
| TU-PLAN-VL-LUX-02 | RN-PLANS-02: luminosity_min=5000 (limite inferior) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-LUX-03 | RN-PLANS-02: luminosity_min=15000 (valor nominal) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-LUX-04 | RN-PLANS-02: luminosity_max=25000 (limite superior) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-LUX-05 | RN-PLANS-02: luminosity_max=25001 (acima máximo) rejeitado | POST /plans | Unidade | VL | PlanValidationError | Nenhuma |
| TU-PLAN-VL-CYCLE-01 | RN-PLANS-02: cycle_days=0 (abaixo mínimo) rejeitado | POST /plans | Unidade | VL | PlanValidationError | Nenhuma |
| TU-PLAN-VL-CYCLE-02 | RN-PLANS-02: cycle_days=1 (limite inferior) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-CYCLE-03 | RN-PLANS-02: cycle_days=90 (valor nominal) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-CYCLE-04 | RN-PLANS-02: cycle_days=365 (limite superior) aceite | POST /plans | Unidade | VL | plano válido | Nenhuma |
| TU-PLAN-VL-CYCLE-05 | RN-PLANS-02: cycle_days=366 (acima máximo) rejeitado | POST /plans | Unidade | VL | PlanValidationError | Nenhuma |
| TU-PLAN-MCDC-01 | RN-PLANS-03: C1=F,C2=F — regular sem auth aceite | POST /plans | Unidade | MC/DC | plano regular aceite, authorized_by=None | Nenhuma |
| TU-PLAN-MCDC-02 | RN-PLANS-03: C1=T,C2=F — pontual sem auth rejeitado | POST /plans | Unidade | MC/DC | UnauthorizedPontualPlan | Nenhuma |
| TU-PLAN-MCDC-03 | RN-PLANS-03: C1=T,C2=T — pontual com auth aceite | POST /plans | Unidade | MC/DC | plano pontual aceite, authorized_by=3 | Nenhuma |
| TU-PLAN-MCDC-04 | RN-PLANS-03: C1=F,C2=T — regular com auth aceite | POST /plans | Unidade | MC/DC | plano regular aceite, authorized_by=3 | Nenhuma |

## Tabela Inversa: Requisito → Casos de Teste

| Requisito | Casos de Teste |
|---|---|
| RN-AUTH-01: password armazenada com hash | TU-AUTH-01, TU-AUTH-02, TU-AUTH-03 |
| RN-AUTH-02: autenticação por email/password | TU-AUTH-04..06, TI-AUTH-01..04b |
| RN-AUTH-03: emissão e renovação de tokens JWT | TU-AUTH-07..09, TU-JWT-01..05, TU-JWT-VL-01..05, TI-AUTH-05..07, TI-USERS-12..14 |
| RN-AUTH-04: controlo de acesso por perfil | TU-AUTH-10..13, TI-USERS-01..03, TI-USERS-07 |
| RN-API-01..04: respostas de erro estruturadas | TU-ERROR-01..06, TI-AUTH-04, TI-AUTH-04b, TI-AUTH-07 |
| RN-USERS-01: gestão de utilizadores (CRUD) | TU-REPO-01..07, TI-USERS-04..05b, TI-USERS-06..11 |
| RN-HERBS-01: classificação de linhas CSV | TU-HERB-01..05, TU-HERB-09..13 |
| RN-HERBS-02: ficheiro vazio rejeitado | TU-HERB-06, TU-HERB-07, TU-HERB-08 |
| RN-PLANS-01: tipo de plano e campos obrigatórios | TU-PLAN-PE-01..11 |
| RN-PLANS-02: intervalos ambientais e duração | TU-PLAN-VL-TEMP-01..05, TU-PLAN-VL-HUM-01..05, TU-PLAN-VL-LUX-01..05, TU-PLAN-VL-CYCLE-01..05 |
| RN-PLANS-03: plano pontual exige autorização | TU-PLAN-MCDC-01..04 |

Nota: os endpoints existem na API FastAPI, mas os testes unitários incidem sobre a lógica isolada.
