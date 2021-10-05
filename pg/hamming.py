from collections import defaultdict

control_counter = 1

payload = [1, 1, 0, 0, 1]
# todo undo reversing
payload = [1, 0, 0, 1, 1]

# number of control bits
k = 0

while 2**k < len(payload) + k + 1:

    # inserting control po
    payload.insert(2**k - 1, "_")
    k += 1

print(payload[::-1], "\n")

checksum_dict = defaultdict(int)
result = []
index = 0

for i, d in enumerate(payload[::-1]):

    if d == 1:
        c_b = list(bin(len(payload) - i)[2:].zfill(4))
        print(c_b)
        print([
            bool(int(i)) for i in c_b
        ])

        for en, v in enumerate[bool(int(i)) for i in c_b]:
            checksum_dict[en] = not v

        # for en, v in enumerate(c_b):
        #     checksum_dict[en] += int(v)

print(checksum_dict)

t = [0 if v%2==0 else 1 for k,v in checksum_dict.items()]
# print(t)

checksum_matrix = t

print("\nchecksum matrix", checksum_matrix)

assert checksum_matrix == [1, 1, 0, 1]
