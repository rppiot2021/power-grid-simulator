payload = "11001"

control_counter = 1

inserted = []

"""
43210
11001
11 11
 11 1
 111 
1


987654321
1_100_1__
1 1 1 1 1
  11  11
  1111
11



"""


def reverse_print(l):
    print(l.reverse())


payload = [1, 1, 0, 0, 1]
# todo undo reversing
payload = [1, 0, 0, 1, 1]

# calculate where to insert chcecksums
to_inser = []
for i in range(10):

    if i == control_counter:
        control_counter *= 2
        to_inser.append(i)


# insert into starting list
for i in to_inser:

    payload.insert(i - 1, "_")

print(payload[::-1])

working_matrix = []

# print binary repr
for i, d in enumerate(payload):

    #
    # create binary representation list
    context_b = list(bin(i+1)[2:].zfill(len(to_inser)))

    print(i +1,d, context_b)
    if d in [ 0, "_"]:
        continue
    working_matrix.append(context_b)


print("___")

checksum_matrix = []

k = 0
for i, d in enumerate(payload):

    # todo reverse again
    if d == "_":
        print("calcuting", [t for t in working_matrix ])
        print("calcuting", [t[k] for t in working_matrix])

        s = sum([int(t[k]) for t in working_matrix])
        print(s)

        if s % 2 == 0:
            print("no add")
            checksum_matrix.append(0)
        else:
            print("add")
            checksum_matrix.append(1)


        k += 1

print("checksum matrix", checksum_matrix)


# insert into starting matrix

print(payload)
print(payload.index("_"))
#

t = payload[::-1]
print("before",t )

for i in checksum_matrix:
    t[t.index("_")] = i


print(t)
# print()
# print("---")
# [print(i) for i in working_matrix]





#
# payload_i = 0
# inserted.append("_")
# while True:
#
#     try:
#         data = t[payload_i]
#         # data = payload.split()[payload_i]
#     except IndexError:
#         break
#
#     print(payload_i)
#
#     if (payload_i + 1) % 2 == 0:
#         inserted.append("_")
#         print("tu", payload_i + 1)
#
#     else:
#         inserted.append(data)
#
#     payload_i += 1
#
# print(inserted)

#
#
#
# for i, d in enumerate(payload):
#     print(i, d)
#     # print(bin(i+1)[2:])
#
#     print("control counter", control_counter)
#
#     if control_counter == i:
#         inserted.append("-")
#         control_counter *= 2
#
#     # else:
#     inserted.append(d)
#
# print(inserted)