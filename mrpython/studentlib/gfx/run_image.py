from tkinter import *

from img_canvas import ImgCanvas

def main():
    root = Tk()
    myframe = Frame(root, width=580, height=320)
    myframe.pack(fill=BOTH, expand=YES)
    mycanvas = ImgCanvas(myframe,width=580, height=320, background="white", highlightthickness=0)
    mycanvas.pack(fill=BOTH, expand=YES, padx=8, pady=8)

    fname = None
    if len(sys.argv) > 1:
        fname = sys.argv[1]

    # the frame around the draw area
    mycanvas.create_rectangle(0, 0, 580, 320)

    import image
    if fname is not None:
        img = image.Image()
        with open(fname, 'rt') as f:
            img = image.image_from_json(f)
        mycanvas.draw_image(img)
    else:

        # add some widgets to the canvas
        mycanvas.draw_line(-1.0, 1.0, 1.0, -1.0, "blue")

    # tag all of the drawn widgets
    mycanvas.addtag_all("all")
    root.mainloop()

if __name__ == "__main__":
    main()
