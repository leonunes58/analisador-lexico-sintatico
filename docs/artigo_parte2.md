# Texto para o artigo — Parte 2: Análise Sintática

> Seções para acrescentar ao artigo do TR4 (depois das seções da análise
> léxica). Ajuste a numeração das seções e figuras ao artigo de vocês.

---

## X. Análise Sintática

### X.1 Fundamentação

A análise sintática é a segunda fase de um compilador. Ela recebe a sequência
de tokens produzida pelo analisador léxico e verifica se essa sequência pode
ser gerada pela gramática da linguagem, que é uma **gramática livre de
contexto** (GLC). Enquanto o analisador léxico decide se cada palavra do
programa é válida (por exemplo, se `Contador` é um identificador bem formado),
o analisador sintático decide se as palavras estão **na ordem correta** (por
exemplo, se toda atribuição tem a forma `identificador = expressão.`).

O resultado da análise é uma **árvore sintática**, que representa a estrutura
hierárquica do programa e serve de entrada para as fases seguintes
(análise semântica e geração de código). Quando a sequência não pertence à
linguagem, o analisador deve relatar o erro com a sua localização e, de
preferência, continuar a análise para encontrar outros erros (Aho et al.,
2008).

Os analisadores sintáticos dividem-se em **descendentes** (*top-down*, como
os LL(1) e os descendentes recursivos), que constroem a árvore da raiz para
as folhas, e **ascendentes** (*bottom-up*, como os LR, SLR e LALR), que partem
dos tokens e aplicam reduções até chegar ao símbolo inicial. Os analisadores
ascendentes aceitam uma classe maior de gramáticas, incluindo gramáticas
recursivas à esquerda, o que permite escrever as expressões aritméticas de
forma natural.

### X.2 Ferramenta: `ply.yacc`

Mantendo a escolha do TR4, a análise sintática foi feita com o módulo
`ply.yacc` da biblioteca **PLY (Python Lex-Yacc)** (Beazley, 2001–2025),
que reproduz em Python a ferramenta clássica *yacc*. O PLY gera um analisador
**LALR(1)**: a partir das regras da gramática ele constrói automaticamente as
tabelas de ação (*shift*, *reduce*, aceitar, erro) e de desvio (*goto*) do
autômato de pilha.

Cada regra é escrita como uma função Python. A produção em notação BNF fica
na *docstring* da função e o corpo da função monta o nó correspondente da
árvore. Por exemplo, a regra da atribuição:

```python
def p_atribuicao(p):
    "atribuicao : ID ASSIGN expressao DOT"
    p[0] = Node("atribuicao", [Node("id", value=p[1]), p[3]])
```

Uma vantagem prática do PLY é que o analisador léxico e o sintático
compartilham a mesma lista de tokens: o parser importa a tupla `tokens` do
módulo léxico da Parte 1, que não precisou ser alterado. Além disso, o PLY
detecta e relata conflitos na gramática no momento em que as tabelas são
geradas, o que ajudou a validar as regras durante o desenvolvimento.

### X.3 Gramática do Elgol

A gramática implementada é apresentada no Quadro X (copiar a BNF do arquivo
`regras_sintaticas.md`). As principais decisões foram:

- **Estrutura do programa**: todo programa é um bloco `inicio ... fim` com
  uma lista (possivelmente vazia) de comandos.
- **Comandos simples** — atribuição (`Nome = expressão.`), declaração
  (`DECIMAL Nome.`) e chamada de função (`$Nome(args).`) — terminam com `.`,
  conforme a especificação da linguagem.
- **Comandos de bloco** — `se`/`senao`, `enquanto` e `para` — têm a condição
  entre parênteses, seguida de `entao`, e são fechados pela palavra `fim`,
  permitindo aninhamento.
- **Condições** são formadas por uma expressão, um dos seis operadores
  relacionais (`maior`, `menor`, `igual`, `diferente`, `migual`, `MIgual`) e
  outra expressão.
- **Expressões** combinam identificadores, números, `_Z_`, chamadas de função
  e os operadores `+`, `-`, `x`, `/`, `RESTO`, `EXP` e o unário `_NEG_`.

