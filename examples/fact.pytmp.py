        """doc"""
        
        # r : Number
        r = 1
    else:
        raise Exception("preconditionError")

    # i : int
    i = 2

    while i <= n:
        r = r * i
        i = i + 1
        print("i="+str(i))

    return r

fact(10)



