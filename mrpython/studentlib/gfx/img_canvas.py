from tkinter import *

CANVAS_DEFAULT_RATIO = 4.0 / 4.0

# a subclass of Canvas for dealing with resizing of windows
class ImgCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        if 'ratio' in kwargs:
            self.ratio = kwargs['ratio']
        else:
            self.ratio = CANVAS_DEFAULT_RATIO
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height

        ewidth = float(event.width)
        eheight = float(event.height)

        canvas_ratio = ewidth / eheight
        if canvas_ratio > self.ratio:
            ewidth = eheight * self.ratio
        else:
            eheight = ewidth / self.ratio

        wscale = float(ewidth)/self.width
        hscale = float(eheight)/self.height
        self.width = ewidth
        self.height = eheight

        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)

    def x(self, x):
        return int(((x + 1.0) / 2.0) * float(self.width))

    def y(self, y):
        return int(float(self.height) - ((y + 1.0) / 2.0) * float(self.height))

    def draw_line(self, x0, y0, x1, y1, color):
        self.create_line(self.x(x0), self.y(y0), self.x(x1), self.y(y1), fill=color)

    def fill_triangle(self, x1, y1, x2, y2, x3, y3, color):
        self.create_polygon((self.x(x1), self.y(y1),
                             self.x(x2), self.y(y2),
                             self.x(x3), self.y(y3)),
                            fill=color)

    def fill_ellipse(self, x1, y1, x2, y2, color):
        self.create_oval((self.x(x1), self.y(y1),
                          self.x(x2), self.y(y2)),
                         fill=color)

    def draw_ellipse(self, x1, y1, x2, y2, color):
        self.create_oval((self.x(x1), self.y(y1),
                          self.x(x2), self.y(y2)),
                         fill='',
                         outline=color)


    def draw_image(self, image):
        for elem in image.objects:
            if elem[0] == "draw-line":
                self.draw_line(elem[1], elem[2], elem[3], elem[4], elem[5])
            elif elem[0] == "draw-triangle":
                x1, y1, x2, y2, x3, y3, color = elem[1:]
                self.draw_line(x1, y1, x2, y2, color)
                self.draw_line(x2, y2, x3, y3, color)
                self.draw_line(x3, y3, x1, y1, color)
            elif elem[0] == 'fill-triangle':
                x1, y1, x2, y2, x3, y3, color = elem[1:]
                self.fill_triangle(x1, y1, x2, y2, x3, y3, color)
            elif elem[0] == 'fill-ellipse':
                x1, y1, x2, y2, color = elem[1:]
                self.fill_ellipse(x1, y1, x2, y2, color)
            elif elem[0] == 'draw-ellipse':
                x1, y1, x2, y2, color = elem[1:]
                self.draw_ellipse(x1, y1, x2, y2, color)
            elif elem[0] == 'empty-image':
                pass # nothing to do
            else:
                raise ValueError("Cannot draw image element: unsupported '{}' type (elem={})".format(elem[0], elem))


CANVAS_WIDGET = None

def show_image(img):
    global CANVAS_WIDGET
    if CANVAS_WIDGET:
        try:
            CANVAS_WIDGET.delete(ALL)
        except:
            CANVAS_WIDGET = None

    if not CANVAS_WIDGET:
        myTop = Toplevel(width=480, height=480)
        myTop.title("Image")
        myframe = Frame(myTop, width=480, height=480)
        myframe.pack(fill=BOTH, expand=YES)
        mycanvas = ImgCanvas(myframe,width=480, height=480, background="white", highlightthickness=0)
        mycanvas.pack(fill=BOTH, expand=YES, padx=8, pady=8)
        CANVAS_WIDGET = mycanvas
        CANVAS_WIDGET.update()


    # the frame around the draw area
    CANVAS_WIDGET.create_rectangle(0, 0, 480, 480)
    CANVAS_WIDGET.draw_image(img)
    CANVAS_WIDGET.addtag_all("all")

