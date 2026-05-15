# Técnicas de Teste Aplicadas

## Particionamento de Equivalência

### Login

| Classe | Entrada | Resultado |
|---|---|---|
| Válida | email existente + password correta | tokens emitidos |
| Inválida | email existente + password errada | InvalidCredentials |
| Inválida | email inexistente | InvalidCredentials |

### Refresh Token

| Classe | Entrada | Resultado |
|---|---|---|
| Válida | token do tipo refresh | novo access token |
| Inválida | token do tipo access | InvalidToken |
| Inválida | token de utilizador inexistente | InvalidToken |

### Perfis

| Classe | Entrada | Resultado |
|---|---|---|
| Válida | ADMIN em recurso ADMIN | acesso permitido |
| Inválida | TECNICO em recurso ADMIN | AccessDenied |
| Inválida | sem utilizador/token | AccessDenied |

## Valores Limite

Para os parâmetros numéricos do módulo de autenticação são testados 5 valores: abaixo do limite inferior, no limite inferior, valor nominal, no limite superior e acima do limite superior.

### TTL do Access Token (segundos) — Intervalo aceitável: [1, 86400]

| Caso | TTL (s) | Posição | Resultado Esperado | Teste |
|---|---|---|---|---|
| Abaixo do mínimo | -1 | < limite inferior | `TokenExpired` ao fazer decode | TU-JWT-VL-01 |
| Limite inferior | 1 | = limite inferior | token criado e decodificado com sucesso | TU-JWT-VL-02 |
| Valor nominal | 900 | interior | token criado e decodificado com sucesso | TU-JWT-VL-03 |
| Limite superior | 86400 | = limite superior | token criado e decodificado com sucesso | TU-JWT-VL-04 |
| Acima do máximo | 86401 | > limite superior | token aceite (sem validação de máximo; regista lacuna) | TU-JWT-VL-05 |

**Nota:** TU-JWT-VL-01 duplica TU-JWT-05 por completude da tabela. TU-JWT-VL-05 evidencia uma lacuna de validação: o `JwtProvider` não rejeita TTL superiores a 86400 s; deve ser adicionada validação em produção.

## MC/DC

Decisão em `require_role`:

```python
if user is None:
    raise AccessDenied

if user.get("role") not in allowed_roles:
    raise AccessDenied
```

Condições atómicas:

- C1: user is None
- C2: role não pertence aos perfis permitidos

| Caso | C1 | C2 | Resultado |
|---|---|---|---|
| Sem user | True | N/A | AccessDenied |
| User com role inválida | False | True | AccessDenied |
| User com role válida | False | False | True |

Cada condição altera isoladamente o resultado da decisão.

---

## Sprint 2

### Particionamento de Equivalência — Importação CSV de Ervas

Classificação de cada linha do ficheiro CSV:

| Classe | Condição | Resultado (`classify_row`) |
|---|---|---|
| Válida | `name` e `family` presentes e não vazios | `"valid"` |
| Parcial | apenas um dos campos obrigatórios presente | `"partial"` |
| Inválida | nenhum campo obrigatório útil | `"invalid"` |

Ficheiro completo:

| Classe | Condição | Resultado (`parse_csv`) |
|---|---|---|
| Válida | ficheiro com linhas todas válidas | totals.valid = N, invalid = 0, partial = 0 |
| Mista | mistura de valid/partial/invalid | contagens corretas por categoria |
| Inválida | ficheiro vazio ou só cabeçalho | `EmptyImportFile` |

### Particionamento de Equivalência — Tipo de Plano

| Classe | Valor de `type` | Resultado |
|---|---|---|
| Válida | `"regular"` | plano aceite |
| Válida | `"emergencia"` | plano aceite |
| Válida | `"pontual"` + `authorized_by` definido | plano aceite |
| Inválida | qualquer outro valor (ex. `"desconhecido"`) | `PlanValidationError` |
| Inválida | string vazia `""` | `PlanValidationError` |

### Análise de Valores Limite — Parâmetros do Plano

