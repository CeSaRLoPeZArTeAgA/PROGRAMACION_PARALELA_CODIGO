import requests
import time

from threading import Thread

all_characters = []
cadena = "Hola"
def get_characters_by_page(x):
    global cadena
    cadena = cadena + str(x)
    print(cadena+"\n")
    

def get_characters_parallel():
    request_threads = {}
    for page in range(5):
        request_threads[page] = Thread(target=get_characters_by_page, kwargs={'x':page})
        request_threads[page].start()
        
    for page in range(5):        
        request_threads[page].join()

if __name__ == '__main__':    
    get_characters_parallel()    
    
