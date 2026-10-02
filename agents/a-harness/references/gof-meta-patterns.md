# GoF / HFDP → a-harness (meta-patterns)

Mapping ridotto da *Head First Design Patterns* a principi già nel harness. **Niente** competency GoF nuove.

| Meta-pattern | Dove in AF | Note |
|--------------|------------|------|
| Template Method / Hollywood | `/cycle` skeleton + Make/hooks | HFDP Fase 1 |
| Adapter | ACL (`anti-corruption-layer`) | HFDP Fase 2 |
| Facade | Platform API Make + Facade L1 | HFDP Fase 2 |
| State | Plan \| Act \| Stuck \| Ready | HFDP Fase 3 |
| Strategy | competenza di **fase** (tdd-*/steward…) | non polymorphism OO |

## Non implementare

- Factory / Abstract Factory / Singleton / Observer / Decorator / Command come competency
- MVC / layered OO tutorial in L1
- `competencies/{adapter,facade,strategy,template-method}/`

Pin fonti esterne: [graph-loop-source.md](graph-loop-source.md) § Non-adopt + L2 harness «fonti esterne → L1».
