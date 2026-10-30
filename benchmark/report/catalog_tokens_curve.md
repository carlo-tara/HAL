# Curva token/richiesta vs dimensione catalogo skill — catalog-curve-20261030T121220

- Proxy tokenizer: Laya `usage.input_tokens` (System 2 del gateway è mock
  senza backend OrcaRouter registrato); due domande per punto.
- Catalogo: 39 skill; stime statiche integrali vs compatte:
  full≈2341 token vs compatte≈449 token (-80.8%).

| skill dichiarate | input token medi (misurati) | chars prompt |
| ---- | ---- | ---- |
| 0 | 140 | 128 |
| 1 | 140 | 124 |
| 5 | 229 | 392 |
| 10 | 374 | 857 |
| 20 | 505 | 1271 |
| 39 | 732 | 1939 |

Lettura: la curva è approssimativamente lineare nella dimensione del catalogo;
la riga compatta (nome+keyword) mantiene il costo di dichiarazione sotto il
budget del tool-search System 1 (voci correlate: Cache L1 a due strati, N21).
