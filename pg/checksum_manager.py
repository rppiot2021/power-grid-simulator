from collections import defaultdict


def get_hamming_cs(pl: list) -> list:
    """
    create hamming checksum for given list

    :param pl: payload
    :return: checksum
    """

    c_pl = pl[::]
    # number of control bits
    k = 0

    while 2 ** k < len(c_pl) + k + 1:
        # inserting control positions
        c_pl.insert(2 ** k - 1, "_")
        k += 1

    checksum_dict = defaultdict(int)

    for i, v in reversed(list(enumerate(c_pl))):

        if v == 1:
            c_b = list(bin(i + 1)[2:].zfill(4))

            for en, va in enumerate(c_b):
                checksum_dict[en] += int(va)

    return [v % 2 for k, v in checksum_dict.items()]


def get_control_b(pl: list) -> int:
    """
    create control value for given list

    :param pl: payload
    :return: checksum
    """

    return sum(pl) % 2


def get_wrapped_payload(pl: list) -> list:
    """
    create list which consist of payload and checksum (hamming + control value)

    :param pl: payload
    :return: payload + checksum
    """

    checksum = get_hamming_cs(pl)

    print("checksum", checksum)

    wrapped_payload = pl + checksum

    c_b = get_control_b(wrapped_payload)

    print("control b", c_b)

    return wrapped_payload + [c_b]


if __name__ == '__main__':
    payload = [1, 0, 0, 1, 1]

    print(get_wrapped_payload(payload))
