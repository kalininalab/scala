import os

import pytest

from scala.bqp.run import bqp_main


def run_identity_splitting(root_dir, out_folder, mode):
    bqp_main(
        input=f"{root_dir}/prot.tsv",
        output=f"{root_dir}/{out_folder}/",
        method="ilp",
        verbosity="I",
        weight_file=None,
        inter=f"{root_dir}/inter.tsv",
        drugs=f"{root_dir}/lig.tsv",
        splits=[0.7, 0.3],
        limit=0.05,
        drug_weights=None,
        technique=mode,
        prot_sim=None,
        drug_sim=None,
        header=None,
        sep="\t",
        names=["train", "test"],
        max_sec=-1,
        max_sol=-1,
    )


@pytest.mark.parametrize("root_dir", ["data/perf_7_3", "data/perf_70_30"])
@pytest.mark.parametrize("mode", [("R", "random"), ("ICD", "id_cold_drug"), ("ICP", "id_cold_protein")])
def test_perf_bin(root_dir, mode):
    def read_tsv(filepath):
        assert os.path.exists(filepath)
        with open(filepath, "r") as d:
            mols = [line.strip().split("\t") for line in d.readlines()]
        os.remove(filepath)
        return mols

    run_identity_splitting(root_dir, mode[1], mode[0])

    inter = read_tsv(f"{root_dir}/{mode[1]}/inter.tsv")

    """if mode[0] == "ICD":
        molecules = read_tsv(f"{root_dir}/{mode[1]}/drugs.tsv")
    elif mode[0] == "ICP":
        molecules = read_tsv(f"{root_dir}/{mode[1]}/proteins.tsv")
    else:
        molecules = None"""

    _, _, splits = list(zip(*inter))
    trains, tests = splits.count("train"), splits.count("test")
    train_frac, test_frac = trains / (trains + tests), tests / (trains + tests)
    assert 0.7 * 0.95 <= train_frac <= 0.7 * 1.05
    assert 0.3 * 0.95 <= test_frac <= 0.3 * 1.05
