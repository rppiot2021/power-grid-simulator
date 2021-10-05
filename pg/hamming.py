from collections import defaultdict

control_counter = 1

payload = [1, 1, 0, 0, 1]
# todo undo reversing
payload = [1, 0, 0, 1, 1]

k = 0
ins = []

while True:
    if 2**k >= len(payload) + k + 1:
        print("found k", k)
        break

    ins.append(2**k)
    k+=1


print("ins", ins)

# l = 1
# for i in range(k):
#     print(l)
#     l *= 2


# calculate where to insert chcecksums
to_inser = []
for i in range(10):

    if i == control_counter:
        control_counter *= 2
        to_inser.append(i)

print(to_inser)
# insert into starting list
for i in to_inser:

    payload.insert(i - 1, "_")

print(payload[::-1])

working_matrix = []

len_to_ins = len(to_inser)

working_dict = defaultdict(int)

# print binary repr
for i, d in enumerate(payload):

    # create binary representation list

    c_b = list(bin(i + 1)[2:])
    print(i +1,d, "".join(c_b).zfill(len_to_ins))

    if d in [ 0, "_"]:
        continue

    for en, v in enumerate(c_b[::-1]):
       working_dict[en] += int(v)


print("___")

[print(i) for i in working_dict.items()]

checksum_matrix = []

for i, v in working_dict.items():
    checksum_matrix.append(0 if v % 2 == 0 else 1)

print(checksum_matrix)

checksum_matrix = checksum_matrix[::-1]

print("checksum matrix", checksum_matrix)

assert checksum_matrix == [1, 1, 0, 1]
