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

# calculate where to insert chcecksums
to_inser = []
for i in range(10):

    if i == control_counter:
        control_counter *= 2
        # print(i)
        to_inser.append(i)

# print(to_inser)

# insert into starting list
for i in to_inser:

    payload.insert(i -1, "_")


print(payload[::-1])





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