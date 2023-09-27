import argparse
import itertools
import typing
from pdb import set_trace

import matplotlib.pyplot as plt
import numpy as np
import pretty_errors
from utils import frac_range


def _cal_irrep_trace(irreps: list, symprec: float = 1e-3) -> list:
    """calculate character from irreps, delete the real or imag part while value euqal to 0

    Args:
        irreps: irreducible representation
        symprec: system precise

    Returns: character table

    """
    character_tabel = []
    for irrep in irreps:
        tmp_character = []
        for tmp in irrep:

            if tmp.size == 1:
                if abs(tmp.imag) < symprec:
                    tmp = tmp.real
                if abs(tmp.real) < symprec:
                    tmp = complex(0, tmp.imag)
                    if tmp.imag == 0:
                        tmp = 0
                tmp_character.append(tmp)
            else:
                tmp = np.trace(tmp)
                if abs(tmp.imag) < symprec:
                    tmp = tmp.real
                if abs(tmp.real) < symprec:
                    tmp = complex(0, tmp.imag)
                    if abs(tmp.imag) < symprec:
                        tmp = 0
                tmp_character.append(tmp)
        character_tabel.append(tmp_character)
    return character_tabel


class CharacterDataset(typing.NamedTuple):
    """dataset of the final result

    Args:
        index: order
        quantum_number: SAB
        character_table:
    """

    index: list[int]
    quantum_number: list[tuple]
    character_table: list


