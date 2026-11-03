# Regras Sintáticas — Analisador do Elgol

## 1. Ferramenta

A análise sintática usa o módulo **`ply.yacc`** do PLY (o mesmo pacote da
análise léxica). O PLY gera um analisador **LALR(1)** ascendente
(*shift-reduce*): cada regra da gramática é escrita como uma função Python
cuja *docstring* contém a produção em BNF, e o corpo da função monta o nó
correspondente da árvore sintática.

Os tokens consumidos pelo parser são exatamente os produzidos pelo
analisador léxico da Parte 1 (`elgol/lexer/lexer.py`).

A gramática abaixo **não tem conflitos** shift/reduce nem reduce/reduce
(87 estados LALR).

---

## 2. Gramática (BNF)

Terminais em MAIÚSCULAS (nome do token) ou entre aspas (lexema).

```
programa          ::= 'inicio' comandos 'fim'

comandos          ::= comandos comando
                    | ε

comando           ::= atribuicao
                    | declaracao
                    | condicional
                    | repeticao_enquanto
                    | repeticao_para
                    | chamada_comando
                    | error '.'                      (recuperação de erro)

atribuicao        ::= ID '=' expressao '.'

declaracao        ::= 'DECIMAL' ID '.'

condicional       ::= 'se' '(' condicao ')' 'entao' comandos 'fim'
                    | 'se' '(' condicao ')' 'entao' comandos 'senao' comandos 'fim'

repeticao_enquanto ::= 'enquanto' '(' condicao ')' 'entao' comandos 'fim'

repeticao_para    ::= 'para' '(' condicao ')' 'entao' comandos 'fim'

chamada_comando   ::= chamada '.'

chamada           ::= FUNCID '(' argumentos ')'

argumentos        ::= lista_argumentos
                    | ε

lista_argumentos  ::= expressao
                    | lista_argumentos ',' expressao

condicao          ::= expressao relacional expressao

relacional        ::= 'maior' | 'menor' | 'igual' | 'diferente'
                    | 'migual' | 'MIgual'

expressao         ::= expressao '+'     expressao
                    | expressao '-'     expressao
                    | expressao 'x'     expressao
                    | expressao '/'     expressao
                    | expressao 'RESTO' expressao
                    | expressao 'EXP'   expressao
                    | '_NEG_' expressao
                    | '(' expressao ')'
                    | '(' condicao ')'
                    | ID
                    | NUMBER
                    | '_Z_'
                    | chamada
```

### 2.1 Precedência e associatividade (da menor para a maior)

| Nível | Operadores | Associatividade |
|---|---|---|
| 1 | `+` `-` | esquerda |
| 2 | `x` `/` `RESTO` | esquerda |
| 3 | `_NEG_` (unário) | direita |
| 4 | `EXP` | direita |

Exemplos:

| Expressão | Interpretação |
|---|---|
| `Base + Base x 2` | `Base + (Base x 2)` |
| `Base - 2 - 1` | `(Base - 2) - 1` |
| `2 EXP 3 EXP 2` | `2 EXP (3 EXP 2)` |
| `_NEG_ 2 EXP 2` | `_NEG_ (2 EXP 2)` |

---

## 3. Regras em linguagem natural

1. Todo programa começa com `inicio` e termina com `fim`.
2. Todo comando simples (atribuição, declaração, chamada de função) termina com `.`.
3. Estruturas de bloco (`se`, `enquanto`, `para`) **não** terminam com `.`:
   são fechadas pelo seu próprio `fim`, e podem ser aninhadas.
4. A condição de `se`, `enquanto` e `para` fica **entre parênteses** e é
   formada por `expressão operador-relacional expressão`, seguida de `entao`.
5. `senao` só pode aparecer dentro de um `se`, antes do `fim` dele.
6. O lado esquerdo de `=` é sempre um identificador.
7. Funções são chamadas com `$Nome(arg1, arg2, ...)`, com zero ou mais
   argumentos separados por `,`; a chamada pode ser um comando ou fazer parte
   de uma expressão.
8. `_Z_` representa o zero e `_NEG_` é o operador unário de negação.
9. Uma comparação entre parênteses pode ser usada como valor numa atribuição:
   `Checagem = (Numero MIgual Betao).`

---

## 4. Tratamento de erros sintáticos

- Cada erro é registrado com a **linha**, o **token inesperado** e, quando
  a lista é curta, os **tokens que eram esperados** naquele ponto (lidos da
  tabela de ações LALR do estado em que o erro ocorreu). Exemplo:

  ```
  linha 5: token inesperado identificador = 'Valor'; esperado: 'entao'
  ```

- **Recuperação em modo pânico**: a produção `comando ::= error '.'` faz o
  parser descartar tokens até o próximo `.` e continuar a análise. Assim um
  único arquivo pode relatar vários erros (ver
  `tests/exemplos/incorretos/10_varios_erros.elgol`).
- Se o arquivo termina antes de fechar todos os blocos, o erro é
  `fim de arquivo inesperado (faltou 'fim'?)`.
- Tokens descartados pelo analisador léxico (por serem inválidos) não chegam
  ao parser; por isso um erro léxico pode gerar também um erro sintático na
  mesma linha.

---

## 5. Pontos a confirmar com a especificação do professor

Estas decisões foram tomadas por falta de regra explícita e são fáceis de
ajustar no arquivo `elgol/syntax/parser.py`:

- **`elgio`**: palavra reservada reconhecida pelo léxico, mas ainda sem
  regra sintática (o PLY avisa "token ELGIO defined, but not used").
- **`DECIMAL`**: tratado como declaração de variável (`DECIMAL Nome.`).
- **`para`**: usa a mesma forma do `enquanto` (`para (condição) entao ... fim`).
- **Declaração de funções**: só há chamada (`$Nome(...)`); não existe regra
  para definir o corpo de uma função.
