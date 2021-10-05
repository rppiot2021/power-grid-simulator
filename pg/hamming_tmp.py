from collections import defaultdict

control_counter = 1

payload = [1, 1, 0, 0, 1]
# todo undo reversing

# number of control bits
k = 0

while True:
    if 2**k >= len(payload) + k + 1:
        print("k", k)
        break

    # inserting control po
    payload.insert(2**k - 1, "_")
    k += 1

print(payload, "\n")

checksum_dict = defaultdict(int)
checksum_matrix = []
index = 0

for i, d in enumerate(payload):

    if d == 1:
        c_b = list(bin(len(payload) - i)[2:].zfill(4))

        for en, v in enumerate(c_b):
            checksum_dict[en] += int(v)

    elif d == "_":
        checksum_matrix.append(0 if checksum_dict[index] % 2 != 0 else 1)
        index += 1

print(checksum_dict)

print("index", checksum_matrix)

print("\nchecksum matrix", checksum_matrix)

assert checksum_matrix == [1, 1, 0, 1]
