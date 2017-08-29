
import multiprocessing as mp

import tkinter as tk

def run_server(reply):
    
    print("[Server] started")
    
    req = reply.recv()
    print("[Server] received '{}'".format(req))

    window = tk.Tk()
    button = tk.Button(window, text=str(req), command=quit_server(reply))
    button.pack()
    
    window.mainloop()

def quit_server(reply):
    def callback():
        print("[Server] send 'quit'")
        reply.send('quit')
        print("[Server] wait for termination")

    return callback

