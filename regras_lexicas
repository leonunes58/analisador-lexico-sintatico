# Documentação das Regras Léxicas — Analisador do Elgol

## 1. Ferramenta utilizada

O analisador léxico foi implementado em **Python 3**, usando a biblioteca
**PLY (Python Lex-Yacc)**, módulo `ply.lex`. O PLY é uma implementação em
Python puro das ferramentas clássicas *lex/yacc*: cada tipo de token é
definido por uma regra (string ou função) associada a uma expressão
regular, e o PLY monta automaticamente o autômato de reconhecimento e a
função de tokenização.

### Instalação

```bash
pip install ply
```

(É um pacote único, sem dependências, disponível no PyPI.)

### Como executar

```bash
python3 analisador.py caminho/para/arquivo.elg
```

O script imprime: lista de tokens, tabela de símbolos e erros léxicos
encontrados.

---

## 2. Categorias de token reconhecidas

| Token | Descrição | Exemplo |
|---|---|---|
| `ID` | Identificador de variável | `Lixo`, `Resultado` |
| `FUNCID` | Nome de função | `$Soma` |
| `NUMBER` | Número inteiro | `34`, `200` |
| Palavras reservadas | Ver tabela abaixo | `inicio`, `se`, `EXP` |
| `ASSIGN` | `=` | |
| `PLUS` | `+` | |
| `MINUS` | `-` | |
| `DIV` | `/` | |
| `MULT` | `x` | |
| `DOT` | `.` (fim de comando) | |
| `LPAREN` / `RPAREN` | `(` `)` | |
| `COMMA` | `,` (separador de parâmetros) | |
| (descartado) | Comentário `* ...` até o fim da linha | |

### Palavras reservadas (case-sensitive)

```
elgio, DECIMAL, _Z_, _NEG_, EXP, RESTO,
enquanto, se, entao, senao, para,
inicio, fim,
maior, menor, igual, diferente, migual, MIgual
```

`migual` e `MIgual` são duas palavras reservadas **distintas** (a
linguagem é case-sensitive), cada uma vira um token diferente
(`MIGUAL` e `MIGUAL_CAP`).

---

## 3. Regras formais (expressões regulares)

### 3.1 Identificador (`ID`)

> Começa com **consoante maiúscula**, termina com **letra minúscula**,
> tem no mínimo **4 caracteres** e contém **apenas letras**.

```
[BCDFGHJKLMNPQRSTVWXYZ][A-Za-z]*[a-z]     (comprimento total >= 4)
```

| Entrada | Válido? | Motivo |
|---|---|---|
| `Teste` | ✅ | consoante maiúscula, termina minúscula, 5 letras |
| `PEsar` | ✅ | maiúsculas no meio são permitidas |
| `teste` | ❌ | não começa com maiúscula |
| `Teste39` | ❌ | contém dígitos |
| `Tes_Te` | ❌ | contém `_` |
| `Xyz`, `Bh`, `Lxt` | ❌ | menos de 4 caracteres |
| `LetrA` | ❌ | termina com maiúscula |
| `Ateras` | ❌ | começa com vogal |

### 3.2 Nome de função (`FUNCID`)

> `$` seguido de um identificador válido (mesma regra acima).

```
\$[BCDFGHJKLMNPQRSTVWXYZ][A-Za-z]*[a-z]   (parte após o $ com >= 4 chars)
```

`$Teste` é válido; `$teste`, `$Te34`, `$Te` não são.

### 3.3 Número inteiro (`NUMBER`)

> Começa com dígito de **1 a 9** seguido de dígitos quaisquer (sem zero
> à esquerda; o dígito `0` sozinho não existe na linguagem).

```
[1-9][0-9]*
```

`200` é válido; `034` e `0` são inválidos (o zero é representado pelo
operador reservado `_Z_`, e números negativos pelo operador `_NEG_`).

### 3.4 Comentário

```
\*[^\n]*
```

Do caractere `*` até o fim da linha; é descartado (não gera token).

### 3.5 Delimitador de comando

Cada comando termina com `.` (token `DOT`), não com `;`.

---

## 4. Estratégia de reconhecimento e tratamento de erro

Para conseguir relatar erros léxicos de forma legível (em vez de reportar
caractere a caractere), o analisador usa uma regra "guarda-chuva" que
captura qualquer sequência de letras/dígitos/`_` iniciada por letra ou
`_` (`[A-Za-z_][A-Za-z0-9_]*`) e uma regra equivalente para nomes de
função (prefixo `$`). Dentro da função de tratamento dessas regras:

1. Se o valor capturado é uma palavra reservada → gera o token
   correspondente.
2. Senão, se casa com a regra formal de identificador → gera `ID`
   (ou `FUNCID`).
3. Senão → é um **erro léxico**: a mensagem é registrada com o número da
   linha e o texto encontrado, e o token é descartado (a análise
   continua nas linhas seguintes).

Caracteres que não pertencem a nenhuma regra (ex.: `&`, `0` isolado)
também geram erro léxico e são simplesmente pulados.

---

## 5. Tabela de símbolos

A tabela de símbolos é construída durante a tokenização: para cada
`ID` e `FUNCID` reconhecido, é guardado o tipo e a lista de linhas em
que o nome aparece. Ela é impressa junto com a lista de tokens ao rodar
`analisador.py`.
