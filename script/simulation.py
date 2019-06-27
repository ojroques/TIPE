# coding=utf-8

"""
Étude et modélisation d'un système proie-prédateur par un automate cellulaire
Author: Olivier Roques
Date: 2015 - 2016
"""

from tkinter import *
from random import randint, choice
from time import clock
import matplotlib.pyplot as plt
import numpy as np
import pickle #Permet d’enregistrer des données avec conservation de leur type
#Module donnant accès aux fenêtres de recherche de fichiers:
from tkinter.filedialog import asksaveasfile, askopenfile


class ProiePredateur(Frame):
    """La classe principale de la simulation proie prédateur et ses méthodes."""
    def __init__(self, master):
        Frame.__init__(self, master)

        self.width       = 660                 #Largeur du canevas
        self.height      = 540                 #Hauteur du canevas
        self.xmax = self.width  // 12          #Nombre de case en largeur
        self.ymax = self.height // 12          #Nombre de case en hauteur
        #Vitesse par defaut de la simulation, en ms:
        self.vitesse     = 200
        self.coul_fond   = "#87D37C"           #Couleur du fond
        #Couleur des proies/prédateurs respectivement:
        self.coul_cel    = ["#EEEEEE", "#D35400"]
        #Couleur des lignes de séparation
        self.coul_lignes = "#68C3A3"
        self.coul_milieu = "#336E7B"           #Couleur des obstacles
        #Variable de contrôle: simulation active (=1) ou non:
        self.flag = 0
        self.proie_cfg = 4                     #Age de reproduction des proies
        #Age de reprod/Age de famine des prédateurs respectivement:
        self.predat_cfg = [7, 10]
        #Chance qu'a le prédateur de capturer sa proie:
        self.chance_capture = 100

        #Liste contenant les icônes des boutons de contrôle
        self.img = [PhotoImage(file="icones/play.gif"),
                    PhotoImage(file="icones/pause.gif"),
                    PhotoImage(file="icones/stop.gif")]

        #Espace de la simulation
        self.can = Canvas(self, width=self.width, height=self.height,
            bg=self.coul_lignes, bd=1, relief=RIDGE)
        self.can.grid(row=0, column=0)

        #Cadre des informations et du contrôle de la simulation (= cadre_info)
        cadre_info = Frame(self, bd=2, relief=GROOVE)
        cadre_info.grid(row=1, column=0, pady=3, padx=3, sticky=EW)

        #Informations sur la génération et les populations (dans cadre_info)
        self.showgen = Label(cadre_info, font="Arial 11")
        self.showgen.pack(side=LEFT, padx=5, pady=2)
        self.showproie = Label(cadre_info, font="Arial 11")
        self.showproie.pack(side=LEFT, padx=40, pady=2)
        self.showpredat = Label(cadre_info, font="Arial 11")
        self.showpredat.pack(side=LEFT, padx=5, pady=2)

        #Boutons de contrôle (cadre_info)
        Button(cadre_info, image=self.img[2], command=self.nouv_grille)\
            .pack(side=RIGHT, padx=2, pady=2) #Nouvelle simulation
        self.bout_play = Button(cadre_info)
        self.bout_play.pack(side=RIGHT, padx=2, pady=2)         #Start


        #Cadre des paramètres (= cadre_config)
        cadre_config = Frame(self, bd=2, relief=GROOVE)
        cadre_config.grid(row=0, column=1, pady=3, padx=3, sticky=NS)
            #Le titre est cliquable et affiche les crédits et le fonctionnement
        Button(cadre_config, text="Simulation Proie-Prédateur", font="Arial 14",
            command=self.credits, bd=2, relief=SOLID)\
            .grid(row=0, column=0, columnspan=6, padx=3, pady=4, sticky=EW)

        #Curseur de choix de la vitesse (cadre_config)
        curseur_vit = Scale(cadre_config, orient=HORIZONTAL, troughcolor="#DADFE1",
            label="Vitesse (en ms):", from_=200, to=2000,\
            command=lambda x: self.change_param(0, x), resolution = 10)
        curseur_vit.grid(row=1, column=0, columnspan=6, padx=3, sticky=EW)
        curseur_vit.set(self.vitesse)

        #Répartition aléatoire (cadre_config)
        Label(cadre_config, text="Répartition aléatoire (pop. maximale: {}):"
            .format(self.xmax*self.ymax))\
            .grid(row=2, column=0, columnspan=6, padx=3, pady=5, sticky=W)
        self.nb_proie = Entry(cadre_config, bd=2, relief=GROOVE)
        self.nb_proie.grid(row=3, column=0, columnspan=3, padx=3, sticky=EW)
        self.nb_predat = Entry(cadre_config, bd=2, relief=GROOVE)
        self.nb_predat.grid(row=3, column=3, columnspan=3, padx=3, sticky=EW)
        self.nb_proie.insert(0, "nb de proies")
        self.nb_predat.insert(0, "nb de prédateurs")
        Button(cadre_config, text="Générer", command=self.pop_aleatoire)\
            .grid(row=4, column=0, columnspan=6, padx=3, pady=3, sticky=EW)

        #Curseur de choix des paramètres
        curseur_proiecfg = Scale(cadre_config, orient=HORIZONTAL,\
            troughcolor="#DADFE1", label="Âge de reproduction des proies:",\
            from_=1, to=20, command=lambda x: self.change_param(1, x))
        curseur_proiecfg.grid(row=5, column=0, columnspan=6, padx=3, sticky=EW)
        curseur_proiecfg.set(self.proie_cfg)
        curseur_predatcfg1 = Scale(cadre_config, orient=HORIZONTAL,\
            troughcolor="#DADFE1", label="Âge de reproduction des prédateurs:",\
            from_=1, to=20, command=lambda x: self.change_param(2, x))
        curseur_predatcfg1.grid(row=6, column=0, columnspan=6, padx=3, sticky=EW)
        curseur_predatcfg1.set(self.predat_cfg[0])
        curseur_predatcfg2 = Scale(cadre_config, orient=HORIZONTAL,\
            troughcolor="#DADFE1", label="Famine des prédateurs:",\
            from_=1, to=20, command=lambda x: self.change_param(3, x))
        curseur_predatcfg2.grid(row=7, column=0, columnspan=6, padx=3, sticky=EW)
        curseur_predatcfg2.set(self.predat_cfg[1])
        curseur_chance = Scale(cadre_config, orient=HORIZONTAL,\
            troughcolor="#DADFE1", label="Chance de capture des prédateurs (en %):",\
            from_=0, to=100, command=lambda x: self.change_param(4, x))
        curseur_chance.grid(row=8, column=0, columnspan=6, padx=3, sticky=EW)
        curseur_chance.set(self.chance_capture)

        #Boutons d'import/export de motifs (cadre_config)
        Label(cadre_config, text="Ouvrir/Enregistrer une répartition:")\
            .grid(row=9, column=0, columnspan=6, padx=3, pady=5, sticky=W)
        Button(cadre_config, text="Ouvrir", command=self.import_motif)\
            .grid(row=10, column=0, columnspan=3, padx=3, sticky=EW)
        Button(cadre_config, text="Enregistrer", command=self.save_motif)\
            .grid(row=10, column=3, columnspan=3, padx=3, sticky=EW)

        #Boutons d'affichage des graphiques (cadre_config)
        Label(cadre_config, text="Graphe:")\
            .grid(row=11, column=0, columnspan=6, padx=3, pady=5, sticky=W)
        Button(cadre_config, text="Afficher", command=self.affiche_graphes)\
            .grid(row=12, column=0, columnspan=6, padx=3, sticky=EW)

        #Bouton de création d'obstacles (cadre_config)
        self.cm = IntVar()
        Checkbutton(cadre_config, text="Création d'obstacles",\
            variable = self.cm, command=self.creer_obstacle)\
            .grid(row=13, column=0, columnspan=6, padx=3, pady=8, sticky=W)


        #Attribution des actions d'un clic de souris
        self.can.bind("<Button-2>", self.coord_mort)
        self.can.bind("<B2-Motion>", self.coord_mort)
        self.creer_obstacle()

        #Bouton d'arrêt du programme
        Button(self, text="Quitter", command=self.master.destroy)\
                     .grid(row=1, column=1, padx=6, pady=2, sticky=E)

        self.nouv_grille() #Démarre une nouvelle simulation

    def creer_obstacle(self):
        "Affecte une action à chaque bouton de la souris, selon si la case \
        de creation d'obstacles est cochée ou non."
        #Si la case n'est pas cochée, le clic gauche donne naissance à une proie:
        if not (self.cm.get()):
            self.can.bind("<Button-1>", self.coord_proie)
            self.can.bind("<Button-3>", self.coord_predat)
            self.can.bind("<B1-Motion>", self.coord_proie)
            self.can.bind("<B3-Motion>", self.coord_predat)
        #Si elle est cochée, le clic gauche fait apparaître une case obstacle:
        else:
            self.can.unbind("<Button-3>")
            self.can.unbind("<B3-Motion>")
            self.can.bind("<Button-1>", self.coord_obstacle)
            self.can.bind("<B1-Motion>", self.coord_obstacle)

    def nouv_grille(self):
        "Affiche l'espace de simulation et initialise les variables."
        #Permet d'éviter une itération en trop lorsqu'une simulation est en cours
        if self.flag:
            self.flag = 0
            self.after(self.vitesse, self.nouv_grille)
            return

        self.change_bouton(1)       #Affichage du bouton Play
        self.can.delete(ALL)        #Efface le canevas

        #Initialisation des variables:

        self.generation = 0         #Compteur de génération
        #Tableau contenant respectivement le nombre de proies et
        #le nombre de prédateurs actuel:
        self.pop = [0, 0]

        #Tableau contenant les populations à chaque génération
        #(cet historique est utile lors du tracé de graphes)
        self.evol_pop =([], [])

        #Tableau des proies contenant pour chaque coordonnées
        #l'âge de la proie (> 0 ou 0 si pas de proie):
        self.grille_proie = np.zeros( (self.xmax, self.ymax), dtype = np.int8)
        #Pareil pour les prédateurs:
        self.grille_predat = np.zeros( (self.xmax, self.ymax), dtype = np.int8)
        #Tableau contenant la 'faim' actuelle du prédateur
        self.grille_predatfaim = np.zeros( (self.xmax, self.ymax), dtype = np.int8)
        #Tableau repérant les cases vivantes, d'obstacles et vides (-1):
        self.grille_vie = np.zeros( (self.xmax, self.ymax), dtype = np.int8)
        #Tableau contenant les cases en elles-mêmes:
        self.grille_items = np.empty( (self.xmax, self.ymax), dtype = np.object)

        #Créer les cellules et les place dans grille_items
        for x in range(self.xmax):
            for y in range(self.ymax):
                self.grille_items[x, y] = self.can.create_rectangle(x*12+3, y*12+3,
                x*12+15, y*12+15, fill=self.coul_fond, outline=self.coul_lignes)

        #On initialise l'affiche de la génération et des populations
        self.showgen.config(text="Géneration: {:5}".format(0))
        self.showproie.config(text="Proies: {:4}".format(0))
        self.showpredat.config(text="Prédateurs: {:4}".format(0))

    def change_param(self, n, x):
        "Récupere la valeur des curseurs pour changer les divers paramètres."
        if n == 0: self.vitesse        = int(x)
        if n == 1: self.proie_cfg      = int(x)
        if n == 2: self.predat_cfg[0]  = int(x)
        if n == 3: self.predat_cfg[1]  = int(x)
        if n == 4: self.chance_capture = int(x)

    def coord_obstacle(self, event):
        "Creé un obstacle à l'emplacement du clic."
        canvas_coord = event.widget
        #Coordonnée x du clic:
        x = int(canvas_coord.canvasx(event.x - (event.x%12))) // 12
        #Coordonnée y du clic:
        y = int(canvas_coord.canvasy(event.y - (event.y%12))) // 12
        #Teste le clic est dans le grille
        if 0 <= x < self.xmax and 0 <= y < self.ymax:
            #Tue l'éventuelle proie:
            if self.grille_proie[x, y]: self.tue_cellule(x, y, 1)
            if self.grille_predat[x, y]: self.tue_cellule(x, y, 2)  #Idem
            #On actualise alors le tableau repérant le contenu des cases:
            self.grille_vie[x, y] = -1
            self.can.itemconfigure(self.grille_items[x, y], fill=self.coul_milieu)

    def coord_proie(self, event):
        "Donne naissance à une proie à l'emplacement du clic."
        canvas_coord = event.widget
        x = int(canvas_coord.canvasx(event.x - (event.x%12))) // 12
        y = int(canvas_coord.canvasy(event.y - (event.y%12))) // 12
        if 0 <= x < self.xmax and 0 <= y < self.ymax\
            and not self.grille_proie[x, y]:
            if self.grille_vie[x, y] == -1: self.tue_cellule(x, y, 0)
            if self.grille_predat[x, y]: self.tue_cellule(x, y, 2)
            #Placement d'une proie avec un âge de reproduction aléatoire:
            self.proie_vie( x, y, randint(1, self.proie_cfg) )

    def coord_predat(self, event):
        "Donne naissance à un prédateur à l'emplacement du clic."
        canvas_coord = event.widget
        x = int(canvas_coord.canvasx(event.x - (event.x%12))) // 12
        y = int(canvas_coord.canvasy(event.y - (event.y%12))) // 12
        if 0 <= x < self.xmax and 0 <= y < self.ymax\
            and not self.grille_predat[x, y]:
            if self.grille_vie[x, y] == -1: self.tue_cellule(x, y, 0)
            if self.grille_proie[x, y]: self.tue_cellule(x, y, 1)
            self.predat_vie( x, y, randint(1, self.predat_cfg[0]),\
                randint(1, self.predat_cfg[1]))

    def coord_mort(self, event):
        "Supprime la proie ou le prédateur de la case selectionnée."
        canvas_coord = event.widget
        x = int(canvas_coord.canvasx(event.x - (event.x%12))) // 12
        y = int(canvas_coord.canvasy(event.y - (event.y%12))) // 12
        if 0 <= x < self.xmax and 0 <= y < self.ymax:
            if self.grille_proie[x, y]: self.tue_cellule(x, y, 1)
            if self.grille_predat[x, y]: self.tue_cellule(x, y, 2)
            if self.grille_vie[x, y] == -1: self.tue_cellule(x, y, 0)

    def proie_vie(self, x, y, reprod):
        "Donne naissance à une proie aux coord (x, y) d'âge 'reprod'."
        self.can.itemconfigure(self.grille_items[x, y], fill=self.coul_cel[0])
        self.grille_vie[x, y] = 1
        self.grille_proie[x, y] = reprod    #Actualise le tableau des proies
        self.pop[0] += 1                    #Actualise la population des proies
        self.showproie.config(text="Proies: {:4}".format(self.pop[0]))

    def predat_vie(self, x, y, reprod, faim):
        "Donne naissance à un prédateur aux coord (x, y), \
        d'age 'reprod' d'état de famine'faim'."
        self.can.itemconfigure(self.grille_items[x, y], fill=self.coul_cel[1])
        self.grille_vie[x, y] = 1
        self.grille_predat[x, y] = reprod
        #Actualise le tableau d'état de famine des prédateurs:
        self.grille_predatfaim[x, y] = faim
        self.pop[1] += 1
        self.showpredat.config(text="Prédateurs: {:4}".format( self.pop[1]))

    def tue_cellule(self, x, y, p):
        "Supprime la proie (p=1) ou le prédateur (p=2) aux coord (x, y)."
        self.can.itemconfigure(self.grille_items[x, y], fill=self.coul_fond)
        self.grille_vie[x, y] = 0
        if p == 1:  #Cas de la proie
            self.grille_proie[x, y] = 0
            self.pop[0] -= 1
            self.showproie.config(text="Proies: {:4}".format(self.pop[0]))
        if p == 2:  #Cas du prédateur
            self.grille_predat[x, y] = 0
            self.grille_predatfaim[x, y] = 0
            self.pop[1] -= 1
            self.showpredat.config(text="Prédateurs: {:4}".format(self.pop[1]))

    def cel_voisines_proie(self, x, y):
        "Retourne un tableau contenant les coord des cellules vides voisines\
         de la proie en (x, y)."
        v = []
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                #L'opération modulo permet de considérer la grille comme torique:
                x2, y2 = (x + j)%self.xmax, (y + i)%self.ymax
                if not self.grille_vie[x2, y2]: v.append((x2, y2))
        return v

    def cel_voisines_predat(self, x, y):
        "Retourne un doublet de tableaux contenant respectivement les cases vides\
         et les proies voisines du prédateur en (x,y)"
        v = ([], [])
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                x2, y2 = (x + j)%self.xmax, (y + i)%self.ymax
                if not self.grille_vie[x2, y2]: v[0].append((x2, y2))
                if self.grille_proie[x2, y2]: v[1].append((x2, y2))
        return v

    def animation(self):
        "Simule l'évolution des populations, en tenant compte des paramètres."
        t1 = clock()

        #On commence par parcourir les cases contenant les proies
        for x, y in np.transpose(np.nonzero(self.grille_proie)):
            #Récupère les cases vides adjacentes:
            v = self.cel_voisines_proie(x, y)
            if v != []:
                reprod = self.grille_proie[x, y]
                #La proie choisit une case au hasard vers laquelle se déplacer:
                x2, y2 = choice(v)
                if reprod >= self.proie_cfg: #Naissance d'une nouvelle proie
                    #'proie_vie' fait apparaître une proie aux coord fournies:
                    self.proie_vie(x2, y2, 1)
                    self.grille_proie[x, y] = 1
                else:
                    #Déplace la proie et incrémente sa variable interne:
                    self.proie_vie(x2, y2, reprod+1)
                    self.tue_cellule(x, y, 1)
            else: self.grille_proie[x, y] += 1

        #Puis on parcout les cases contenant les prédateurs
        for x, y in np.transpose(np.nonzero(self.grille_predat)):
            #v est un tuple de tableaux renvoyé 'par cel_voisines_predat':
            v = self.cel_voisines_predat(x, y)
            faim = self.grille_predatfaim[x, y]
            #Si le prédateur est affamé, on le tue:
            if faim >= self.predat_cfg[1]: self.tue_cellule(x, y, 2)
            elif v != ([], []):
                reprod = self.grille_predat[x, y]
                #Si il y a une proie à coté, et que le prédateur
                #réussit à l'attraper, il prendra sa place:
                if v[1] != [] and (randint(1, 100) <= self.chance_capture\
                    or v[0] == []):
                    x2, y2 = choice(v[1])
                    self.tue_cellule(x2, y2, 1)
                    faim = 0
                else: x2, y2 = choice(v[0]) #Sinon, déplacement vers une case vide:
                #Le prédateur peut donner naissance à une nouvelle proie:
                if reprod >= self.predat_cfg[0]:
                    self.predat_vie(x2, y2, 1, faim + 1)
                    self.grille_predat[x, y] = 1
                    self.grille_predatfaim[x, y] = faim + 1
                else: #Déplace le prédateur
                    self.predat_vie(x2, y2, reprod+1, faim+1)
                    self.tue_cellule(x, y, 2)
            else:
                self.grille_predat[x, y] += 1
                self.grille_predatfaim[x, y] += 1

        #La génération est incrementée de 1, puis on actualise l'affichage
        self.generation += 1
        self.showgen.config(text="Génération: {:4}".format(self.generation))
        #On ajoute les effectifs dans le tableau des relevés:
        self.evol_pop[0].append(self.pop[0])
        self.evol_pop[1].append(self.pop[1])

        #Rappelle la fonction d'animation après un certain temps 'vitesse' (en ms)
        if self.flag:
            t = int((clock()-t1)*1000)
            #On tient ici compte du délai provenant des tests précédents:
            if t < self.vitesse: self.after(self.vitesse - t, self.animation)
            else: self.after(0, self.animation)

    def start(self, event=None):
        "Démarrage de l'animation."
        #Evite de lancer la simulation lorsqu'une autre est en cours:
        if not self.flag:
            self.flag = 1           #Autorise la simulation
            self.animation()        #Appel de la fonction animant la simulation
            self.change_bouton(0)   #Change l'état du bouton play
            if self.generation == 0:
                self.evol_pop[0].append(self.pop[0])
                self.evol_pop[1].append(self.pop[1])

    def pause(self, event=None):
        "Mise en pause de l'animation."
        self.flag = 0               #Stoppe la simulation
        self.change_bouton(1)

    def change_bouton(self, etat):
        "Modifie le bouton 'Play' en 'Pause' et inversement."
        if etat: self.bout_play.config(image=self.img[0], command=self.start)
        else:    self.bout_play.config(image=self.img[1], command=self.pause)

    def import_motif(self):
        "Charge une configuration initiale a partir d'un fichier .motf."
        if self.flag:
            self.pause()
            self.after(self.vitesse, self.import_motif)
            return

        #Ouvre la fenêtre d'importation
        fichier = askopenfile(mode="rb", filetypes=[("Motif",".motf")],
            defaultextension=".motf")
        #Si l'utilisateur ferme la fenêtre, on quitte la fonction:
        if not fichier: return

        try:    #On tente de récuperer le dictionnaire à l'aide du module Pickle
            motif = pickle.Unpickler(fichier)
            listes = motif.load()
            fichier.close()
        except: #Si il y a erreur, on ferme le fichier et on quitte la fonction
            fichier.close()
            return

        self.nouv_grille()        #On efface le canevas
        self.grille_vie, self.grille_proie, self.grille_predat,\
            self.grille_predatfaim, self.pop = listes

        #On actualise la population des proies
        self.showproie.config(text="Proies: {:4}".format(self.pop[0]))
        self.showpredat.config(text="Prédateurs: {:4}".format(self.pop[1]))

        #Cette boucle redessine la grille en fonction des nouvelles variables
        for x in range(0, self.xmax):
            for y in range(0, self.ymax):
                if self.grille_vie[x, y] == -1:
                    self.can.itemconfigure(self.grille_items[x, y],
                        fill=self.coul_milieu)
                if self.grille_proie[x, y]:
                    self.can.itemconfigure(self.grille_items[x, y],
                        fill=self.coul_cel[0])
                if self.grille_predat[x, y]:
                    self.can.itemconfigure(self.grille_items[x, y],
                        fill=self.coul_cel[1])

    def save_motif(self):
        "Sauvegarde une configuration initiale dans un fichier .motf."
        if self.flag:
            self.pause()
            self.after(self.vitesse, self.save_motif)
            return

        #Ouvre la fenêtre de sauvegarde
        fichier = asksaveasfile(mode="wb", filetypes=[("Motif",".motf")],
            defaultextension=".motf")
        if not fichier: return
        #On utilise le module Pickle pour sauvegarder le dictionnaire  :
        listes = pickle.Pickler(fichier)
        listes.dump( (self.grille_vie, self.grille_proie, self.grille_predat,\
            self.grille_predatfaim, self.pop) )
        fichier.close()                 #Fermeture du fichier

    def pop_aleatoire(self):
        "Initialise une nouvelle grille ayant une répartition aléatoire de\
        proies et de prédateurs."
        if self.flag:
            self.pause()
            self.after(self.vitesse, self.pop_aleatoire)
            return

        self.nouv_grille()
        #Correspond à un nombre maximal de proies ou de prédateurs par défaut
        cases = self.xmax*self.ymax // 4
        #Vérifie si le texte entré est bien un nombre entier
        try: pop_proie = int(self.nb_proie.get())
        except:
            self.nb_proie.delete(0, END)
            pop_proie = randint(1, cases)
        try: pop_predat = int(self.nb_predat.get())
        except:
            self.nb_predat.delete(0, END)
            pop_predat = randint(1, cases)

        #Teste si le nombre totale de proies/prédateurs est bien inférieure
        #au nombre total de cases
        if pop_proie + pop_predat > self.xmax*self.ymax:
            self.nb_proie.delete(0, END)
            self.nb_predat.delete(0, END)
            pop_proie = randint(1, cases)
            pop_predat = randint(1, cases)

        #Avec le nombre de proies et de prédateurs, on redessine la grille
        coord = [(x, y) for x in range(self.xmax) for y in range(self.ymax)]
        for _ in range(pop_proie):
            x, y = choice(coord)        #Choix d'une coordonnée au hasard
            self.proie_vie( x, y, randint(1, self.proie_cfg) )
            coord.remove((x, y))
        for _ in range(pop_predat):
            x, y = choice(coord)
            self.predat_vie( x, y, randint(1, self.predat_cfg[0]),
                randint(1, self.predat_cfg[1]) )
            coord.remove((x, y))

    def affiche_graphes(self):
        "Trace le graphe de l'évolution des populations au cours de la simulation."
        if self.flag:
            self.pause()
            self.after(self.vitesse, self.affiche_graphes)
            return

        gen = range(self.generation)
        plt.title("Evolution des populations au cours du temps")
        plt.plot(gen, self.evol_pop[0], linewidth=1.5,
            color="#22A7F0", label="Proies")
        plt.plot(gen, self.evol_pop[1], linewidth=1.5,
            color="#D35400", label="Prédateurs")
        plt.legend(loc='upper left')
        plt.xlabel("Génération")
        plt.ylabel("Nombre d'individus")
        plt.grid()
        plt.show()

        #Affiche les statistiques de la simulation:
        """if self.evol_pop != ([], []):
            stats = Toplevel(self)
            stats.title("Statistiques")

            maxi, mini, med, moy, et = np.amax(self.evol_pop[0]),\
                np.amin(self.evol_pop[0]), np.median(self.evol_pop[0]),\
                np.mean(self.evol_pop[0]), np.std(self.evol_pop[0])
            Label(stats, text="Résultats sur la population des proies:",\
                font="Arial 13 bold").grid(row=0, column=0, sticky=NW)
            Label(stats, text="Maximum: {:4}".format(maxi),\
                font="Arial 11").grid(row=1, column=0, sticky=NW)
            Label(stats, text="Minimum: {:4}".format(mini),\
                font="Arial 11").grid(row=2, column=0, sticky=NW)
            Label(stats, text="Valeur médiane: {:4.2f}".format(med),\
                font="Arial 11").grid(row=3, column=0, sticky=NW)
            Label(stats, text="Moyenne: {:4.2f}".format(moy),\
                font="Arial 11").grid(row=4, column=0, sticky=NW)
            Label(stats, text="Ecart-type: {:4.2f}\n".format(et),\
                font="Arial 11").grid(row=5, column=0, sticky=NW)

            maxi, mini, med, moy, et = np.amax(self.evol_pop[1]),\
                np.amin(self.evol_pop[1]), np.median(self.evol_pop[1]),\
                np.mean(self.evol_pop[1]), np.std(self.evol_pop[1])
            Label(stats, text="Résultats sur la population des prédateurs:",\
                font="Arial 13 bold").grid(row=6, column=0, sticky=NW)
            Label(stats, text="Maximum: {:4}".format(maxi),\
                font="Arial 11").grid(row=7, column=0, sticky=NW)
            Label(stats, text="Minimum: {:4}".format(mini),\
                font="Arial 11").grid(row=8, column=0, sticky=NW)
            Label(stats, text="Valeur médiane: {:4.2f}".format(med),\
                font="Arial 11").grid(row=9, column=0, sticky=NW)
            Label(stats, text="Moyenne: {:4.2f}".format(moy),\
                font="Arial 11").grid(row=10, column=0, sticky=NW)
            Label(stats, text="Ecart-type: {:4.2f}\n".format(et),\
                font="Arial 11").grid(row=11, column=0, sticky=NW)"""

    def credits(self):
        "Affiche les crédits et le fonctionnement du programme."
        fen_credits = Toplevel(self)
        fen_credits.title("Crédits")
        Label(fen_credits, text="Olivier Roques", font="Arial 13 bold").\
            grid(row=0, column=0)
        Label(fen_credits, text="TIPE 2015-2016", font="Arial 13 bold").\
            grid(row=1, column=0)
        Label(fen_credits, text="github:ojroques\n", font="Arial 13 bold").\
            grid(row=2, column=0)
        Label(fen_credits, text="En mode répartition:", font="Arial 12 bold").\
            grid(row=3, column=0, sticky=W)
        Label(fen_credits, text="- Clic gauche pour faire apparaître une proie",\
            font="Arial 12").grid(row=4, column=0, sticky=W)
        Label(fen_credits, text="- Clic droit pour faire apparaître un prédateur",\
            font="Arial 12").grid(row=5, column=0, sticky=W)
        Label(fen_credits, text="- Clic de la molette pour vider une cellule occupée\n",\
            font="Arial 12").grid(row=6, column=0, sticky=W)
        Label(fen_credits, text="En mode création d'obstacles:",\
            font="Arial 12 bold").grid(row=7, column=0, sticky=W)
        Label(fen_credits, text="- Clic gauche pour faire apparaître un obstacle",\
            font="Arial 12").grid(row=8, column=0, sticky=W)
        Label(fen_credits, text="- Clic de la molette pour vider une cellule occupée",\
            font="Arial 12").grid(row=9, column=0, sticky=W)


if __name__ == "__main__":
    fen = Tk()
    fen.title("Modelisation Proie-Prédateur")
    fen.resizable(width=False, height=False)
    ProiePredateur(fen).pack()
    fen.mainloop()
