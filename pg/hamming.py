from collections import defaultdict


def get_hamming_cs(pl):
    # number of control bits
    k = 0

    while 2 ** k < len(pl) + k + 1:
        # inserting control positions
        pl.insert(2 ** k - 1, "_")
        k += 1

    checksum_dict = defaultdict(int)

    for i, v in reversed(list(enumerate(pl))):

        if v == 1:
            c_b = list(bin(i + 1)[2:].zfill(4))

            for en, va in enumerate(c_b):
                checksum_dict[en] += int(va)

    return [v % 2 for k, v in checksum_dict.items()]


if __name__ == '__main__':
    payload = [1, 0, 0, 1, 1]

    checksum = get_hamming_cs(payload)

    print("cheksum", checksum)

    assert checksum == [1, 1, 0, 1]
