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

