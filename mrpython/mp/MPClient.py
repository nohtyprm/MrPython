
import multiprocessing as mp

import time

import MPServer

if __name__ == "__main__":
    #mp.set_start_method('fork')
    
    print("[Client] start")

    request, reply = mp.Pipe()
    serv = mp.Process(target=MPServer.run_server, args=(reply,))
    serv.start()
    print("[Client] launched server")

    #time.sleep(3)
    print("[Client] send 'test'")
    request.send("test")

    print("[Client] wait loop")
    avail = False
    while not avail:
        print("[Client] wait 1 second")
        avail = request.poll(1)

    msg = request.recv()
    print("[Client] receives '{}'".format(msg))
    print("[Client] terminates server")
    serv.terminate() 
    serv.join()
    print("[Client] stop")

    
