import argparse
import hashlib
import json
from math import comb
from math import factorial
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path


def choose(upper, lower):
    return comb(upper, lower) if 0 <= lower <= upper else 0


def add(*polynomials):
    width = max(map(len, polynomials))
    result = [sum(poly[index] if index < len(poly) else 0 for poly in polynomials)
              for index in range(width)]
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def scale(polynomial, scalar):
    return [value * scalar for value in polynomial]


def multiply(first, second):
    result = [0] * (len(first) + len(second) - 1)
    for first_degree, first_value in enumerate(first):
        for second_degree, second_value in enumerate(second):
            result[first_degree + second_degree] += first_value * second_value
    return add(result)


def coefficient(polynomial, degree):
    return polynomial[degree] if 0 <= degree < len(polynomial) else 0


def column_value(dimension, index):
    return choose(index + dimension - 1, dimension - 1) + choose(index + dimension - 2, dimension - 1)


def evaluate_polynomial(polynomial, argument):
    result = [0]
    for value in reversed(polynomial):
        result = add(multiply(result, argument), [value])
    return result


def sibling_checks(rows):
    counts = {}
    accumulated = [2 * index + 1 for index in range(61)]
    family_count = 0
    recurrence_count = 0
    terminating_count = 0
    divisibility_count = 0
    for dimension in range(2, 13):
        for index, value in enumerate(accumulated):
            assert value == column_value(dimension, index)
            numerator = 2 * index + dimension - 1
            reflected = -index - dimension + 1
            reflected_numerator = 2 * reflected + dimension - 1
            for factor in range(1, dimension - 1):
                numerator *= index + factor
                reflected_numerator *= reflected + factor
            assert Fraction(numerator, factorial(dimension - 1)) == value
            assert Fraction(reflected_numerator, factorial(dimension - 1)) == (-1) ** (dimension - 1) * value
            family_count += 1
            if index >= dimension:
                assert value == sum((-1) ** (offset + 1) * choose(dimension, offset) * accumulated[index - offset]
                                    for offset in range(1, dimension + 1))
                recurrence_count += 1
        for length in range(1, 31):
            ratio = Fraction(1)
            total = Fraction(accumulated[0])
            for index in range(1, length + 1):
                ratio *= Fraction(-(length - index + 1), length + dimension + index - 1)
                total += ratio * accumulated[index]
            assert total == 0
            terminating_count += 1
        for prime in [7, 13, 17]:
            if prime <= dimension - 1:
                continue
            for exponent in range(1, 4):
                modulus = prime ** exponent
                roots = [(-factor) % modulus for factor in range(1, dimension - 1)]
                roots.append((-(dimension - 1) * pow(2, -1, modulus)) % modulus)
                for index in roots:
                    assert column_value(dimension, index) % modulus == 0
                    divisibility_count += 1
        running = 0
        following = []
        for value in accumulated:
            running += value
            following.append(running)
        accumulated = following
    counts['column_family'] = {'d_min': 2, 'd_max': 12, 'm_min': 0, 'm_max': 60,
                               'formula_and_reflection_cases': family_count,
                               'recurrence_cases': recurrence_count}
    counts['terminating_identities'] = {'d_min': 2, 'd_max': 12, 'n_min': 1, 'n_max': 30,
                                        'exact_rational_cases': terminating_count}
    counts['column_divisibility'] = {'primes': [7, 13, 17], 'exponents': [1, 2, 3],
                                     'condition': 'p>d-1', 'cases': divisibility_count}
    subset_count = 0
    for dimension in range(4, 9):
        for index in range(5):
            universe = range(index + dimension)
            first_block = {0, 1}
            second_block = set(range(2, index + dimension - 1))
            count = sum(bool(set(subset) & first_block) and bool(set(subset) & second_block)
                        for subset in combinations(universe, dimension))
            assert count == column_value(dimension, index)
            subset_count += 1
    counts['subset_interpretation'] = {'d_min': 4, 'd_max': 8, 'm_min': 0, 'm_max': 4,
                                        'exhaustive_cases': subset_count}
    queen_count = 0
    for queen_number in range(2, 5):
        for index in range(4):
            side = queen_number + index
            count = 0
            for row_set in combinations(range(side), queen_number):
                for column_set in combinations(range(side), queen_number):
                    for ordered_columns in permutations(column_set):
                        if all(abs(row_set[first] - row_set[second]) ==
                               abs(ordered_columns[first] - ordered_columns[second])
                               for first in range(queen_number) for second in range(first)):
                            count += 1
            assert count == 2 * column_value(queen_number + 2, index)
            queen_count += 1
    counts['queens_interpretation'] = {'queens_min': 2, 'queens_max': 4, 'm_min': 0, 'm_max': 3,
                                        'exhaustive_cases': queen_count}
    order_count = 0
    for dimension in range(3, 7):
        for index in range(4):
            chain_length = dimension - 3
            count = 0
            for assignment in product(range(index + 1), repeat=dimension - 1):
                chain = assignment[:chain_length]
                if any(chain[position] > chain[position + 1] for position in range(chain_length - 1)):
                    continue
                if chain and max(chain) > min(assignment[-2:]):
                    continue
                count += 1
            assert count == column_value(dimension, index)
            order_count += 1
    counts['order_polytope_interpretation'] = {'d_min': 3, 'd_max': 6, 'm_min': 0, 'm_max': 3,
                                               'exhaustive_cases': order_count}
    chebyshev = [[1], [0, 1]]
    for degree in range(2, 40):
        chebyshev.append(add([0] + scale(chebyshev[-1], 2), scale(chebyshev[-2], -1)))
    chebyshev_count = 0
    for power in range(1, 12):
        for index in range(13):
            assert coefficient(chebyshev[power + 2 * index], power) == (
                (-1) ** index * 2 ** (power - 1) * column_value(power + 1, index))
            chebyshev_count += 1
    counts['chebyshev_interpretation'] = {'r_min': 1, 'r_max': 11, 'm_min': 0, 'm_max': 12,
                                          'coefficient_cases': chebyshev_count}
    pascal = [2, 1]
    for stage in range(1, 81):
        first, second = rows[stage]
        combined = [0] * max(2 * len(first) - 1, 2 * len(second))
        for degree, value in enumerate(first):
            combined[2 * degree] += value
        combined[0] += 1
        for degree, value in enumerate(second):
            combined[2 * degree + 1] += value
        assert add(combined) == pascal
        pascal = multiply(pascal, [1, 1])
    morgan = [[1], [3, 1]]
    for stage in range(2, 71):
        morgan.append(add(multiply(morgan[-1], [2, 1]), scale(morgan[-2], -1)))
    morgan_count = 0
    for stage, polynomial in enumerate(morgan):
        for degree in range(stage + 6):
            assert coefficient(polynomial, degree) == coefficient(rows[stage + degree + 1][1], degree)
            morgan_count += 1
    counts['prior_array_identifications'] = {'pascal_polynomial_cases': 80,
                                             'morgan_voyce_m_min': 0, 'morgan_voyce_m_max': 70,
                                             'morgan_voyce_coefficient_cases': morgan_count}
    fibonacci = [0, 1]
    for index in range(1, 400):
        fibonacci.append(fibonacci[-1] + fibonacci[-2])
    lucas = [2, 1]
    for index in range(1, 150):
        lucas.append(lucas[-1] + lucas[-2])
    for index, polynomial in enumerate(morgan):
        assert sum(polynomial) == lucas[2 * index + 1]
        assert sum(value * (-1) ** degree for degree, value in enumerate(polynomial)) == [1, 2, 1, -1, -2, -1][index % 6]
    laurent_count = 0
    for index in range(21):
        for argument in range(2, 7):
            argument = Fraction(argument)
            difference = argument - 1 / argument
            assert argument ** (2 * index + 1) - argument ** (-(2 * index + 1)) == difference * sum(
                Fraction(value) * difference ** (2 * degree)
                for degree, value in enumerate(morgan[index]))
            laurent_count += 1
    fibonacci_count = 0
    for index in range(16):
        for source_index in range(13):
            expected = sum(value * (-1) ** ((index + degree) * source_index) *
                           5 ** degree * fibonacci[source_index] ** (2 * degree + 1)
                           for degree, value in enumerate(morgan[index]))
            assert fibonacci[(2 * index + 1) * source_index] == expected
            fibonacci_count += 1
    counts['morgan_voyce_identities'] = {'lucas_and_alternating_cases': 142,
                                          'laurent_exact_rational_cases': laurent_count,
                                          'fibonacci_multiple_cases': fibonacci_count,
                                          'fibonacci_m_min': 0, 'fibonacci_m_max': 15,
                                          'fibonacci_n_min': 0, 'fibonacci_n_max': 12}
    real, imaginary = 1, 2
    complex_rows = []
    for index in range(250):
        complex_rows.append((real, imaginary))
        assert real == sum(value * (-1) ** degree for degree, value in enumerate(rows[index + 1][1]))
        if index >= 4:
            assert (real, imaginary) == tuple(-4 * value for value in complex_rows[index - 4])
        real, imaginary = real + imaginary, imaginary - real
    assert complex_rows[18][1] == -512
    assert complex_rows[19][1] == -1536
    counts['alternating_complex_pair'] = {'m_min': 0, 'm_max': 249, 'pair_cases': 250,
                                           'corrected_b_18': -512, 'b_19': -1536}
    for size in range(1, 101):
        first_set = range(size)
        second_set = range(0, size * size, size)
        assert {first + second for first in first_set for second in second_set} == set(range(size * size))
    counts['chu_square_covering'] = {'n_min': 1, 'n_max': 100, 'construction_cases': 100,
                                     'minimality': 'cardinality proof in note.tex'}
    initial_first, initial_second, affine = [3, -2, 5], [-1, 4], [2, 1]
    coupling = [-2, 3, 1]
    first, second = initial_first, initial_second
    for exponent in range(31):
        even = [choose(exponent, 2 * degree) for degree in range(exponent // 2 + 1)]
        odd = [choose(exponent, 2 * degree + 1) for degree in range((exponent + 1) // 2)] or [0]
        even = evaluate_polynomial(even, coupling)
        odd = evaluate_polynomial(odd, coupling)
        assert first == add(multiply(even, add(initial_first, affine)),
                            multiply(coupling, multiply(odd, initial_second)), scale(affine, -1))
        assert second == add(multiply(odd, add(initial_first, affine)), multiply(even, initial_second))
        first, second = add(first, multiply(coupling, second)), add(first, second, affine)
    counts['arbitrary_polynomial_coupling'] = {'t': coupling, 'n_min': 1, 'n_max': 31,
                                                'polynomial_cases': 62}
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('verification.json'))
    args = parser.parse_args()
    directory = Path(__file__).resolve().parent
    data = json.loads((directory / 'reference-data.json').read_text())
    first, second = [1], [1]
    rows = {}
    coefficient_cases = 0
    column_cases = 0
    for stage in range(1, 251):
        rows[stage] = (first, second)
        for degree in range(stage + 9):
            expected_first = (choose(stage - 1, 2 * degree) + choose(stage, 2 * degree)
                              - int(degree == 0))
            expected_second = choose(stage - 1, 2 * degree + 1) + choose(stage, 2 * degree + 1)
            assert coefficient(first, degree) == expected_first, ('u', stage, degree)
            assert coefficient(second, degree) == expected_second, ('v', stage, degree)
            coefficient_cases += 2
        assert len(first) - 1 == stage // 2
        assert len(second) - 1 == (stage - 1) // 2
        assert sum(first) == (1 if stage == 1 else 3 * 2 ** (stage - 2) - 1)
        assert sum(second) == (1 if stage == 1 else 3 * 2 ** (stage - 2))
        for degree in range(9):
            shifted_second = stage - 1 - 2 * degree
            expected_second = (choose(shifted_second + 2 * degree + 1, 2 * degree + 1)
                               + choose(shifted_second + 2 * degree, 2 * degree + 1)
                               if shifted_second >= 0 else 0)
            assert coefficient(second, degree) == expected_second
            if degree == 0:
                assert coefficient(first, degree) == 1
            else:
                shifted_first = stage - 2 * degree
                expected_first = (choose(shifted_first + 2 * degree, 2 * degree)
                                  + choose(shifted_first + 2 * degree - 1, 2 * degree)
                                  if shifted_first >= 0 else 0)
                assert coefficient(first, degree) == expected_first
            column_cases += 2
        if stage >= 3:
            for degree in range(stage + 2):
                assert coefficient(second, degree) == (
                    2 * coefficient(rows[stage - 1][1], degree)
                    + coefficient(rows[stage - 2][1], degree - 1)
                    - coefficient(rows[stage - 2][1], degree))
        first, second = add(first, [0] + second), add(first, second, [1])
    alternating = [1, 3]
    for stage in range(3, 251):
        alternating.append(2 * alternating[-1] - 2 * alternating[-2])
    for stage in range(1, 251):
        assert sum(value * (-1) ** degree for degree, value in enumerate(rows[stage][1])) == alternating[stage - 1]
    prefix_cases = 0
    for entry in data['column_prefixes']:
        stage = entry['first_source_n']
        family_index = 0 if entry['family'] == 'u' else 1
        for offset, value in enumerate(entry['values']):
            assert coefficient(rows[stage + offset][family_index], entry['degree']) == value, entry['id']
            prefix_cases += 1
    for family, sequence in [('u', 'A208508'), ('v', 'A208509')]:
        flattened = []
        for stage in range(1, 251):
            flattened.extend(rows[stage][0 if family == 'u' else 1])
        expected = data['triangle_prefixes'][sequence]
        assert flattened[:len(expected)] == expected
        prefix_cases += len(expected)
    for stage, value in enumerate(data['sum_prefixes']['A083329'], 1):
        assert sum(rows[stage][0]) == value
        prefix_cases += 1
    for stage, value in enumerate(data['sum_prefixes']['A003945'], 1):
        assert sum(rows[stage][1]) == value
        prefix_cases += 1
    for stage, value in enumerate(data['sum_prefixes']['A090131'], 1):
        assert alternating[stage - 1] == value
        prefix_cases += 1
    assert sum(rows[2][1]) == 3
    assert data['sum_prefixes']['A003948'][:5] == [1, 6, 30, 150, 750]
    assert coefficient(rows[9][0], 4) == 10
    for offset, value in enumerate(data['column_correction']['fifth_column_nonzero_prefix']):
        assert coefficient(rows[8 + offset][0], 4) == value
        prefix_cases += 1
    assert data['column_correction']['A054334_prefix'][:5] == [1, 12, 77, 352, 1287]
    for offset, value in enumerate(data['column_correction']['A054334_prefix']):
        assert coefficient(rows[10 + offset][0], 5) == value
        prefix_cases += 1
    initial_first, initial_second, affine = [3, -2, 5], [-1, 4], [2, 1]
    first, second = initial_first, initial_second
    general_cases = 0
    for exponent in range(60):
        even = [choose(exponent, 2 * degree) for degree in range(exponent // 2 + 1)]
        odd = [choose(exponent, 2 * degree + 1) for degree in range((exponent + 1) // 2)] or [0]
        expected_first = add(multiply(even, add(initial_first, affine)),
                             [0] + multiply(odd, initial_second), scale(affine, -1))
        expected_second = add(multiply(odd, add(initial_first, affine)), multiply(even, initial_second))
        assert first == expected_first
        assert second == expected_second
        general_cases += 2
        first, second = add(first, [0] + second), add(first, second, affine)
    siblings = sibling_checks(rows)
    output = {
        'status': 'pass',
        'arithmetic': 'exact Python integers',
        'coefficient_scope': {'n_min': 1, 'n_max': 250, 'k_min': 0, 'k_max_per_n': 'n+8',
                              'comparisons': coefficient_cases, 'families': ['u', 'v']},
        'degree_comparisons': 500,
        'column_series_scope': {'n_min': 1, 'n_max': 250, 'k_min': 0, 'k_max': 8,
                                'comparisons': column_cases},
        'row_sum_comparisons': 500,
        'alternating_sum_comparisons': 250,
        'bivariate_series_recurrence_n': [3, 250],
        'oeis_prefix_comparisons': prefix_cases,
        'general_initial_value_scope': {'n_min': 1, 'n_max': 60,
                                        'p': initial_first, 'q': initial_second, 'c': affine,
                                        'polynomial_comparisons': general_cases},
        'cross_reference_counterexample': {'source': 'A208509, Crossrefs: A003948',
                                          'n': 2, 'v_n_at_1': 3, 'A003948_at_1': 6,
                                          'corrected_formula': 'v_1(1)=1; v_n(1)=3*2^(n-2) for n>=2'},
        'companion_column_counterexample': {'source': 'A208508, Comments: col 5 A054334',
                                            'n': 9, 'k': 4, 'u_coefficient': 10,
                                            'A054334_second_term': 12,
                                            'corrected_identification': 'A054334 is column 6 (one-based), k=5, after initial zeros'},
        'lean_declaration_scope': 'werner_a208509: all n>=1 and k>=0 for the second-family coefficients',
        'universal_proof': 'note.tex: coefficient theorem, corollaries and general initial-value proposition',
        'sibling_checks': siblings,
        'inputs_sha256': {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                          for name in ['verify.py', 'reference-data.json']}
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps(output, sort_keys=True))


if __name__ == '__main__':
    main()
