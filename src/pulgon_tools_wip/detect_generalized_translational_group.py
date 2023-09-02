import argparse
import itertools
from pdb import set_trace

import ase.io.vasp
import numpy as np
import pretty_errors
from ase import Atoms
from ase.io import read
from ase.io.vasp import read_vasp
from pymatgen.core import Molecule
from pymatgen.core.operations import SymmOp
from pymatgen.symmetry.analyzer import PointGroupAnalyzer
from pymatgen.util.coord import find_in_coord_list

from pulgon_tools_wip.utils import refine_cell


class CyclicGroupAnalyzer:
    """A class to analyze the generalized translational group (cyclic group)

    The general outline of the algorithm is as follows:

    1. find primitive cell and get the pure translation distance in z direction.
    2. get the potential monomers and the correspond translational vector.

    3. detect the possible cyclic group
       - If the rotational symmetry exist, it's a screw-axis group TQ(f) generated by (CQ|f).
       - If the mirror symmetry exist, it's a glide plane group T'(f) generated by (σv|f).

    """

    def __init__(
        self,
        atom: ase.atoms.Atoms,
        spmprec: float = 0.01,
        round_symprec: int = 3,
    ) -> None:
        """

        Args:
            atom: Line group structure to determine the generalized translational group
            spmprec: system precise tolerance
            round_symprec: system precise tolerance when take "np.round"
        """
        self._symprec = spmprec
        self._round_symprec = round_symprec
        self._zaxis = np.array([0, 0, 1])
        self._atom = atom

        self._primitive = self._find_primitive()
        self._pure_trans = self._primitive.cell[2, 2]

        # Todo: find out the x-y center, if mass center may not locate in circle center
        self._primitive = self._find_axis_center_of_nanotube(self._primitive)
        self._analyze()

    def _analyze(self) -> None:
        """print all possible monomers and their cyclic group"""
        monomer, potential_trans = self._potential_translation()
        self.cyclic_group, self.monomers = self._get_translations(
            monomer, potential_trans
        )

    def _find_axis_center_of_nanotube(
        self, atom: ase.atoms.Atoms
    ) -> ase.atoms.Atoms:
        """remove the center of structure to (x,y):(0,0)

        Args:
            atom: initial structure

        Returns: centralized structure

        """
        n_st = atom.copy()
        vector = atom.get_center_of_mass()
        atoms = Atoms(
            cell=n_st.cell,
            numbers=n_st.numbers,
            positions=n_st.positions - [vector[0], vector[1], 0],
        )

        return atoms

    def _get_translations(
        self, monomer_atoms: ase.atoms.Atoms, potential_tans: list
    ) -> [list, list]:
        """

        Args:
            monomer_atoms: possible monomers molecular
            potential_tans: translational distances in z direction of monomers

        Returns: cyclic groups and monomers

        """
        cyclic_group, mono = [], []
        for ii, monomer in enumerate(monomer_atoms):
            tran = potential_tans[ii]

            ind = int(np.round(1 / tran, self._round_symprec))

            if ind - 1 / tran > self._symprec:
                print("selecting wrong translation vector")
                continue

            if len(monomer) == len(self._primitive):
                cyclic_group.append("T")
                mono.append(monomer)
            else:
                # detect rotation
                rotation, Q = self._detect_rotation(
                    monomer, tran * self._pure_trans, ind
                )

                if rotation:
                    cyclic_group.append(
                        "T%s(%s)" % (Q, np.round(tran * self._pure_trans, 3))
                    )
                    mono.append(monomer)
                if (
                    ind == 2 and abs(tran - 0.5) < self._symprec
                ):  # only 2 layer in primitive cell
                    # detect mirror
                    coords = self._primitive.positions
                    diff_st_ind = np.array(
                        [
                            find_in_coord_list(coords, coord, self._symprec)
                            for coord in monomer.positions
                        ]
                    )
                    if diff_st_ind.ndim > 1:
                        diff_st_ind = diff_st_ind.T[0]

                    diff_st = self._primitive[
                        np.setdiff1d(range(len(coords)), diff_st_ind)
                    ]

                    mirror = self._detect_mirror(
                        monomer, diff_st, self._pure_trans / 2
                    )
                    if mirror:
                        cyclic_group.append(
                            "T'(%s)" % np.round(self._pure_trans / 2, 3)
                        )
                        mono.append(monomer)
        return cyclic_group, mono

    def _detect_rotation(
        self, monomer: ase.atoms.Atoms, tran: np.float64, ind: int
    ) -> [bool, int | float]:
        """

        Args:
            monomer: monomer candidates
            tran: the translational distance of monomer candidates
            ind: monomer layer numbers in the primitive cell

        Returns: judge if the rotational symmetry exist and rotational index Q

        """
        coords = self._primitive.positions

        # detect the monomer's rotational symmetry for specifying therotation
        mol = Molecule(species=monomer.numbers, coords=monomer.positions)
        monomer_rot_ind = PointGroupAnalyzer(mol)._check_rot_sym(self._zaxis)

        # possible rotational angle in cyclic group
        ind1 = (
            np.array(
                [
                    360 * ii / monomer_rot_ind
                    for ii in range(1, monomer_rot_ind + 1)
                ]
            )
            / ind
        )
        for test_ind in ind1:

            itp1, itp2 = (
                True,
                True,
            )  # record the rotational result from different layer
            for layer in range(1, ind):
                op1 = SymmOp.from_axis_angle_and_translation(
                    self._zaxis,
                    test_ind * layer,
                    translation_vec=(0, 0, tran * layer),
                )
                op2 = SymmOp.from_axis_angle_and_translation(
                    self._zaxis,
                    -test_ind * layer,
                    translation_vec=(0, 0, tran * layer),
                )
                itp3, itp4 = (
                    [],
                    [],
                )  # record the rotational result in current layer
                for site in monomer:
                    coord1 = op1.operate(site.position)
                    coord2 = op2.operate(site.position)

                    tmp1 = find_in_coord_list(coords, coord1, self._symprec)
                    tmp2 = find_in_coord_list(coords, coord2, self._symprec)
                    itp3.append(
                        len(tmp1) == 1
                        and self._primitive.numbers[tmp1[0]] == site.number
                    )
                    itp4.append(
                        len(tmp2) == 1
                        and self._primitive.numbers[tmp2[0]] == site.number
                    )
                itp1 = itp1 and np.array(itp3).all()
                itp2 = itp2 and np.array(itp4).all()
                if not (itp1 or itp2):
                    break

            if itp1 or itp2:
                Q = int(360 / test_ind)
                return True, Q
        return False, 1

    def _detect_mirror(
        self,
        monomer: ase.atoms.Atoms,
        diff_st: ase.atoms.Atoms,
        tran: np.float64,
    ) -> bool:
        """

        Args:
            monomer: monomer candidates
            diff_st: diff_st + monomer = primitive cell
            tran: the translational distance of monomer candidates

        Returns: judge if the mirror symmetry exist

        """
        for itp1, itp2 in itertools.combinations_with_replacement(
            range(len(monomer)), 2
        ):
            s1, s2 = monomer[itp1], diff_st[itp2]

            if (
                s1.number == s2.number
                and (s1.position[2] + tran - s2.position[2]) < self._symprec
            ):
                normal = s1.position - s2.position
                normal[2] = 0
                op = SymmOp.reflection(normal)

                itp = []
                for site in monomer:
                    coord = op.operate(site.position) + np.array([0, 0, tran])
                    tmp = find_in_coord_list(
                        diff_st.positions, coord, self._symprec
                    )
                    itp.append(
                        len(tmp) == 1
                        and diff_st.numbers[tmp[0]] == site.number
                    )
                if np.array(itp).all():
                    return True
        return False

    def _get_monomer_ind(
        self, z: np.ndarray, z_uniq: np.ndarray
    ) -> [list, list]:
        monomer_ind = [np.where(z == tmp)[0] for tmp in z_uniq]
        monomer_ind_sum = []
        tmp1 = np.array([])
        for tmp in monomer_ind:
            tmp1 = np.sort(np.append(tmp1, tmp)).astype(np.int32)
            monomer_ind_sum.append(tmp1)
        return monomer_ind, monomer_ind_sum

    def _potential_translation(self) -> [list, list]:
        """generate the potential monomer and the scaled translational distance in z axis

        Returns: possible monomers and translational distances

        """
        z = self._primitive.get_scaled_positions()[:, 2]
        z_uniq, counts = np.unique(z, return_counts=True)
        potential_trans = np.append((z_uniq - z_uniq[0])[1:], 1)
        monomer_ind, monomer_ind_sum = self._get_monomer_ind(z, z_uniq)

        translation, monomer = [], []
        for ii in range(len(z_uniq)):
            monomer_num = counts[: ii + 1].sum()
            # check the atomic number and layer number of potential monomer
            # check the translational distance whether correspond to the layer numbers
            if (
                len(self._primitive) % monomer_num == 0
                and len(z_uniq) % (ii + 1) == 0
                and abs(len(z_uniq) / (ii + 1) - 1 / potential_trans[ii])
                < self._symprec
            ):

                if len(self._primitive) == monomer_num:
                    # if the monomer is the whole structure
                    monomer.append(self._primitive)
                    translation.append(1)
                else:
                    monomer.append(self._primitive[monomer_ind_sum[ii]])
                    translation.append(potential_trans[ii])
        return monomer, translation

    def _find_primitive(self) -> ase.atoms.Atoms:
        """fine the primitive cell of line group structure

        Returns: primitive cell

        """
        x_y = self._atom.get_scaled_positions()[:, :2]
        z = self._atom.get_scaled_positions()[:, 2]

        ind = find_in_coord_list(x_y[1:], x_y[0], atol=self._symprec) + 1

        if len(ind) == 0:
            return self._atom
        else:
            potential_z = z[ind] - z[0]

            trans_z = []
            for tmp in potential_z:
                v = np.array([0, 0, tmp])
                pos1, num1 = refine_cell(
                    self._atom.get_scaled_positions() + v,
                    self._atom.numbers,
                    symprec=self._round_symprec,
                )
                pos2, num2 = refine_cell(
                    self._atom.get_scaled_positions(),
                    self._atom.numbers,
                    symprec=self._round_symprec,
                )
                if (abs(pos1 - pos2) < self._symprec).all() and (
                    num1 == num2
                ).all():
                    trans_z.append(tmp)
            if len(trans_z) == 0:
                return self._atom
            else:
                pure_z = min(trans_z)
                itp = np.where(z < pure_z - self._symprec)[0]
                cell = np.array(
                    [
                        self._atom.cell[0].copy(),
                        self._atom.cell[1].copy(),
                        [0, 0, pure_z * self._atom.cell[2, 2]],
                    ]
                )
                numbers = self._atom.numbers[itp]
                pos = self._atom.positions[itp]
                atom = Atoms(cell=cell, numbers=numbers, positions=pos)
                return atom

    def get_cyclic_group(self) -> [list, list]:
        """Returns a PointGroup object for the molecule."""
        return self.cyclic_group, self.monomers


def main():
    parser = argparse.ArgumentParser(
        description="Try to detect the generalized translational group of a line group structure"
    )
    parser.add_argument(
        "filename", help="path to the file from which coordinates will be read"
    )

    args = parser.parse_args()

    st_name = args.filename
    st = read(st_name)

    cyclic = CyclicGroupAnalyzer(st)
    cy, mon = cyclic.get_cyclic_group()

    for ii, cg in enumerate(cy):
        print(cg + "  " + str(mon[ii].symbols))


if __name__ == "__main__":
    main()