**Precedência.** Em vez de criar um não terminal para cada nível de
precedência (expressão, termo, fator), foi usada a tabela `precedence` do
PLY, que resolve os conflitos da gramática ambígua de expressões de forma
declarativa:

| Nível | Operadores | Associatividade |
|---|---|---|
| 1 (menor) | `+` `-` | esquerda |
| 2 | `x` `/` `RESTO` | esquerda |
| 3 | `_NEG_` | direita |
| 4 (maior) | `EXP` | direita |

Assim, `Base + Base x 2` é interpretado como `Base + (Base x 2)` e
`2 EXP 3 EXP 2` como `2 EXP (3 EXP 2)`, como na matemática. Com essas
declarações a gramática final não possui nenhum conflito *shift/reduce* ou
*reduce/reduce*, resultando em um autômato LALR de 87 estados.

### X.4 Tratamento de erros sintáticos

Quando o autômato encontra um token para o qual não há ação na tabela, o PLY
chama a função `p_error`. Nela o analisador registra:

1. a **linha** do token;
2. o **token encontrado** e seu valor;
3. quando a lista é pequena, os **tokens esperados** naquele ponto,
   obtidos da própria tabela de ações do estado em que ocorreu o erro.

Exemplo de saída para um `enquanto` sem `entao`:

```
linha 5: token inesperado identificador = 'Valor'; esperado: 'entao'
```

Para não parar no primeiro erro, foi usada a **recuperação em modo pânico**
do yacc com a produção `comando : error DOT`: ao encontrar um erro, o parser
descarta tokens até o próximo `.` (fim de comando) e continua a análise.
Dessa forma um mesmo arquivo pode relatar vários erros independentes. Se o
arquivo termina antes de fechar algum bloco, é emitido
`fim de arquivo inesperado (faltou 'fim'?)`.

### X.5 Árvore sintática

Para programas válidos, o analisador imprime a árvore sintática. Por
exemplo, para o trecho

```
se (Nota maior 6) entao
    Situacao = 1.
fim
```

é gerada a árvore:

```
se
├── condicao (maior)
│   ├── id (Nota)
│   └── numero (6)
└── entao
    └── atribuicao
        ├── id (Situacao)
        └── numero (1)
```

### X.6 Testes e resultados

Foram preparados 6 programas corretos e 12 incorretos (o exemplo léxico da
Parte 1 e 11 programas com um erro sintático típico cada: falta de `.`, falta
de `fim`, falta de `entao`, operador faltando, condição sem operador
relacional, atribuição a um número, parêntese não fechado, ausência de
`inicio`, `senao` sem `se`, vários erros no mesmo arquivo e mistura de erros
léxicos e sintáticos).

A verificação foi automatizada com o **pytest** em 46 casos de teste, que
conferem: (a) que todos os programas corretos são aceitos; (b) que cada
programa incorreto é rejeitado **exatamente nas linhas esperadas**; (c) o
formato da árvore gerada, comprovando a precedência e a associatividade dos
operadores; (d) os seis operadores relacionais e as chamadas de função com e
sem argumentos; e (e) a recuperação após erros. Todos os testes passaram.

| Conjunto | Arquivos | Resultado esperado | Resultado obtido |
|---|---|---|---|
| Corretos | 6 | aceitos | 6/6 aceitos |
| Incorretos | 12 | rejeitados | 12/12 rejeitados na linha esperada |
| Testes pytest | 46 | aprovados | 46/46 |

### X.7 Limitações

A análise sintática garante apenas a **forma** do programa. Verificações que
dependem de significado — como usar uma variável antes de atribuir um valor a
ela, ou chamar uma função com o número errado de argumentos — pertencem à
análise semântica e não foram tratadas nesta etapa. A tabela de símbolos
construída na Parte 1 já registra os identificadores e as linhas em que
aparecem, e pode ser usada como base para essa próxima fase.

---

## Referências (acrescentar às do artigo)

AHO, A. V.; LAM, M. S.; SETHI, R.; ULLMAN, J. D. **Compiladores: princípios,
técnicas e ferramentas**. 2. ed. São Paulo: Pearson Addison-Wesley, 2008.

BEAZLEY, D. M. **PLY (Python Lex-Yacc)**. Disponível em:
<https://www.dabeaz.com/ply/>. Acesso em: nov. 2026.