| Parâmetro | Intervalo | Abaixo mínimo | Limite inf. | Nominal | Limite sup. | Acima máximo |
|---|---|---|---|---|---|---|
| Temperatura (°C) | [18, 28] | 17 ❌ | 18 ✅ | 23 ✅ | 28 ✅ | 29 ❌ |
| Humidade (%) | [40, 80] | 39 ❌ | 40 ✅ | 60 ✅ | 80 ✅ | 81 ❌ |
| Luminosidade (lux) | [5000, 25000] | 4999 ❌ | 5000 ✅ | 15000 ✅ | 25000 ✅ | 25001 ❌ |
| Duração ciclo (dias) | [1, 365] | 0 ❌ | 1 ✅ | 90 ✅ | 365 ✅ | 366 ❌ |

### MC/DC — Validação do Plano Pontual

Decisão em `validate_plan`:

```python
if plan_type == "pontual" and authorized_by is None:
    raise UnauthorizedPontualPlan(...)
```

Condições atómicas:
- **C1**: `type == "pontual"`
- **C2**: `authorized_by is not None`

| Caso | C1 | C2 | Resultado | Teste |
|---|---|---|---|---|
| MCDC-01 | False | False | aceite (regular sem auth) | TU-PLAN-MCDC-01 |
| MCDC-02 | True | False | rejeitado (pontual sem auth) | TU-PLAN-MCDC-02 |
| MCDC-03 | True | True | aceite (pontual com auth) | TU-PLAN-MCDC-03 |
| MCDC-04 | False | True | aceite (regular com auth ignorada) | TU-PLAN-MCDC-04 |

**Demonstração MC/DC:**
- MCDC-01 vs MCDC-02: C1 varia (F→T), C2=False → resultado muda (aceite→rejeitado) — C1 afeta isoladamente o resultado ✓
- MCDC-02 vs MCDC-03: C2 varia (F→T), C1=True → resultado muda (rejeitado→aceite) — C2 afeta isoladamente o resultado ✓

---

## Sprint 3

### Particionamento de Equivalência — HerbService

#### `list_herbs` e `get_herb`

| Classe | ID | Condição | Resultado |
|---|---|---|---|
| Válida | EC-SVC-LIST-V1 | repositório com ervas | lista com todas as ervas devolvida |
| Válida (limite) | EC-SVC-LIST-V2 | repositório vazio | lista vazia devolvida |
| Válida | EC-SVC-GET-V1 | `herb_id` existente no repositório | erva correspondente devolvida |
| Inválida | EC-SVC-GET-I1 | `herb_id` inexistente | `HerbNotFound` lançado |

#### `create_herb`

| Classe | ID | Condição | Resultado |
|---|---|---|---|
| Válida | EC-SVC-CREATE-V1 | `name` e `family` presentes e não vazios | erva criada e guardada |
| Inválida | EC-SVC-CREATE-I1 | `name` ausente ou só espaços | `HerbValidationError` |
| Inválida | EC-SVC-CREATE-I2 | `family` ausente ou só espaços | `HerbValidationError` |

#### `import_from_csv`

| Classe | ID | Condição | Resultado |
|---|---|---|---|
| Válida | EC-SVC-IMPORT-V1 | CSV com linhas válidas | `save_many` chamado com as válidas; relatório devolvido |
| Inválida | EC-SVC-IMPORT-I1 | CSV vazio (sem conteúdo) | `EmptyImportFile` propagado |
| Inválida | EC-SVC-IMPORT-I2 | CSV sem nenhuma linha válida | `save_many` não chamado |

### Particionamento de Equivalência — HerbJsonRepository

