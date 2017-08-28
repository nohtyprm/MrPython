
import multiprocessing as mp

import time

import MPServer




if __name__ == "__main__":
    #mp.set_start_method('fork')
    
    print("Start client")

    request, reply = mp.Pipe()
    serv = mp.Process(target=MPServer.run_server, args=(reply,))
    serv.start()
    print("[Client] launched server")

    #time.sleep(3)
    print("[Client] send 'test'")
    request.send("test")
    
    serv.join()
    print("Stop client")

    
