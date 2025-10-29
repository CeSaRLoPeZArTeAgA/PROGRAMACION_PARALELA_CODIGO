from multiprocessing import Queue

# create queue
q = Queue()

# add elements
q.put(1) # 1
q.put(2) # 2 1
q.put(3) # 3 2 1
q.put(4) # 4 3 2 1

# now q looks like this:
# back --> 3 2 1 --> front

# get and remove first element
first = q.get() # --> 1
print(first)
if q.empty():
    print("Esta vacia1")

# q looks like this:
# back --> 3 2 --> front
second = q.get() # --> 2
print(second)
if q.empty():
    print("Esta vacia2")


tercero = q.get() # --> 3
print(tercero)
if q.empty():
    print("Esta vacia3")

cuarto = q.get() # --> 
print(cuarto)
if q.empty():
    print("Esta vacia4")