| Classe | ID | Método | Condição | Resultado |
|---|---|---|---|---|
| Válida | EC-REPO-FIND-V1 | `find_by_id` | id existente no ficheiro | dicionário da erva devolvido |
| Inválida | EC-REPO-FIND-I1 | `find_by_id` | id inexistente | `None` |
| Válida | EC-REPO-NAME-V1 | `find_by_name` | nome existente (case-insensitive) | dicionário da erva devolvido |
| Inválida | EC-REPO-NAME-I1 | `find_by_name` | nome inexistente | `None` |
| Válida (limite) | EC-REPO-FILE-I1 | `list_all` | ficheiro não existe | lista vazia, sem erro |
| Inválida | EC-REPO-FILE-I2 | `list_all` | ficheiro existe mas está vazio | lista vazia |
| Válida | EC-REPO-FILE-V1 | `list_all` | ficheiro com dados | lista com todas as ervas |
| Válida (limite) | EC-REPO-SAVE-V2 | `save` | repositório vazio | erva recebe `id=1` |
| Válida | EC-REPO-SAVE-V1 | `save` | repositório com ervas | `id = max(ids) + 1` atribuído |
| Válida | EC-REPO-MANY-V1 | `save_many` | lista com N ervas | ids sequenciais atribuídos; todas persistidas |
| Válida (limite) | EC-REPO-MANY-V2 | `save_many` | lista vazia | repositório inalterado |

### Particionamento de Equivalência — PlanService

#### `list_plans` e `get_plan`

| Classe | ID | Condição | Resultado |
|---|---|---|---|
| Válida | EC-PSVC-LIST-V1 | repositório com planos | lista completa devolvida |
| Válida (limite) | EC-PSVC-LIST-V2 | repositório vazio | lista vazia devolvida |
| Válida | EC-PSVC-GET-V1 | `plan_id` existente | plano correspondente devolvido |
| Inválida | EC-PSVC-GET-I1 | `plan_id` inexistente | `PlanNotFound` lançado |

#### `create_plan`

| Classe | ID | Condição | Resultado |
|---|---|---|---|
| Válida | EC-PSVC-CREATE-V1 | dados válidos, tipo `regular` | plano validado, guardado e devolvido |
| Inválida | EC-PSVC-CREATE-I1 | tipo de plano inválido | `PlanValidationError` propagada |
| Inválida | EC-PSVC-CREATE-I1 | `temp_min` abaixo do mínimo | `PlanValidationError` propagada |
| Válida | EC-PSVC-CREATE-V2 | plano `pontual` com `authorized_by` | aceite e guardado |
| Inválida | EC-PSVC-CREATE-I2 | plano `pontual` sem `authorized_by` | `UnauthorizedPontualPlan` lançado |

### Particionamento de Equivalência — PlanJsonRepository

| Classe | ID | Método | Condição | Resultado |
|---|---|---|---|---|
| Válida (limite) | EC-PREPO-FILE-I1 | `list_all` | ficheiro não existe | lista vazia, sem erro |
| Inválida | EC-PREPO-FILE-I2 | `list_all` | ficheiro existe mas vazio | lista vazia |
| Válida | EC-PREPO-FILE-V1 | `list_all` | ficheiro com dados | lista com todos os planos |
| Válida | EC-PREPO-FIND-V1 | `find_by_id` | id existente | dicionário do plano devolvido |
| Inválida | EC-PREPO-FIND-I1 | `find_by_id` | id inexistente | `None` |
| Válida (limite) | EC-PREPO-SAVE-V2 | `save` | repositório vazio | plano recebe `id=1` |
| Válida | EC-PREPO-SAVE-V1 | `save` | repositório com dados | `id = max(ids) + 1` atribuído e persistido |

### MC/DC — HerbService.import_from_csv

Decisão em `import_from_csv`:

```python
validas = [h for h in parsed.herbs if h["status"] == "valid"]
if validas:
    self._repository.save_many(validas)
```

Condições atómicas:
- **C1**: existem linhas com `status == "valid"` no CSV

| Caso | C1 | Resultado | Teste |
|---|---|---|---|
| CSV com válidas | True | `save_many` chamado | TU-HERB-SVC-10 |
| CSV sem válidas | False | `save_many` não chamado | TU-HERB-SVC-11 |

C1 é a única condição — MC/DC satisfeita com os dois casos (True e False, cada um determinante).

### MC/DC — PlanService.create_plan (autorização pontual)

Decisão em `create_plan` / `validate_plan`:

```python
if plan_type == "pontual" and authorized_by is None:
    raise UnauthorizedPontualPlan(...)
```

