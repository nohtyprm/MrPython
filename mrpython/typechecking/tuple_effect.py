def bad_function(L):
    '''list[int] -> int'''

    #e : tuple[list[int],int]
    e = (L,1)
    a,b = e
    a.append(7)
    while a==2:
        print("hi")
    if a==2:
        return 0

    print("helloe")

assert bad_function(([1,2])) == 0
assert bad_function([3,2,1]) == 0
