from collections import defaultdict


# todo error correction


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

    wrapped_payload = pl + checksum

    c_b = get_control_b(wrapped_payload)

    return wrapped_payload + [c_b]


def check_payload(c_pl: list) -> bool:
    """
    check if payload is corrupted

    :param c_pl: payload
    :return: is corrupted
    """

    pl = c_pl[::]

    c_b = pl.pop()

    if not c_b == get_control_b(pl):
        return False

    # number of control bits
    k = 1
    pl_len = 1
    true_len = len(pl)

    while not (k + pl_len == true_len):
        pl_len += 1

        k = 0
        while 2 ** k < pl_len + k + 1:
            k += 1

    received_pl = pl[:k + 1]
    received_hamm_cs = pl[-k:]

    return received_hamm_cs == get_hamming_cs(received_pl)


def main():
    payload = [1, 0, 0, 1, 1]

    wrapped_payload = get_wrapped_payload(payload)
    print("wrapped payload", wrapped_payload)

    # test control value
    # t = wrapped_payload.pop()
    # wrapped_payload = wrapped_payload + [1 if t == 0 else 1]

    t = check_payload(wrapped_payload)

    print(t)


if __name__ == '__main__':
    main()