Condições atómicas:
- **C1**: `type == "pontual"`
- **C2**: `authorized_by is None`

| Caso | C1 | C2 | Resultado | Teste |
|---|---|---|---|---|
| Regular sem auth | False | True | aceite | TU-PLAN-SVC-11 |
| Pontual sem auth | True | True | `UnauthorizedPontualPlan` | TU-PLAN-SVC-09 |
| Pontual com auth | True | False | aceite | TU-PLAN-SVC-08 |
| Regular com auth | False | False | aceite | TU-PLAN-SVC-10 |

**Demonstração MC/DC:**
- TU-PLAN-SVC-11 vs TU-PLAN-SVC-09: C1 varia (F→T), C2=True → resultado muda (aceite→rejeitado) — C1 afeta isoladamente ✓
- TU-PLAN-SVC-09 vs TU-PLAN-SVC-08: C2 varia (T→F), C1=True → resultado muda (rejeitado→aceite) — C2 afeta isoladamente ✓


---

## Sprint 3

### Particionamento de Equivalência — HerbService

#### `list_herbs` e `get_herb`

| Classe | ID | Condição | Resultado |
|---|---|---|---|
| Válida | EC-SVC-LIST-V1 | repositório com ervas | lista com todas as ervas devolvida |
| Válida (limite) | EC-SVC-LIST-V2 | repositório vazio | lista vazia devolvida |
| Válida | EC-SVC-GET-V1 | `herb_id` existente no repositório | erva correspondente devolvida |
| Inválida | EC-SVC-GET-I1 | `herb_id` inexistente | `HerbNotFound` lançado |

#### `create_herb`

| Classe | ID | Condição | Resultado |
|---|---|---|---|
| Válida | EC-SVC-CREATE-V1 | `name` e `family` presentes e não vazios | erva criada e guardada |
| Inválida | EC-SVC-CREATE-I1 | `name` ausente ou só espaços | `HerbValidationError` |
| Inválida | EC-SVC-CREATE-I2 | `family` ausente ou só espaços | `HerbValidationError` |

#### `import_from_csv`

| Classe | ID | Condição | Resultado |
|---|---|---|---|
| Válida | EC-SVC-IMPORT-V1 | CSV com linhas válidas | `save_many` chamado com as válidas; relatório devolvido |
| Inválida | EC-SVC-IMPORT-I1 | CSV vazio (sem conteúdo) | `EmptyImportFile` propagado |
| Inválida | EC-SVC-IMPORT-I2 | CSV sem nenhuma linha válida | `save_many` não chamado |

### Particionamento de Equivalência — HerbJsonRepository

| Classe | ID | Método | Condição | Resultado |
|---|---|---|---|---|
| Válida | EC-REPO-FIND-V1 | `find_by_id` | id existente no ficheiro | dicionário da erva devolvido |
| Inválida | EC-REPO-FIND-I1 | `find_by_id` | id inexistente | `None` |
| Válida | EC-REPO-NAME-V1 | `find_by_name` | nome existente (case-insensitive) | dicionário da erva devolvido |
| Inválida | EC-REPO-NAME-I1 | `find_by_name` | nome inexistente | `None` |
| Válida (limite) | EC-REPO-FILE-I1 | `list_all` | ficheiro não existe | lista vazia, sem erro |
| Inválida | EC-REPO-FILE-I2 | `list_all` | ficheiro existe mas vazio | lista vazia |
| Válida | EC-REPO-FILE-V1 | `list_all` | ficheiro com dados | lista com todas as ervas |
| Válida (limite) | EC-REPO-SAVE-V2 | `save` | repositório vazio | erva recebe `id=1` |
| Válida | EC-REPO-SAVE-V1 | `save` | repositório com ervas | `id = max(ids) + 1` atribuído |
| Válida | EC-REPO-MANY-V1 | `save_many` | lista com N ervas | ids sequenciais atribuídos; todas persistidas |
| Válida (limite) | EC-REPO-MANY-V2 | `save_many` | lista vazia | repositório inalterado |

### Particionamento de Equivalência — PlanService

#### `list_plans` e `get_plan`

