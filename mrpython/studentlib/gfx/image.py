
import json

class Image:
    def __init__(self, _objects=tuple()):
        self.objects = _objects

    def __str__(self):
        return str(self.objects)

    def tojson(self, fileobj):
        json.dump(
            { "tag": "gfx_image"
              , "image" : self.objects
            }, fileobj)

def image_from_json(fileobj):
    js = json.load(fileobj)
    if "tag" not in js:
        raise ValueError("Not an image: missing 'tag' key")
    if js['tag'] != "gfx_image":
        raise ValueError(format("Not an image: wrong 'gfx_image' tag (was: '{}')", js['tag']))
    if "image" not in js:
        raise ValueError("Not an image: missing 'image' key")
    objects = ()
    for elem in js['image']:
        objects += ((tuple(elem)),)
    return Image(objects)

def draw_line(x0, y0, x1, y1, color="black"):
    # TODO: check arguments
    return Image((('draw-line', x0, y0, x1, y1, color),))

def draw_triangle(x0, y0, x1, y1, x2, y2, color="black"):
    # TODO: check arguments
    return Image((('draw-triangle', x0, y0, x1, y1, x2, y2, color),))

def fill_triangle(x0, y0, x1, y1, x2, y2, color="black"):
    # TODO: check arguments
    return Image((('fill-triangle', x0, y0, x1, y1, x2, y2, color),))

def draw_ellipse(x0, y0, x1, y1, color="black"):
    # TODO: check arguments
    return Image((('draw-ellipse', x0, y0, x1, y1, color),))

def fill_ellipse(x0, y0, x1, y1, color="black"):
    # TODO: check arguments
    return Image((('fill-ellipse', x0, y0, x1, y1, color),))

def overlay(*images):
    # TODO : check arguments
    objects = ()
    for img in images:
        objects += ((img.objects),)

    return Image(objects)

if __name__ == "__main__":

    img = overlay(draw_line(-1, -1, 1, 1)
                  ,draw_triangle(-1, 0, 0, 1, 1, 0)
                  ,fill_triangle(-0.5, 0.1, 0, 0.6, 0.5, 0.1, "blue")
                  ,fill_ellipse(-0.5, -0.2, 0.5, -0.6, "purple")
                  ,draw_ellipse(-0.8, -0.3, 0.8, -0.9, "red")
    )

    print("Source image:")
    print(img)

    import sys
    with open("img.json", 'wt') as f:
        img.tojson(f)

    img2 = None
    with open("img.json", 'rt') as f:
        img2 = image_from_json(f)
    print("Dest image:")
    print(img2)
