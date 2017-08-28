
import multiprocessing as mp


def run_server(reply):
    print("Server started")

    req = reply.recv()
    print("[Server] received '{}'".format(req))
    
    print("Server exited")
