from multiprocessing import Pool 

def cube(number):
    return number * number * number


if __name__ == "__main__":
    numbers = range(10)#[0,1,2,3,4,5,6,7,8,9]

    p = Pool()

    # by default this allocates the maximum number of available 
    # processors for this task --> os.cpu_count()
    result = p.map(cube,  numbers)

    # or 
    # result = [p.apply(cube, args=(i,)) for i in numbers]

    p.close()
    p.join()

    print(result)
