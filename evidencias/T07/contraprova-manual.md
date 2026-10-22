# Contraprova matricial fechada T07

Expectativas derivadas antes do produto em `tests/test_grafo.py`, recibo RED `red01`.
As contas abaixo não usam funções produtoras para gerar o lado esperado.

## Associação múltipla sem multiplicação

Ocorrência a associa x,y,z; ocorrência b associa somente x.

```
B = [1/3 1/3 1/3]      W = [1/3 1/3]      A = [0 1]
    [ 1   0   0 ]          [1/3  1 ]          [1 0]
```

A soma de cada linha elegível de B é 1; repetir a linha documental a→x não muda B.
Se a posição H1 contém C=2,D=4 e alcança duas ocorrências, Q=(1/2,1/2), portanto
as massas são C_alocada=(1,1), D_alocada=(2,2), preservando as somas 2 e 4.
Três BNCC da mesma ocorrência não criam mais observações nem oportunidades.

## Ausência, zero e nó isolado

A primeira linha de A é (0,1/4,3/4,0); P=(1/5,0,ausente,9/10).
Seu numerador é (1/4)×0=0 e a massa observada é 1/4; propagado=0, com uma fonte.
Os nós b e c recebem 1/5 de a. O nó d, com linha nula, fica ausente; seu observado
9/10 permanece intacto. Um aluno com máscara toda falsa permanece todo ausente.

## Dois passos, máscara original e autorretorno

```
A = [0  1  0]          A² = [1/2 0 1/2]
    [1/2 0 1/2]            [ 0  1  0 ]
    [0  1  0]              [1/2 0 1/2]
```

P=(1,ausente,0); M=(1,0,1). Em dois passos o numerador é (1/2,0,1/2), massa=(1,0,1),
resultado=(1/2,ausente,1/2). Massa de retorno=(1/2,0,1/2). Removendo retorno, a massa
é (1/2,0,1/2), numerador=(0,0,1/2), resultado=(0,ausente,1). O nó b continua sem
observação original; a estimativa de um passo 1/2 não é promovida a observação.

Para apenas dois nós ligados, A²=I. P=(3/10,8/10) é repetido em dois passos; toda a
sensibilidade sem retorno fica ausente. É autorretorno, sem confirmação independente.

## Grupos sobrepostos e denominadores

Três observações sintéticas: s1=1/1, s2=0/3, s3=1/2.
g1={s1,s2}: 1/4. g2={s2,s3}: 1/5. Escola deduplicada: 2/6=1/3, N=3.
Somar grupos produziria denominador 9 (errado); média das três taxas seria 1/2
(outra pergunta). O teste usa 2/6 literal. Agregado escolar como entrada individual é recusado.

## Conferência real separada

`contraprova.py` reconstruiu os grafos diretamente dos vínculos autenticados T04 e
todos os valores da evidência original T05, com Fraction e laços. Não importa airam
nem numpy. As 129.997 comparações abrangem B/W/A, C/D/P, alocação, um/dois passos,
retorno, ausência e visões. Matemática do 1º ano foi conferida como inteiramente sem
vizinhos. Os recibos preservam fontes, versões, hashes, horário e saída reais.

Isto demonstra consistência computacional local; não valida domínio BNCC ou efeitos
pedagógicos. Identidades e células individuais não aparecem nesta contraprova pública.
