def original(l):
    ''' Appends something to l'''
    print(type(l))
    l.append(1)
    return l

print(type(original([])))
# def changed(l):
#     # recurse on each element of list
#     if l is list:
#         l = ListWrapper(l)
#         l[:] = map(ListWrapper.wrap_list, l)
#         l = ListWrapper(l)
#     l.append(1)
#     # Add before each return
#     l = list(l)
#     return l