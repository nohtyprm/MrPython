
def filled_rectangle(x, y, largeur, hauteur, couleur):
    """ float * float * float * float * str -> Image
        Hypothèse: (largeur > 0.0) and (hauteur > 0.0)

        Retourne l'image d'un rectangle au coin bas
        gauche en (x,y) et de la largeur et hauteur
        spécifiées.
    """

    return overlay(filled_triangle(x, y, x + largeur, y, x + largeur, y + hauteur, couleur),
                   filled_triangle(x + largeur, y + hauteur, x, y + hauteur, x, y, couleur))


def pyramide(x, y, largeur_min, largeur_max, hauteur, nb_etages, couleur):
    """  float * float * float * float * float * int * str -> Image
       Hypothèse: (largeur_min > 0.0) and (largeur_max > largeur_min) and (hauteur > 0.0)
       Hypothèse: nb_etages > 0

       Retourne un monument égyptien bien dimensionné.
    """

    # x_incr : float (incrément en x à chaque étape)
    x_incr = ((largeur_max - largeur_min) / nb_etages)  / 2.0

    # y_incr : float (incrément en y à chaque étape)
    y_incr = hauteur / nb_etages

    # x_courant : float
    x_courant = x

    # y_courant : float
    y_courant = y

    # l_courant : float
    l_courant = largeur_max

    # img : Image
    img = empty_image()

    # i : int (etage)
    for i in range(nb_etages):
        img = overlay(img,
                      filled_rectangle(x_courant, y_courant, l_courant, y_incr, couleur))
        x_courant = x_courant + x_incr
        y_courant = y_courant + y_incr
        l_courant = l_courant - 2 * x_incr

    return img

#r1 = filled_rectangle (-0.5, -0.5, 0.8, 0.6, "black")
#show_image(r1)

pyra = pyramide(-0.5, -0.5, 0.2, 1.2, 1.4, 32, "blue")
#print(pyra)
show_image(pyra)
                      

           
