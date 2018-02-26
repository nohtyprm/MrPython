
def sablier (x, y, l, h) :
    """ float * float * float * float -> Image
        Hypothèse : l et h sont positives
        
        sablier(x, y, l, h) dessine un sablier dont (x, y) est le point bas
        gauche, l est la largeur et h la hauteur.
    """

    return overlay(
        fill_triangle(x, y, x + l / 2, y + h / 2, x + l, y),
        fill_triangle(x + l / 2, y + h / 2, x, y + h, x + l, y + h))

#show_image(sablier(-0.3, -0.8, 0.6, 1.6)) 

#show_image(sablier(-0.2, 0, 0.4, 1.0)) 
                   
show_image(sablier(-0.4, -0.4, 0.8, 0.8))
