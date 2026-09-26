# HEKATE

Status: canonical model note

This directory records the HEKATE primitive in the Root0 / OaSIs grammar.

## Primitive

```text
HEP :: TRANSMUTE :: EXCHANGE
```

### Constant substrate

```text
H = Hydrogen
E = Electrum
P = Potassium
```

### Operators

```text
T = Transmute
E = Exchange
```

So the five-slot primitive is:

```text
[ H ][ E ][ P ][ T ][ E ]
  \____3____/   \__2__/

3 constants :: 2 operators
```

## Semantic rule

```text
STATE
{H,E,P}
   ↓
TRANSMUTE
   ↓
EXCHANGE
   ↓
NEW STATE
```

This is a Logica / Somatic symbolic primitive. It is not, by itself, a conventional chemistry or nuclear reaction equation.

A physical interpretation requires an explicit Mathea mapping with specific isotopes, reaction pathways, conservation laws, predicted products, and measured results.

## Distilled axiom

```text
hold three → transmute → exchange
```