| Classe | ID | Condição | Resultado |
|---|---|---|---|
| Válida | EC-PSVC-LIST-V1 | repositório com planos | lista completa devolvida |
| Válida (limite) | EC-PSVC-LIST-V2 | repositório vazio | lista vazia devolvida |
| Válida | EC-PSVC-GET-V1 | `plan_id` existente | plano correspondente devolvido |
| Inválida | EC-PSVC-GET-I1 | `plan_id` inexistente | `PlanNotFound` lançado |

#### `create_plan`

| Classe | ID | Condição | Resultado |
|---|---|---|---|
| Válida | EC-PSVC-CREATE-V1 | dados válidos, tipo `regular` | plano validado, guardado e devolvido |
| Inválida | EC-PSVC-CREATE-I1 | tipo de plano inválido | `PlanValidationError` propagada |
| Inválida | EC-PSVC-CREATE-I1 | `temp_min` abaixo do mínimo | `PlanValidationError` propagada |
| Válida | EC-PSVC-CREATE-V2 | plano `pontual` com `authorized_by` | aceite e guardado |
| Inválida | EC-PSVC-CREATE-I2 | plano `pontual` sem `authorized_by` | `UnauthorizedPontualPlan` lançado |

### Particionamento de Equivalência — PlanJsonRepository

| Classe | ID | Método | Condição | Resultado |
|---|---|---|---|---|
| Válida (limite) | EC-PREPO-FILE-I1 | `list_all` | ficheiro não existe | lista vazia, sem erro |
| Inválida | EC-PREPO-FILE-I2 | `list_all` | ficheiro existe mas vazio | lista vazia |
| Válida | EC-PREPO-FILE-V1 | `list_all` | ficheiro com dados | lista com todos os planos |
| Válida | EC-PREPO-FIND-V1 | `find_by_id` | id existente | dicionário do plano devolvido |
| Inválida | EC-PREPO-FIND-I1 | `find_by_id` | id inexistente | `None` |
| Válida (limite) | EC-PREPO-SAVE-V2 | `save` | repositório vazio | plano recebe `id=1` |
| Válida | EC-PREPO-SAVE-V1 | `save` | repositório com dados | `id = max(ids) + 1` atribuído e persistido |

### MC/DC — HerbService.import_from_csv

Decisão em `import_from_csv`:

```python
validas = [h for h in parsed.herbs if h["status"] == "valid"]
if validas:
    self._repository.save_many(validas)
```

Condições atómicas:
- **C1**: existem linhas com `status == "valid"` no CSV

| Caso | C1 | Resultado | Teste |
|---|---|---|---|
| CSV com válidas | True | `save_many` chamado | TU-HERB-SVC-10 |
| CSV sem válidas | False | `save_many` não chamado | TU-HERB-SVC-11 |

C1 é a única condição — MC/DC satisfeita com os dois casos (True e False, cada um determinante).

### MC/DC — PlanService.create_plan (autorização pontual)

Decisão em `create_plan` / `validate_plan`:

```python
if plan_type == "pontual" and authorized_by is None:
    raise UnauthorizedPontualPlan(...)
```

Condições atómicas:
- **C1**: `type == "pontual"`
- **C2**: `authorized_by is None`

| Caso | C1 | C2 | Resultado | Teste |
|---|---|---|---|---|
| Regular sem auth | False | True | aceite | TU-PLAN-SVC-11 |
| Pontual sem auth | True | True | `UnauthorizedPontualPlan` | TU-PLAN-SVC-09 |
| Pontual com auth | True | False | aceite | TU-PLAN-SVC-08 |
| Regular com auth | False | False | aceite | TU-PLAN-SVC-10 |

**Demonstração MC/DC:**
- TU-PLAN-SVC-11 vs TU-PLAN-SVC-09: C1 varia (F→T), C2=True → resultado muda (aceite→rejeitado) — C1 afeta isoladamente ✓
- TU-PLAN-SVC-09 vs TU-PLAN-SVC-08: C2 varia (T→F), C1=True → resultado muda (rejeitado→aceite) — C2 afeta isoladamente ✓
