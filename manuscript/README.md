# Werner's conjecture in OEIS A208509, Formula, revision 28

## Statement and established antecedents

For `u[1]=v[1]=1`, `u[n+1]=u[n]+x*v[n]` and `v[n+1]=u[n]+v[n]+1`, the note proves, for every `n>=1` and `k>=0`,

```text
[x^k]v[n] = binomial(n-1,2k+1) + binomial(n,2k+1),
[x^k]u[n] = binomial(n-1,2k) + binomial(n,2k) - 1(k=0).
```

The title and abstract credit Knuth's exact coefficient families (1993, pp. 285–286). The note gives the index correspondence and parity decomposition, relates the formulas to André-Jeannin (1994) and Barry (2013), and credits later occurrences and the established column interpretations. It includes Blanco Gómez's 2026 proof of Chu's square-covering conjecture as a reproof, not a new resolution.

The correct row sums are A003945, not A003948. The fifth nonzero companion column is A053347; A054334 is the sixth, an arrangement also recorded in A208510. The A111125 column identification is with the second family after a shear, not the constant-column first family. For the A090131 associated sequence, the omitted value is `b[18]=-512`; its continuous polar angle is `atan(2)-m*pi/4`.

Further corollaries cover all column generating functions, partial sums, finite-difference recurrences, reflection and divisibility identities, terminating sums, subset and queens counts, Chebyshev coefficients, order-polytope counts, Morgan–Voyce/Lucas/Fibonacci identities, and arbitrary coupling and initial values over any commutative ring. Each has a complete written proof. The coverage table specifies the remaining source assertions outside these conclusions.

## Build

All references are embedded in `note.tex`. Build with Tectonic 0.17.0:

```sh
tectonic note.tex
```

Alternatively, run `pdflatex note.tex` twice. No external bibliography is needed. A source using an external `.bib` file can use the usual pdflatex/bibtex sequence.

## Exact finite checks

Use Python 3.10 or later and its standard library:

```sh
python3 verify.py --output verification.json
```

The checker constructs the two polynomial sequences from their recurrence independently of the binomial formulas. It compares all coefficients through `n=250`, including zero tails, and checks the source prefixes, sums, degrees, prior-array identifications, and additional corollaries. Subset selections, queen placements and bounded order-preserving assignments are enumerated directly. All arithmetic is integral or exact rational. `verification.json` lists every finite range and count; the universal claims have the written proofs in the note.

The pinned [Lean coefficient file](https://github.com/the-omega-institute/trureturing/blob/6ffa76e4424ce4c0d1048e56afb0724762ed8285/D5/S1/Recurrence/Invariants/AffinePolynomialPairBinomialCoefficients.lean) defines stage zero as source index one. Its declaration `werner_a208509` states the second-family identity for all `n>=1`, `k>=0`. The companion identity is a local simultaneous invariant, not a separate exported theorem. The other conclusions have the written proofs specified in the PDF and finite checks with the stated bounds.

## Files and license

- `note.tex`, `note.pdf`: the complete argument and typeset note.
- `metadata.json`: revision 2, ordered creators, license and source locator.
- `verify.py`, `verification.json`: the exact finite checker and its expected output.
- `reference-data.json`, `references.json`: source prefixes, locators and scientific references.
- `MANIFEST.sha256`: member hashes in the source archive.

Haobo Ma (ChronoAI Pte Ltd, Singapore), then Wenlin Zhang (National University of Singapore; ChronoAI Pte Ltd, Singapore). CC BY 4.0 (`cc-by-4.0`).

Posing sources: [A208509, revision 28](https://oeis.org/history/view?seq=A208509&v=28) and [A208508, revision 10](https://oeis.org/history/view?seq=A208508&v=10). The bibliography and `references.json` give the public scientific sources.
