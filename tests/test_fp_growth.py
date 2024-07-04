from numpy.testing import assert_equal
import numpy as np
import fp_growth as fp

mock_header_table = {"z": 5, "r": 3, "x": 4, "y": 3, "s": 3, "t": 3}
mock_unsorted_transactions = np.array(
    [
        ["r", "z", "h", "j", "p"],
        ["z", "y", "x", "w", "v", "u", "t", "s"],
        ["z"],
        ["r", "x", "n", "o", "s"],
        ["y", "r", "x", "z", "q", "t", "p"],
        ["y", "z", "x", "e", "q", "s", "t", "m"],
    ],
    dtype=object,
)


def test_insert_transactions():
    tree = fp.FPTree(mock_header_table, 3)
    tree.insertTransactions(mock_unsorted_transactions)

    assert_equal(
        repr(tree),
        "root:1 -> z,x\nz:5 -> r,x\nr:1 -> \nx:3 -> y\ny:3 -> t\nt:3 -> s,r\ns:2 -> \nr:1 -> \nx:1 -> s\ns:1 -> r\nr:1 -> ",
    )


def test_get_freq_items():
    tree = fp.FPTree(mock_header_table, 3)
    tree.insertTransactions(mock_unsorted_transactions)
    freq_items = sorted(tree.get_freq_items())

    assert_equal(
        freq_items,
        sorted(
            [
                ["s", "x"],
                ["t", "y"],
                ["t", "x"],
                ["t", "z"],
                ["y", "x"],
                ["y", "z"],
                ["x", "z"],
                ["t", "x", "z"],
                ["t", "y", "x"],
                ["t", "y", "z"],
                ["y", "x", "z"],
                ["t", "y", "x", "z"],
            ]
        )
    )
