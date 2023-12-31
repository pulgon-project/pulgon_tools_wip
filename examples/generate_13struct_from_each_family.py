# Copyright 2023 The PULGON Project Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

from pdb import set_trace

import numpy as np
import pretty_errors
from ase.io.vasp import write_vasp

from pulgon_tools_wip.generate_structures import (
    T_Q,
    Cn,
    S2n,
    T_v,
    U,
    U_d,
    change_center,
    dimino,
    generate_line_group_structure,
    sigmaH,
    sigmaV,
)


def input1():
    """(Cq|f),Cn"""
    motif = np.array([2, 0, 0])
    generators = np.array([Cn(4)])
    cyclic = {"T_Q": [6, 1.5]}
    st_name = "st1.vasp"
    return motif, generators, cyclic, st_name


def input2():
    """(I|q),S2n"""
    motif = np.array([3, 0, 1])
    generators = np.array([S2n(6)])
    cyclic = {"T_Q": [1, 3]}
    st_name = "st2.vasp"
    return motif, generators, cyclic, st_name


def input3():
    """(I|q),Cn,sigmaH"""
    motif = np.array([2.5, 0, 1])
    generators = np.array([Cn(6), sigmaH()])
    cyclic = {"T_Q": [1, 3]}
    st_name = "st3.vasp"
    return motif, generators, cyclic, st_name


def input4():
    """(C2n|f/2),Cn,sigmaH"""
    motif = np.array([3, 0, 0.6])
    generators = np.array([Cn(6), sigmaH()])
    cyclic = {"T_Q": [12, 4]}
    st_name = "st4.vasp"
    return motif, generators, cyclic, st_name


def input5():
    """(Cq|f),Cn,U"""
    motif = np.array([3, np.pi / 9, 0.5])
    generators = np.array([Cn(6), U()])
    cyclic = {"T_Q": [12, 4]}
    st_name = "st5.vasp"
    return motif, generators, cyclic, st_name


def input6():
    """(I|a),Cn,sigmaV"""
    motif = np.array([3, np.pi / 24, 1])
    generators = np.array([Cn(6), sigmaV()])
    cyclic = {"T_Q": [1, 3]}
    st_name = "st6.vasp"
    return motif, generators, cyclic, st_name


def input7():
    """(sigmaV|a/2),Cn"""
    motif = np.array([3, np.pi / 24, 1])
    generators = np.array([Cn(6)])
    cyclic = {"T_V": 1.5}
    st_name = "st7.vasp"
    return motif, generators, cyclic, st_name


def input8():
    """(C2n|a/2),Cn,sigmaV"""
    motif = np.array([3, np.pi / 24, 0])
    generators = np.array([Cn(6), sigmaV()])
    cyclic = {"T_Q": [12, 1.5]}
    st_name = "st8.vasp"
    return motif, generators, cyclic, st_name


def input9():
    """(I|a),Cn,Ud,sigmaV"""
    motif = np.array([3, np.pi / 24, 0.6])
    generators = np.array([Cn(6), U_d(np.pi / 12), sigmaV()])
    cyclic = {"T_Q": [1, 4]}
    st_name = "st9.vasp"
    return motif, generators, cyclic, st_name


def input10():
    """(sigmaV|a/2),S2n"""
    motif = np.array([3, np.pi / 18, 0.4])
    generators = np.array([S2n(6)])
    cyclic = {"T_V": 4}
    st_name = "st10.vasp"
    return motif, generators, cyclic, st_name


def input11():
    """(I|a),Cn,sigmaV"""
    motif = np.array([3, np.pi / 18, 0.6])
    generators = np.array([Cn(6), U(), sigmaV()])
    cyclic = {"T_Q": [1, 4]}
    st_name = "st11.vasp"
    return motif, generators, cyclic, st_name


def input12():
    """(sigmaV|a),Cn,U,sigmaV"""
    motif = np.array([3, np.pi / 24, 0.5])
    generators = np.array([Cn(6), sigmaH()])
    cyclic = {"T_V": 2.5}
    st_name = "st12.vasp"
    return motif, generators, cyclic, st_name


def input13():
    """(C2n|a/2),Cn,U,sigmaV"""
    motif = np.array([3, np.pi / 16, 0.6])
    generators = np.array([Cn(6), U(), sigmaV()])
    cyclic = {"T_Q": [12, 3]}
    st_name = "st13.vasp"
    return motif, generators, cyclic, st_name


def main():
    pos_cylin, generators, cg, st_name = input12()

    if pos_cylin.ndim == 1:
        pos = np.array(
            [
                pos_cylin[0] * np.cos(pos_cylin[1]),
                pos_cylin[0] * np.sin(pos_cylin[1]),
                pos_cylin[2],
            ]
        )
    else:
        pos = np.array(
            [
                pos_cylin[:, 0] * np.cos(pos_cylin[:, 1]),
                pos_cylin[:, 0] * np.sin(pos_cylin[:, 1]),
                pos_cylin[:, 2],
            ]
        )
        pos = pos.T
    rot_sym = dimino(generators, symec=3)
    monomer_pos = []
    for sym in rot_sym:
        if pos.ndim == 1:
            monomer_pos.append(np.dot(sym, pos.reshape(pos.shape[0], 1)).T[0])
        else:
            monomer_pos.extend([np.dot(sym, line) for line in pos])
    monomer_pos = np.array(monomer_pos)

    st = generate_line_group_structure(monomer_pos, cg, symprec=3)
    # set_trace()
    write_vasp("%s" % st_name, st, direct=True, sort=True, long_format=False)


if __name__ == "__main__":
    main()