def line_group_1(
    q: int,
    r: int,
    a: float,
    f: float,
    n: int,
    k1: float,
    k2: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """TQ(f)Cn"""

    # if the input satisfy the requirements
    judge = True
    message = []
    if k1 <= -np.pi / a or k1 > np.pi / a:
        judge = False
        message.append("k1 not belong to (-pi/a,pi/a]")

    if k2 <= -np.pi / f or k2 > np.pi / f:
        judge = False
        message.append("k2 not belong to (-pi/f,pi/f]")

    m1 = frac_range(-q / 2, q / 2, left=False)
    m2 = frac_range(-n / 2, n / 2, left=False)

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m1, m2]))
        for comb in combs:
            tmp_m1, tmp_m2 = comb

            irrep1 = np.round(
                [
                    np.exp(1j * (k1 * f + tmp_m1 * 2 * np.pi * r / q)),
                    np.exp(1j * tmp_m1 * 2 * np.pi / n),
                ],
                round_symprec,
            )
            irrep2 = np.round(
                [np.exp(1j * k2 * f), np.exp(1j * tmp_m2 * 2 * np.pi / n)],
                round_symprec,
            )
            irreps = [irrep1, irrep2]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            quantum_number.append(((k1, tmp_m1), (k2, tmp_m2)))
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def line_group_2(
    a: float,
    n: float,
    k: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """T(a)S2n"""

    # whether the input satisfy the requirements
    judge = True
    message = []
    if k < 0 or k > np.pi:
        judge = False
        message.append("k not belong to [0,pi]")

    m = frac_range(-n / 2, n / 2, left=False)
    piH = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m, piH]))
        for comb in combs:
            tmp_m, tmp_piH = comb
            if k == 0 or k == np.pi / a:
                irrep1 = np.round(
                    [
                        np.exp(1j * k * a),
                        tmp_piH * np.exp(1j * tmp_m * np.pi / n),
                    ],
                    round_symprec,
                )
                quantum_number.append((k, tmp_m, tmp_piH))
                irreps = [irrep1]
                character_table.append(_cal_irrep_trace(irreps, symprec))
            else:
                irrep1 = np.round(
                    [
                        [
                            [np.exp(1j * k * a), 0],
                            [0, np.exp(-1j * k * a)],
                        ],
                        [[0, np.exp(1j * tmp_m * np.pi / n)], [1, 0]],
                    ],
                    round_symprec,
                )
                quantum_number.append(((k, tmp_m), (-k, tmp_m)))
                irreps = [irrep1]
                character_table.append(_cal_irrep_trace(irreps, symprec))

            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def line_group_3(
    a: float,
    n: float,
    k: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """T(a)Cnh"""

    # whether the input satisfy the requirements
    judge = True
    message = []

    if k <= 0 or k >= np.pi:
        judge = False
        message.append("k not belong to [0,pi]")

    m = frac_range(-n / 2, n / 2, left=False)
    piH = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m, piH]))
        for comb in combs:
            tmp_m, tmp_piH = comb

            if k == 0 or k == np.pi / a:
                irrep1 = np.round(
                    [
                        np.exp(1j * k * a),
                        np.exp(1j * tmp_m * 2 * np.pi / n),
                        tmp_piH,
                    ],
                    round_symprec,
                )
                irreps = [irrep1]
                character_table.append(_cal_irrep_trace(irreps, symprec))
                quantum_number.append((k, tmp_m, tmp_piH))

            else:
                irrep1 = np.round(
                    [
                        [
                            [np.exp(1j * k * a), 0],
                            [0, np.exp(-1j * k * a)],
                        ],
                        [
                            [np.exp(1j * tmp_m * 2 * np.pi / n), 0],
                            [0, np.exp(1j * tmp_m * 2 * np.pi / n)],
                        ],
                        [[0, 1], [1, 0]],
                    ],
                    round_symprec,
                )
                irreps = [irrep1]
                character_table.append(_cal_irrep_trace(irreps, symprec))
                quantum_number.append((((k, tmp_m), (-k, tmp_m))))

            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def line_group_4(
    a: float,
    n: float,
    k1: float,
    k2: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """T(a)Cnh"""

    # whether the input satisfy the requirements
    judge = True
    message = []

    if k1 < 0 or k1 > np.pi / a:
        judge = False
        message.append("k1 not belong to [0,pi/a]")

    m1 = frac_range(-n, n, left=False)
    m2 = frac_range(-n / 2, n / 2, left=False)
    piH = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m1, m2, piH]))
        for comb in combs:
            tmp_m1, tmp_m2, tmp_piH = comb

            if k2 < 2 * np.pi * tmp_m2 / n / a or k2 > (
                2 * np.pi / a + 2 * np.pi * tmp_m2 / n / a
            ):
                continue

            tmp_qn = []
            if k1 == 0:
                irrep1 = np.round(
                    [
                        np.exp(1j * tmp_m1 * np.pi / n),
                        np.exp(1j * tmp_m1 * 2 * np.pi / n),
                        tmp_piH,
                    ],
                    round_symprec,
                )
                tmp_qn.append((k1, tmp_m1, tmp_piH))
            else:
                irrep1 = np.round(
                    [
                        [
                            [
                                np.exp(1j * (tmp_m1 * np.pi / n + k1 * a / 2)),
                                0,
                            ],
                            [
                                0,
                                np.exp(1j * (tmp_m1 * np.pi / n - k1 * a / 2)),
                            ],
                        ],
                        [
                            [
                                np.exp(1j * tmp_m1 * 2 * np.pi / n),
                                0,
                            ],
                            [
                                0,
                                np.exp(1j * tmp_m1 * 2 * np.pi / n),
                            ],
                        ],
                        [[0, 1], [1, 0]],
                    ],
                    round_symprec,
                )
                tmp_qn.append(((k1, tmp_m1), (-k1, tmp_m1)))

            if (
                k2 == 2 * np.pi * tmp_m2 / n / a
                or k2 == 2 * np.pi * tmp_m2 / n / a + 2 * np.pi / a
            ):
                irrep2 = np.round(
                    [
                        np.exp(1j * k2 * a / 2),
                        np.exp(1j * tmp_m2 * 2 * np.pi / n),
                        tmp_piH,
                    ],
                    round_symprec,
                )
                tmp_qn.append((k2, tmp_m2, tmp_piH))
            else:
                irrep2 = np.round(
                    [
                        [
                            [np.exp(1j * k2 * a / 2), 0],
                            [
                                0,
                                np.exp(
                                    1j * (tmp_m2 * 2 * np.pi / n - k2 * a / 2)
                                ),
                            ],
                        ],
                        [
                            [
                                np.exp(1j * tmp_m2 * 2 * np.pi / n),
                                0,
                            ],
                            [
                                0,
                                np.exp(1j * tmp_m2 * 2 * np.pi / n),
                            ],
                        ],
                        [[0, 1], [1, 0]],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    ((k2, tmp_m2), (-k2 + 4 * tmp_m2 * np.pi / n / a, tmp_m2))
                )

            irreps = [irrep1, irrep2]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            quantum_number.append(tuple(tmp_qn))
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


# Todo: k1/m1? p?
def line_group_5(
    q: int,
    r: int,
    a: float,
    f: float,
    p: int,
    n: float,
    k1: float,
    k2: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """TQ(f)Dn"""
    # row_labels = [r"$(C_{2n}|1/2)$", r"$C_{n}$", r"$\sigma_{h}$"]
    # column_labels = [r"$_{0}A_{m}^{\Pi_{h}}$", r"$_{k}E_{m}$", r"$_{\widetilde{k}_{\widetilde{M}}(\widetilde{m})}A_{\widetilde{m}}^{\Pi_{h}}$", r"$_{\widetilde{k}}E_{\widetilde{m}}$"]

    # whether the input satisfy the requirements
    judge = True
    message = []

    if k1 < 0 or k1 > np.pi / a:
        judge = False
        message.append("k1 not belong to [0,pi/a]")

    if k2 < 0 or k2 > np.pi / f:
        judge = False
        message.append("k2 not belong to [0,pi/f]")

    if k1 == 0:
        m1 = [0, q / 2]
    elif k1 == np.pi / a:
        m1 = [-p / 2, (q - p) / 2]
    else:
        m1 = frac_range(-q / 2, q / 2, left=False)

    m2 = frac_range(-n, n, left=False)
    piH = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m1, m2, piH]))
        for comb in combs:
            tmp_m1, tmp_m2, tmp_piH = comb

            if k2 < 2 * np.pi * tmp_m2 / n / a or k2 > (
                2 * np.pi / a + 2 * np.pi * tmp_m2 / n / a
            ):
                continue

            tmp_qn = []
            if k1 == 0:
                irrep1 = np.round(
                    [
                        np.exp(1j * tmp_m1 * np.pi / n),
                        np.exp(1j * tmp_m1 * 2 * np.pi / n),
                        tmp_piH,
                    ],
                    round_symprec,
                )
                tmp_qn.append((k1, tmp_m1, tmp_piH))
            else:
                irrep1 = np.round(
                    [
                        [
                            [
                                np.exp(1j * (tmp_m1 * np.pi / n + k1 * a / 2)),
                                0,
                            ],
                            [
                                0,
                                np.exp(1j * (tmp_m1 * np.pi / n - k1 * a / 2)),
                            ],
                        ],
                        [
                            [
                                np.exp(1j * tmp_m1 * 2 * np.pi / n),
                                0,
                            ],
                            [
                                0,
                                np.exp(1j * tmp_m1 * 2 * np.pi / n),
                            ],
                        ],
                        [[0, 1], [1, 0]],
                    ],
                    round_symprec,
                )
                tmp_qn.append(((k1, tmp_m1), (-k1, tmp_m1)))

            if (
                k2 == 2 * np.pi * tmp_m2 / n / a
                or k2 == 2 * np.pi * tmp_m2 / n / a + 2 * np.pi / a
            ):
                irrep2 = np.round(
                    [
                        np.exp(1j * k2 * a / 2),
                        np.exp(1j * tmp_m2 * 2 * np.pi / n),
                        tmp_piH,
                    ],
                    round_symprec,
                )
                tmp_qn.append((k2, tmp_m2, tmp_piH))
            else:
                irrep2 = np.round(
                    [
                        [
                            [np.exp(1j * k2 * a / 2), 0],
                            [
                                0,
                                np.exp(
                                    1j * (tmp_m2 * 2 * np.pi / n - k2 * a / 2)
                                ),
                            ],
                        ],
                        [
                            [
                                np.exp(1j * tmp_m2 * 2 * np.pi / n),
                                0,
                            ],
                            [
                                0,
                                np.exp(1j * tmp_m2 * 2 * np.pi / n),
                            ],
                        ],
                        [[0, 1], [1, 0]],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    ((k2, tmp_m2), (-k2 + 4 * tmp_m2 * np.pi / n / a, tmp_m2))
                )

            irreps = [irrep1, irrep2]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            quantum_number.append(tuple(tmp_qn))
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def line_group_6(
    a: float,
    n: int,
    k1: float,
    k2: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """T(a)Cnv"""

    # whether the input satisfy the requirements
    judge = True
    message = []
    if k1 <= -np.pi / a or k1 > np.pi / a:
        judge = False
        message.append("k1 not belong to (-pi/a,pi/a]")

    if k2 <= -np.pi / a or k2 > np.pi / a:
        judge = False
        message.append("k2 not belong to (-pi/f,pi/f]")

    m1 = [0, n / 2]
    m2 = frac_range(0, n / 2, left=False, right=False)
    piV = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(
            itertools.product(*[m1, m2, piV])
        )  # all the combination of parameters
        for comb in combs:
            tmp_m1, tmp_m2, tmp_piV = comb

            irrep1 = np.round(
                [
                    np.exp(1j * k1 * a),
                    np.exp(1j * tmp_m1 * 2 * np.pi / n),
                    tmp_piV,
                ],
                round_symprec,
            )
            irrep2 = np.round(
                [
                    [
                        [np.exp(1j * k2 * a), 0],
                        [0, np.exp(1j * k2 * a)],
                    ],
                    [
                        [np.exp(1j * tmp_m2 * 2 * np.pi / n), 0],
                        [0, np.exp(-1j * tmp_m2 * 2 * np.pi / n)],
                    ],
                    [[0, 1], [1, 0]],
                ],
                round_symprec,
            )
            irreps = [irrep1, irrep2]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            quantum_number.append(
                ((k1, tmp_m1, tmp_piV), ((k2, -tmp_m2), (k2, tmp_m2)))
            )
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def line_group_7(
    a: float,
    n: int,
    k1: float,
    k2: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """T'(a/2)Cn"""

    # whether the input satisfy the requirements
    judge = True
    message = []
    if k1 <= -np.pi / a or k1 > np.pi / a:
        judge = False
        message.append("k1 not belong to (-pi/a,pi/a]")

    if k2 <= -np.pi / a or k2 > np.pi / a:
        judge = False
        message.append("k2 not belong to (-pi/a,pi/a]")

    m1 = [0, n / 2]
    m2 = frac_range(0, n / 2, left=False, right=False)
    piV = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m1, m2, piV]))
        for comb in combs:
            tmp_m1, tmp_m2, tmp_piV = comb

            irrep1 = np.round(
                [
                    tmp_piV * np.exp(1j * k1 * a / 2),
                    np.exp(1j * tmp_m1 * 2 * np.pi / n),
                ],
                round_symprec,
            )
            irrep2 = np.round(
                [
                    [
                        [0, np.exp(1j * k2 * a / 2)],
                        [np.exp(1j * k2 * a / 2), 0],
                    ],
                    [
                        [np.exp(1j * tmp_m2 * 2 * np.pi / n), 0],
                        [0, np.exp(-1j * tmp_m2 * 2 * np.pi / n)],
                    ],
                ],
                round_symprec,
            )
            irreps = [irrep1, irrep2]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            quantum_number.append(
                ((k1, tmp_m1, tmp_piV), ((k2, tmp_m2), (k2, -tmp_m2)))
            )
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def line_group_8(
    a: float,
    n: int,
    k1: float,
    k2: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """T_{2n}^{1}(a/2)Cnv"""

    # whether the input satisfy the requirements
    judge = True
    message = []
    if k1 <= -np.pi / a or k1 > np.pi / a:
        judge = False
        message.append("k1 not belong to (-pi/a,pi/a]")

    if k2 <= -2 * np.pi / a or k2 > 2 * np.pi / a:
        judge = False
        message.append("k2 not belong to (-2pi/a,2pi/a]")

    m1 = frac_range(0, n)
    m2 = frac_range(0, n / 2)
    piV = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m1, m2, piV]))
        for comb in combs:
            tmp_m1, tmp_m2, tmp_piV = comb

            tmp_qn = []
            if tmp_m1 == 0 or tmp_m1 == n:
                irrep1 = np.round(
                    [
                        np.exp(1j * k1 * a / 2 + tmp_m1 * np.pi / n),
                        1,
                        tmp_piV,
                    ],
                    round_symprec,
                )
                tmp_qn.append((k1, tmp_m1, tmp_piV))
            else:
                irrep1 = np.round(
                    [
                        [
                            [np.exp(1j * k2 * a / 2 + tmp_m2 * np.pi / n), 0],
                            [0, np.exp(1j * k2 * a / 2 - tmp_m2 * np.pi / n)],
                        ],
                        [
                            [np.exp(1j * tmp_m2 * 2 * np.pi / n), 0],
                            [0, np.exp(-1j * tmp_m2 * 2 * np.pi / n)],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(((k1, tmp_m1), (k1, -tmp_m1)))

            if tmp_m2 == 0:
                irrep2 = np.round(
                    [
                        np.exp(1j * k2 * a / 2),
                        1,
                        tmp_piV,
                    ],
                    round_symprec,
                )
                tmp_qn.append((k2, 0, tmp_piV))

            else:
                if tmp_m2 == n / 2:
                    if k2 <= 0:
                        continue

                irrep2 = np.round(
                    [
                        [
                            [np.exp(1j * k2 * a / 2), 0],
                            [
                                0,
                                np.exp(
                                    1j * k2 * a / 2 - tmp_m2 * 2 * np.pi / n
                                ),
                            ],
                        ],
                        [
                            [np.exp(1j * tmp_m2 * 2 * np.pi / n), 0],
                            [0, np.exp(-1j * tmp_m2 * 2 * np.pi / n)],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    (
                        (k2, tmp_m2, 0),
                        (k2 - 4 * tmp_m2 * np.pi / n / a, -tmp_m2, 0),
                    )
                )

            irreps = [irrep1, irrep2]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            set_trace()
            quantum_number.append(tuple(tmp_qn))
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def line_group_9(
    a: float,
    n: int,
    k1: float,
    k2: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """T(a)Dnd"""
    # whether the input satisfy the requirements
    judge = True
    message = []
    if k1 < 0 or k1 > np.pi / a:
        judge = False
        message.append("k1 not belong to [0,pi/a]")

    if k2 < 0 or k2 > np.pi / a:
        judge = False
        message.append("k2 not belong to [0,pi/a]")

    m1 = [0, n / 2]
    m2 = frac_range(0, n / 2, left=False, right=False)
    piU = [-1, 1]
    piV = [-1, 1]
    piH = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m1, m2, piU, piV, piH]))
        for comb in combs:
            (
                tmp_m1,
                tmp_m2,
                tmp_piU,
                tmp_piV,
                tmp_piH,
            ) = comb

            tmp_qn = []
            if k1 == 0 or k1 == np.pi / a:
                if tmp_m1 == 0:
                    irrep1 = np.round(
                        [
                            np.exp(1j * k1 * a),
                            1,
                            tmp_piU,
                            tmp_piV,
                        ],
                        round_symprec,
                    )
                    tmp_qn.append((k1, 0, tmp_piU, tmp_piV, tmp_piH))
                elif tmp_m1 == n / 2:
                    irrep1 = np.round(
                        [
                            [
                                [np.exp(1j * k1 * a), 0],
                                [0, np.exp(1j * k1 * a)],
                            ],
                            [
                                [-1, 0],
                                [0, -1],
                            ],
                            [
                                [0, 1],
                                [1, 0],
                            ],
                            [
                                [1, 0],
                                [0, -1],
                            ],
                        ],
                        round_symprec,
                    )
                    tmp_qn.append(
                        ((k1, tmp_m1, 0, "A", 0), (k1, tmp_m1, 0, "B", 0))
                    )  # Todo: check A/B
            else:
                irrep1 = np.round(
                    [
                        [
                            [
                                np.exp(1j * k1 * a),
                                0,
                            ],
                            [
                                0,
                                np.exp(-1j * k1 * a),
                            ],
                        ],
                        [
                            [np.exp(1j * tmp_m1 * 2 * np.pi / n), 0],
                            [0, np.exp(1j * tmp_m1 * 2 * np.pi / n)],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                        [
                            [tmp_piV, 0],
                            [
                                0,
                                tmp_piV * np.exp(1j * tmp_m1 * 2 * np.pi / n),
                            ],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    (
                        (k1, tmp_m1, 0, tmp_piV, 0),
                        (
                            -k1,
                            tmp_m1,
                            0,
                            np.exp(1j * tmp_m1 * 2 * np.pi / n * tmp_piV),
                            0,
                        ),
                    )
                )  # Todo: check A/B

            if k2 == 0 or k2 == np.pi / a:

                irrep2 = np.round(
                    [
                        [
                            [
                                np.exp(1j * k2 * a),
                                0,
                            ],
                            [
                                0,
                                np.exp(1j * k2 * a),
                            ],
                        ],
                        [
                            [
                                np.exp(1j * tmp_m2 * 2 * np.pi / n),
                                0,
                            ],
                            [
                                0,
                                np.exp(-1j * tmp_m2 * 2 * np.pi / n),
                            ],
                        ],
                        [
                            [
                                0,
                                tmp_piH * np.exp(1j * tmp_m2 * np.pi / n),
                            ],
                            [
                                tmp_piH * np.exp(-1j * tmp_m2 * np.pi / n),
                                0,
                            ],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    (
                        (k2, tmp_m2, 0, 0, tmp_piH),
                        (-k1, -tmp_m1, 0, 0, tmp_piH),
                    )
                )  # Todo: check A/B
            else:
                irrep2 = np.round(
                    [
                        [
                            [
                                np.exp(1j * k2 * a),
                                0,
                                0,
                                0,
                            ],
                            [
                                0,
                                np.exp(1j * k2 * a),
                                0,
                                0,
                            ],
                            [
                                0,
                                0,
                                np.exp(-1j * k2 * a),
                                0,
                            ],
                            [
                                0,
                                0,
                                0,
                                np.exp(-1j * k2 * a),
                            ],
                        ],
                        [
                            [
                                np.exp(1j * tmp_m2 * 2 * np.pi / n),
                                0,
                                0,
                                0,
                            ],
                            [
                                0,
                                np.exp(-1j * tmp_m2 * 2 * np.pi / n),
                                0,
                                0,
                            ],
                            [
                                0,
                                0,
                                np.exp(-1j * tmp_m2 * 2 * np.pi / n),
                                0,
                            ],
                            [
                                0,
                                0,
                                0,
                                np.exp(1j * tmp_m2 * 2 * np.pi / n),
                            ],
                        ],
                        [
                            [0, 0, 1, 0],
                            [0, 0, 0, 1],
                            [1, 0, 0, 0],
                            [0, 1, 0, 0],
                        ],
                        [
                            [0, 1, 0, 0],
                            [1, 0, 0, 0],
                            [
                                0,
                                0,
                                0,
                                np.exp(1j * tmp_m2 * 2 * np.pi / n),
                            ],
                            [
                                0,
                                0,
                                np.exp(-1j * tmp_m2 * 2 * np.pi / n),
                                0,
                            ],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    (
                        (k2, tmp_m2, 0, 0, 0),
                        (k1, -tmp_m1, 0, 0, 0),
                        (-k1, -tmp_m1, 0, 0, 0),
                        (-k1, tmp_m1, 0, 0, 0),
                    )
                )  # Todo: check A/B

            irreps = [irrep1, irrep2]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            quantum_number.append(tuple(tmp_qn))
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def line_group_10(
    a: float,
    n: int,
    k1: float,
    k2: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """T'(a/2)S2n"""

    # whether the input satisfy the requirements
    judge = True
    message = []
    if k1 < 0 or k1 > np.pi / a:
        judge = False
        message.append("k1 not belong to [0,pi/a]")

    if k2 < 0 or k2 > np.pi / a:
        judge = False
        message.append("k2 not belong to [0,pi/a]")

    m1 = [0, n / 2]
    m2 = frac_range(0, n / 2, left=False, right=False)
    piU = [-1, 1]
    piV = [-1, 1]
    piH = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m1, m2, piU, piV, piH]))
        for comb in combs:
            (
                tmp_m1,
                tmp_m2,
                tmp_piU,
                tmp_piV,
                tmp_piH,
            ) = comb

            tmp_qn = []
            if (k1 == 0 and tmp_m1 == 0) or (
                k1 == np.pi / a and tmp_m1 == n / 2
            ):
                irrep1 = np.round(
                    [
                        tmp_piV * np.exp(1j * k1 * a / 2),
                        tmp_piV * tmp_piU * np.exp(1j * tmp_m1 * np.pi / n),
                    ],
                    round_symprec,
                )
                tmp_qn.append((k1, tmp_m1, tmp_piU, tmp_piV, tmp_piH))

            elif (k1 == 0 and tmp_m1 == n / 2) or (
                k1 == np.pi / a and tmp_m1 == 0
            ):
                irrep1 = np.round(
                    [
                        [
                            [np.exp(1j * 12 * a / 2), 0],
                            [0, -np.exp(1j * 12 * a / 2)],
                        ],
                        [
                            [0, -np.exp(1j * 12 * np.pi / n)],
                            [1, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    ((k1, tmp_m1, 0, "A", 0), (k1, tmp_m1, 0, "B", 0))
                )  # Todo: check A/B
            else:
                irrep1 = np.round(
                    [
                        [
                            [tmp_piV * np.exp(1j * k1 * a / 2), 0],
                            [
                                0,
                                tmp_piV
                                * np.exp(
                                    1j * (tmp_m1 * 2 * np.pi / n - k1 * a / 2)
                                ),
                            ],
                        ],
                        [
                            [0, np.exp(1j * tmp_m1 * 2 * np.pi / n)],
                            [1, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    (
                        (k1, tmp_m1, 0, tmp_piV, 0),
                        (
                            -k1,
                            tmp_m1,
                            0,
                            np.exp(1j * 2 * np.pi / n * tmp_m1) * tmp_piV,
                            0,
                        ),
                    )
                )

            if k2 == 0 or k2 == np.pi / a:
                irrep2 = np.round(
                    [
                        [
                            [0, np.exp(1j * k2 * a / 2)],
                            [np.exp(1j * k2 * a / 2), 0],
                        ],
                        [
                            [tmp_piH * np.exp(1j * tmp_m2 * np.pi / n), 0],
                            [
                                0,
                                tmp_piH
                                * np.exp(1j * (k2 * a - tmp_m2 * np.pi / n)),
                            ],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    (
                        (k2, tmp_m2, 0, 0, tmp_piH),
                        (k2, -tmp_m2, 0, 0, np.exp(1j * k2 * a) * tmp_piH),
                    )
                )
            else:
                irrep2 = np.round(
                    [
                        [
                            [0, np.exp(1j * k2 * a / 2), 0, 0],
                            [np.exp(1j * k2 * a / 2), 0, 0, 0],
                            [
                                0,
                                0,
                                0,
                                np.exp(
                                    -1j * (tmp_m2 * 2 * np.pi / n + k2 * a / 2)
                                ),
                            ],
                            [
                                0,
                                0,
                                np.exp(
                                    1j * (tmp_m2 * 2 * np.pi / n - k2 * a / 2)
                                ),
                                0,
                            ],
                        ],
                        [
                            [0, 0, np.exp(1j * tmp_m2 * 2 * np.pi / n), 0],
                            [0, 0, 0, np.exp(-1j * tmp_m2 * 2 * np.pi / n)],
                            [1, 0, 0, 0],
                            [0, 1, 0, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    (
                        (k2, tmp_m2, 0, 0, 0),
                        (k2, -tmp_m2, 0, 0, 0),
                        (-k2, tmp_m2, 0, 0, 0),
                        (-k2, -tmp_m2, 0, 0, 0),
                    )
                )

            irreps = [irrep1, irrep2]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            quantum_number.append(tuple(tmp_qn))
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def line_group_11(
    a: float,
    n: int,
    k1: float,
    k2: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """TDnh"""
    # label for line group family
    # row_labels = [r"$(C_{Q}|f)$", r"$C_{n}$"]
    # column_labels = [r"$_{k}A_{m}$", r"$_{\widetilde{k}}A_{\widetilde{m}}$"]

    # whether the input satisfy the requirements
    judge = True
    message = []

    if k1 < 0 or k1 > np.pi:
        judge = False
        message.append("k1 not belong to [0,pi]")

    if k2 < 0 or k2 > np.pi:
        judge = False
        message.append("k2 not belong to [0,pi]")

    m1 = frac_range(0, n / 2)
    m2 = frac_range(0, n / 2)
    piV = [-1, 1]
    piH = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m1, m2, piV, piH]))
        for comb in combs:
            tmp_m1, tmp_m2, tmp_piV, tmp_piH = comb

            tmp_qm = []
            if k1 == 0 or k1 == np.pi:
                irrep1 = np.round(
                    [
                        np.exp(1j * k1 * a),
                        np.exp(1j * tmp_m1 * 2 * np.pi / n),
                        tmp_piV,
                        tmp_piH,
                    ],
                    round_symprec,
                )
                tmp_qm.append((k1, tmp_m1, 0, tmp_piV, tmp_piH))

            else:
                irrep1 = np.round(
                    [
                        [
                            [np.exp(1j * k1 * a), 0],
                            [0, np.exp(-1j * k1 * a)],
                        ],
                        [
                            [np.exp(1j * tmp_m1 * 2 * np.pi / n), 0],
                            [0, np.exp(1j * tmp_m1 * 2 * np.pi / n)],
                        ],
                        [
                            [tmp_piV, 0],
                            [0, tmp_piV],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qm.append(
                    ((k1, tmp_m1, 0, tmp_piV, 0), (-k1, tmp_m1, 0, tmp_piV, 0))
                )

            if k2 == 0 or k2 == np.pi:
                irrep2 = np.round(
                    [
                        [
                            [np.exp(1j * k2 * a), 0],
                            [0, -np.exp(1j * k2 * a)],
                        ],
                        [
                            [np.exp(1j * tmp_m2 * 2 * np.pi / n), 0],
                            [0, np.exp(-1j * tmp_m2 * 2 * np.pi / n)],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                        [
                            [tmp_piH, 0],
                            [0, tmp_piH],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qm.append(
                    ((k2, tmp_m2, 0, 0, tmp_piH), (k2, -tmp_m2, 0, 0, tmp_piH))
                )

            else:
                irrep2 = np.round(
                    [
                        [
                            [np.exp(1j * k2 * a), 0, 0, 0],
                            [0, np.exp(1j * k2 * a), 0, 0],
                            [0, 0, np.exp(-1j * k2 * a), 0],
                            [0, 0, 0, np.exp(-1j * k2 * a)],
                        ],
                        [
                            [np.exp(1j * tmp_m2 * 2 * np.pi / n), 0, 0, 0],
                            [0, np.exp(-1j * tmp_m2 * 2 * np.pi / n), 0, 0],
                            [0, 0, np.exp(1j * tmp_m2 * 2 * np.pi / n), 0],
                            [0, 0, 0, np.exp(-1j * tmp_m2 * 2 * np.pi / n)],
                        ],
                        [
                            [0, 1, 0, 0],
                            [1, 0, 0, 0],
                            [0, 0, 0, 1],
                            [0, 0, 1, 0],
                        ],
                        [
                            [0, 0, 1, 0],
                            [0, 0, 0, 1],
                            [1, 0, 0, 0],
                            [0, 1, 0, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qm.append(
                    (
                        (k2, tmp_m2, 0, 0, 0),
                        (k2, -tmp_m2, 0, 0, 0),
                        (-k2, tmp_m2, 0, 0, 0),
                        (-k2, -tmp_m2, 0, 0, 0),
                    )
                )

            irreps = [irrep1, irrep2]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            quantum_number.append(tuple(tmp_qm))
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def line_group_12(
    a: float,
    n: int,
    k1: float,
    k2: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """T'(a/2)Cnh"""

    # whether the input satisfy the requirements
    judge = True
    message = []

    if k1 < 0 or k1 > np.pi:
        judge = False
        message.append("k1 not belong to [0,pi]")

    if k2 < 0 or k2 > np.pi:
        judge = False
        message.append("k2 not belong to [0,pi]")

    m1 = [0, n / 2]
    m2 = frac_range(0, n / 2, left=False, right=False)
    piU = [-1, 1]
    piV = [-1, 1]
    piH = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m1, m2, piU, piV, piH]))
        for comb in combs:
            (
                tmp_m1,
                tmp_m2,
                tmp_piU,
                tmp_piV,
                tmp_piH,
            ) = comb

            tmp_qn = []
            if k1 == 0:
                irrep1 = np.round(
                    [tmp_piV, np.exp(1j * tmp_m1 * 2 * np.pi / n), tmp_piH],
                    round_symprec,
                )
                tmp_qn.append((k1, tmp_m1, tmp_piU, tmp_piV, tmp_piH))

            elif k1 == np.pi:
                irrep1 = np.round(
                    [
                        [
                            [1j, 0],
                            [0, -1j],
                        ],
                        [
                            [np.exp(1j * tmp_m1 * 2 * np.pi / n), 0],
                            [0, np.exp(1j * tmp_m1 * 2 * np.pi / n)],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    ((np.pi, tmp_m1, 0, "A", 0), (np.pi, tmp_m1, 0, "B", 0))
                )  # Todo: check the value of A/B
            else:
                irrep1 = np.round(
                    [
                        [
                            [tmp_piV * np.exp(1j * k1 * a / 2), 0],
                            [0, tmp_piV * np.exp(-1j * k1 * a / 2)],
                        ],
                        [
                            [np.exp(1j * tmp_m1 * 2 * np.pi / n), 0],
                            [0, np.exp(1j * tmp_m1 * 2 * np.pi / n)],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    ((k1, tmp_m1, 0, tmp_piV, 0), (-k1, tmp_m1, 0, tmp_piV, 0))
                )

            if k2 == 0 or k2 == np.pi:
                irrep2 = np.round(
                    [
                        [
                            [0, np.exp(1j * k2 * a / 2)],
                            [np.exp(1j * k2 * a / 2), 0],
                        ],
                        [
                            [np.exp(1j * tmp_m2 * 2 * np.pi / n), 0],
                            [0, np.exp(-1j * tmp_m2 * 2 * np.pi / n)],
                        ],
                        [
                            [tmp_piH, 0],
                            [0, tmp_piH],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    ((k1, tmp_m1, 0, 0, tmp_piH), (k1, -tmp_m1, 0, 0, tmp_piH))
                )

            else:
                irrep2 = np.round(
                    [
                        [
                            [0, np.exp(1j * k2 * a / 2), 0, 0],
                            [np.exp(1j * k2 * a / 2), 0, 0, 0],
                            [0, 0, 0, np.exp(-1j * k2 * a / 2)],
                            [0, 0, np.exp(-1j * k2 * a / 2), 0],
                        ],
                        [
                            [np.exp(1j * tmp_m2 * 2 * np.pi / n), 0, 0, 0],
                            [0, np.exp(-1j * tmp_m2 * 2 * np.pi / n), 0, 0],
                            [0, 0, np.exp(1j * tmp_m2 * 2 * np.pi / n), 0],
                            [0, 0, 0, np.exp(-1j * tmp_m2 * 2 * np.pi / n)],
                        ],
                        [
                            [0, 0, 1, 0],
                            [0, 0, 0, 1],
                            [1, 0, 0, 0],
                            [0, 1, 0, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    (
                        (k1, tmp_m1, 0, 0, 0),
                        (k1, -tmp_m1, 0, 0, 0),
                        (-k1, tmp_m1, 0, 0, 0),
                        (-k1, -tmp_m1, 0, 0, 0),
                    )
                )

            irreps = [irrep1, irrep2]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            quantum_number.append(tuple(tmp_qn))
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


# Todo: unfinish
def line_group_13(
    q: int,
    r: int,
    a: float,
    f: float,
    n: int,
    k1: float,
    k2: float,
    k3: float,
    k4: float,
    symprec: float = 1e-4,
    round_symprec: int = 3,
) -> CharacterDataset:
    """T_{2n}^{1}Dnh"""
    # label for line group family
    # row_labels = [r"$(C_{Q}|f)$", r"$C_{n}$"]
    # column_labels = [r"$_{k}A_{m}$", r"$_{\widetilde{k}}A_{\widetilde{m}}$"]

    # whether the input satisfy the requirements
    judge = True
    message = []

    if k1 < 0 or k1 > np.pi / a:
        judge = False
        message.append("k1 not belong to [0,pi/a]")

    if k2 < 0 or k2 > np.pi / a:
        judge = False
        message.append("k2 not belong to [0,pi/a]")

    if k3 < 0 or k3 > 2 * np.pi / a:
        judge = False
        message.append("k3 not belong to [0,2pi/a]")

    if k4 <= 0 or k4 >= 3 * np.pi / a:
        judge = False
        message.append("k4 not belong to (0,3pi/a)")

    m1 = [0, n]
    m2 = frac_range(0, n, left=False, right=False)
    m3 = [0]
    m4 = frac_range(0, n / 2, left=False)
    piU = [-1, 1]
    piV = [-1, 1]
    piH = [-1, 1]

    if judge:
        ind = 0
        quantum_number = []
        character_table = []
        index = []

        combs = list(itertools.product(*[m1, m2, m3, m4, piU, piV, piH]))
        for comb in combs:
            (
                tmp_m1,
                tmp_m2,
                tmp_m3,
                tmp_m4,
                tmp_piU,
                tmp_piV,
                tmp_piH,
            ) = comb

            tmp_qn = []
            if k1 == 0:
                irrep1 = np.round(
                    [np.exp(1j * tmp_m1 * np.pi / n), 1, tmp_piU, tmp_piV],
                    round_symprec,
                )
                tmp_qn.append((0, tmp_m1, tmp_piU, tmp_piH, tmp_piV))
            elif k1 == np.pi / a and tmp_m1 == n:
                continue
            else:
                irrep1 = np.round(
                    [
                        [
                            [
                                np.exp(1j * tmp_m1 * np.pi / n)
                                * np.exp(1j * k1 * f),
                                0,
                            ],
                            [
                                0,
                                np.exp(1j * tmp_m1 * np.pi / n)
                                * np.exp(-1j * k1 * f),
                            ],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                        [
                            [0, tmp_piV],
                            [tmp_piV, 0],
                        ],
                        [
                            [tmp_piV, 0],
                            [0, tmp_piV],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    ((k1, tmp_m1, 0, tmp_piV, 0), (-k1, tmp_m1, 0, tmp_piV, 0))
                )

            if k2 == 0:
                irrep2 = np.round(
                    [
                        [
                            [np.exp(1j * tmp_m2 * np.pi / n), 0],
                            [0, np.exp(-1j * tmp_m2 * np.pi / n)],
                        ],
                        [
                            [np.exp(1j * 2 * tmp_m2 * np.pi / n), 0],
                            [0, np.exp(-1j * 2 * tmp_m2 * np.pi / n)],
                        ],
                        [
                            [0, tmp_piH],
                            [tmp_piH, 0],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    ((0, tmp_m2, 0, 0, tmp_piH), (0, -tmp_m1, 0, 0, tmp_piH))
                )

            elif k2 == np.pi / a and tmp_m2 == n / 2:
                irrep2 = np.round(
                    [
                        [
                            [-1, 0],
                            [0, 1],
                        ],
                        [
                            [-1, 0],
                            [0, -1],
                        ],
                        [
                            [tmp_piU, 0],
                            [0, tmp_piU],
                        ],
                        [
                            [0, 1],
                            [1, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    (
                        (np.pi / a, n / 2, tmp_piU, 0, 0),
                        (np.pi / a, -n / 2, tmp_piU, 0, 0),
                    )
                )
            else:
                if k2 == np.pi / a and n / 2 < tmp_m2 < n:
                    continue
                irrep2 = np.round(
                    [
                        [
                            [
                                np.exp(1j * (k2 * f + tmp_m2 * np.pi / n)),
                                0,
                                0,
                                0,
                            ],
                            [
                                0,
                                np.exp(1j * (k2 * f - tmp_m2 * np.pi / n)),
                                0,
                                0,
                            ],
                            [
                                0,
                                0,
                                np.exp(1j * (-k2 * f + tmp_m2 * np.pi / n)),
                                0,
                            ],
                            [
                                0,
                                0,
                                0,
                                np.exp(-1j * (k2 * f + tmp_m2 * np.pi / n)),
                            ],
                        ],
                        [
                            [np.exp(1j * tmp_m2 * 2 * np.pi / n), 0, 0, 0],
                            [0, np.exp(1j * tmp_m2 * 2 * np.pi / n), 0, 0],
                            [0, 0, np.exp(1j * tmp_m2 * 2 * np.pi / n), 0],
                            [0, 0, 0, np.exp(1j * tmp_m2 * 2 * np.pi / n)],
                        ],
                        [
                            [0, 0, 0, 1],
                            [0, 0, 1, 0],
                            [0, 1, 0, 0],
                            [1, 0, 0, 0],
                        ],
                        [
                            [0, 0, 1, 0],
                            [0, 0, 0, 1],
                            [1, 0, 0, 0],
                            [0, 1, 0, 0],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(
                    (
                        (np.pi / a, n / 2, tmp_piU, 0, 0),
                        (np.pi / a, -n / 2, tmp_piU, 0, 0),
                    )
                )

            if k3 == 0 or k3 == 2 * np.pi / a:
                irrep3 = np.round(
                    [np.exp(1j * k3 * a / 2), 1, tmp_piH * tmp_piV, tmp_piV],
                    round_symprec,
                )
                tmp_qn.append((k3, 0, tmp_piH, tmp_piV))
            else:
                irrep3 = np.round(
                    [
                        [
                            [np.exp(1j * k3 * f), 0],
                            [0, np.exp(-1j * k3 * f)],
                        ],
                        [
                            [1, 0],
                            [0, 1],
                        ],
                        [
                            [0, tmp_piV],
                            [tmp_piV, 0],
                        ],
                        [
                            [tmp_piV, 0],
                            [0, tmp_piV],
                        ],
                    ],
                    round_symprec,
                )
                tmp_qn.append(((k3, 0, tmp_piV), (-k3, 0, tmp_piV)))

            irreps = [irrep1, irrep2, irrep3, irrep4]
            character_table.append(_cal_irrep_trace(irreps, symprec))
            quantum_number.append(tuple(tmp_qn))
            index.append(ind)
            ind = ind + 1
        return CharacterDataset(index, quantum_number, character_table)
    else:
        print("error of input:")
        for tmp in message:
            print(tmp)


def main():
    parser = argparse.ArgumentParser(
        description="Generate the character table dataset of line group"
    )
    parser.add_argument("-F", "--family", type=int, default=1, help="")
    parser.add_argument(
        "-q",
        type=int,
        default=6,
        help="123",
    )
    parser.add_argument(
        "-r",
        type=int,
        default=2,
        help="",
    )
    parser.add_argument(
        "-a",
        type=float,
        default=9,
        help="",
    )
    parser.add_argument(
        "-f",
        type=float,
        default=3,
        help="",
    )
    parser.add_argument(
        "-n",
        type=int,
        default=5,
        help="",
    )
    parser.add_argument(
        "-k",
        type=list,
        default=[0, 0],
        help="",
    )

    parser.add_argument(
        "-s",
        "--s_name",
        type=str,
        default="poscar.vasp",
        help="the saved file name",
    )
    args = parser.parse_args()

    family = args.family
    if family in [1, 5]:
        q = args.q
        r = args.r
        a = args.a
        f = args.f
    else:
        a = args.a
        n = args.n

    a = 3
    n = 6
    k1 = 0
    k2 = 0
    k3 = np.pi / 3
    k4 = 2 * np.pi / a
    k5 = 2 * np.pi / a

    dataset = line_group_10(a, n, k1, k2)

    set_trace()


if __name__ == "__main__":
    main()
