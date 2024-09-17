import random
import sys
import pygame
import pygame.freetype
import math
import time
import pathlib

pygame.init()

pygame.font.init()
myfont_1 = pygame.font.Font(None, 30)
myfont_2 = pygame.font.Font(None, 40)
myfont_3 = pygame.font.Font(None, 55)
myfont_4 = pygame.font.Font(None, 70)
myfont_5 = pygame.font.Font(None, 100)

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Casse-brique")

clock = pygame.time.Clock()

BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
BLEU = (100, 100, 255)
ROUGE = (237, 28, 36)
VERT = (100, 255, 100)
GRIS = (61, 61, 56)
JAUNE = (253, 228, 14)

RAYON_BALLE = 10
XMIN, YMIN = 0, 0
XMAX, YMAX = width, height


def file_in_directory(directory):
    """Retourne le nombre de niveau."""
    initial_count = 0
    for path in pathlib.Path(f"{directory}\\").iterdir():
        if path.is_file():
            initial_count += 1
    return initial_count


class Main:
    """Ensemble contenant tout ce qui sert au jeu (menu, etc)."""

    def __init__(self):
        self.menu = Menu(self)
        self.menu_niveau = MenuNiveau(self)
        self.info = Informations(self)
        self.parametre = Parametre(self)
        self.jeu = None
        self.fin = None

        self.menu_on = True
        self.menu_niveau_on = False
        self.info_on = False
        self.parametre_on = False
        self.jeu_on = False
        self.fin_du_jeu_on = False

        self.vitesse_balle = 2
        self.couleur = NOIR


class Balle:
    """Balle pour le jeu du Casse-brique.
        Elle est représenté par un rectangle en interne, mais apparaît ronde."""

    def __init__(self, parent, vitesse):
        self.parent = parent
        self.x, self.y = (400, 400)
        self.x_pre, self.y_pre = None, None
        self.vitesse = vitesse  # vitesse a varier entre 1 et 2 pr varier la difficulte (des bugs de collision peuvent apparaissent quand la vitesse se rapproche de 2)
        self.angle = self.direction()
        self.vitesse_par_angle(self.angle)  # mettre 123 pr tester bug collision sur niveau 6 ou niveau 1 avec la v11 du projet

    @staticmethod
    def direction():
        """Donne un angle aléatoire à la balle"""
        gauche, droite = random.randint(100, 160), random.randint(20, 80)
        gauche_ou_droite = random.randint(0, 1)
        if gauche_ou_droite == 0:
            return gauche
        else:
            return droite

    def vitesse_par_angle(self, angle):
        self.vx = self.vitesse * math.cos(math.radians(angle))
        self.vy = -self.vitesse * math.sin(math.radians(angle))

    def afficher(self):
        # pygame.draw.rect(screen, BLANC, (int(self.x - RAYON_BALLE), int(self.y - RAYON_BALLE), 2 * RAYON_BALLE, 2 * RAYON_BALLE), 0)
        pygame.draw.circle(screen, BLANC, (int(self.x), int(self.y)), 10, 0)

    def deplacer(self, raquette):
        self.x += self.vx
        self.y += self.vy
        if self.x + RAYON_BALLE > XMAX:
            self.vx = -self.vx
        if self.x - RAYON_BALLE < XMIN:
            self.vx = -self.vx
        if self.y + RAYON_BALLE > YMAX:
            main.jeu.balle = Balle(main.jeu, main.vitesse_balle)
            raquette.decrementer_vie()
            main.jeu.coeur[raquette.vie] = pygame.image.load("images\\coeur_vide.png").convert_alpha()
            main.jeu.coeur[raquette.vie] = pygame.transform.scale(main.jeu.coeur[raquette.vie], (30, 30))
        if self.y - RAYON_BALLE < YMIN:
            self.vy = -self.vy

    def calculer_angle(self):
        """Calcule l'angle que la balle doit avoir après avoir toucher la raquette, en fonction d'à quelle endroit elle la touche
            Angle = 25 si le milieu de la balle est hors de la raquette à droite
            Angle = 155 si le milieu de la balle est hors de la raquette à gauche
            Sinon Angle = 155 - i * 13 (i étant le numéro de la partie dans laquelle le milieu de la balle se situe)."""
        largeur_raquette = main.jeu.raquette.largeur
        x_gauche_raquette = main.jeu.raquette.x - main.jeu.raquette.largeur // 2
        largeur_partie = largeur_raquette // 10
        angle = self.angle
        if self.x < x_gauche_raquette:
            return 155
        for i in range(11):
            if x_gauche_raquette + largeur_partie * i < self.x < x_gauche_raquette + largeur_partie * (i + 1):
                angle = 155 - i * 13
                return angle
        return 25


class Raquette:
    """Raquette pour le jeu du Casse-brique.
        C'est un rectangle.
        La raquette a 3 vies (vies du joueurs), qu'elle perd lorsque la balle touche le bas de l'écran."""

    def __init__(self, parent):
        self.parent = parent
        self.x, self.y = (XMIN + XMAX) / 2, YMAX - RAYON_BALLE
        self.largeur = 10 * RAYON_BALLE
        self.hauteur = 2 * RAYON_BALLE
        self.vie = 3

    def afficher(self):
        pygame.draw.rect(screen, BLANC,
                         (int(self.x - self.largeur / 2), int(self.y - self.hauteur / 2), self.largeur, self.hauteur),
                         0)

    def deplacer(self, x):
        if x - self.largeur / 2 < XMIN:
            self.x = XMIN + self.largeur / 2
        elif x + self.largeur / 2 > XMAX:
            self.x = XMAX - self.largeur / 2
        else:
            self.x = x

    def decrementer_vie(self):
        self.vie -= 1


class Brique:
    """Brique pour le jeu du Casse-brique.
        C'est un rectangle.
        Elle peut avoir jusqu'à 3 vies, qu'elle perd à chaque collision avec la balle."""
    nombre_de_briques = 0

    def __init__(self, parent, x, y, largeur, hauteur, vie):
        self.parent = parent
        self.x, self.y = x, y
        self.largeur, self.hauteur = largeur, hauteur
        self.vie = vie

    @classmethod
    def afficher_tout(cls, liste_briques):
        """Prend une liste de brique et les affiche une par une"""
        for brique in liste_briques:
            if brique == "0":
                continue
            brique.afficher()

    def afficher(self):
        """Prend une brique et l'affiche"""
        if self.vie == 3:
            pygame.draw.rect(screen, (243, 24, 24), (
                int(self.x - self.largeur / 2), int(self.y - self.hauteur / 2), self.largeur, self.hauteur), 0)
        elif self.vie == 2:
            pygame.draw.rect(screen, (255, 255, 0), (
                int(self.x - self.largeur / 2), int(self.y - self.hauteur / 2), self.largeur, self.hauteur), 0)
        elif self.vie == 1:
            pygame.draw.rect(screen, BLANC, (
                int(self.x - self.largeur / 2), int(self.y - self.hauteur / 2), self.largeur, self.hauteur), 0)
        pygame.draw.rect(screen, BLEU,
                         (int(self.x - self.largeur / 2), int(self.y - self.hauteur / 2), self.largeur, self.hauteur),
                         1)


class Jeu:
    """Ecran de jeu, contenant la balle, la raquette, et l'ensemble des briques, placées grâce à des fichiers classés par niveau."""

    def __init__(self, parent, mode, niveau, vitesse_balle):
        self.parent = parent
        self.balle = Balle(self, vitesse_balle)
        self.raquette = Raquette(self)
        self.niveau = niveau
        self.briques = self.creer_briques(f"niveaux\\niveau_{self.niveau}.csv")
        self.stop = myfont_2.render(f"Appuyer sur la touche espace pour continuer", True, BLEU)
        self.bouton_pause = Bouton(self, "Quitter", XMAX // 2 - 66, YMAX // 2 + 30, myfont_3, BLEU)
        self.pause = False
        self.mode = mode
        self.niveau_max = file_in_directory("niveaux")
        self.coeur = self.creer_coeur()
        self.score = 0
        self.clique = False

        self.score_text = myfont_2.render(f"Score : {str(self.score)}", True, BLEU)
        self.niveau_text = myfont_2.render(f"Niveau : {str(self.niveau)}", True, BLEU)
        self.vie_text = myfont_2.render(f"Vie :", True, BLEU)

    def gestion_evenements(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.pause = True if self.pause == False else False
            elif event.type == pygame.MOUSEBUTTONUP:
                self.clique = True

    def mise_a_jour(self):
        x, y = pygame.mouse.get_pos()
        if not self.pause:
            self.balle.deplacer(self.raquette)
            self.raquette.deplacer(x)
            self.gerer_collision_balle_raquette(self.balle, self.raquette)
            self.gerer_collision_balle_briques(self.balle, self.briques)
            self.balle.x_pre, self.balle.y_pre = self.balle.x, self.balle.y
            if self.raquette.vie == 0:
                main.fin = Fin(main)
                main.fin_du_jeu_on = True
                main.fin.text_win = myfont_4.render("PERDU", True, BLEU)
            if Brique.nombre_de_briques == 0:
                if self.mode == "All":
                    self.balle = Balle(self, main.vitesse_balle)
                    if self.niveau >= self.niveau_max:
                        main.fin = Fin(main)
                        main.fin_du_jeu_on = True
                        main.fin.text_win = myfont_4.render("GAGNE", True, BLEU)
                    else:
                        self.niveau += 1
                        self.briques = self.creer_briques(f"niveaux\\niveau_{self.niveau}.csv")
                        self.niveau_text = myfont_2.render(f"Niveau : {str(self.niveau)}", True, BLEU)
                elif self.mode == "Level":
                    main.fin = Fin(main)
                    main.fin_du_jeu_on = True
                    main.fin.text_win = myfont_4.render("GAGNE", True, BLEU)
        else:
            if self.clique:
                if self.bouton_pause.clique_on():
                    main.jeu_on = False
                    main.menu_on = True
                self.clique = False

    def affichage(self):
        screen.fill(main.couleur)
        # image = pygame.image.load("images\\fond.png").convert_alpha()
        # screen.blit(image, (0, 0))
        self.balle.afficher()
        self.raquette.afficher()
        Brique.afficher_tout(self.briques)

        screen.blit(self.score_text, (0, 0))
        screen.blit(self.niveau_text, (340, 0))
        screen.blit(self.vie_text, (600, 0))

        x_coeur, y_coeur = 670, 0
        for coeur in self.coeur:
            screen.blit(coeur, (x_coeur, y_coeur))
            x_coeur += 40

        if self.pause:
            screen.blit(self.stop, (XMAX // 2 - 310, YMAX // 2 - 13))
            self.bouton_pause.affichage()

    def creer_briques(self, fichier):
        """Prend un fichier donné en argument, et créer des briques (de la classe Brique) en fonction du contenu du fichier"""
        # 11 briques de large (maximum) sur 12 de haut
        Brique.nombre_de_briques = 0
        briques = []
        with open(fichier) as f:
            lignes = []
            for ligne in f:
                ligne_0_1 = ligne.split(', ')
                ligne_0_1[-1] = ligne_0_1[-1].strip()
                lignes.append(ligne_0_1)

        largeur_brique = 71  # a ne pas changer
        hauteur_brique = largeur_brique // 3  # a ne pas changer
        for i in range(11):  # 2 colonnes vide sur les cotes et 9 remplissable au milieu
            for j in range(12):
                if lignes[j][i] == "0":
                    continue
                x, y = (largeur_brique + 2) * i + largeur_brique // 2, (hauteur_brique + 2) * j + hauteur_brique // 2
                brique = Brique(self, x, y, largeur_brique, hauteur_brique, int(lignes[j][i]))
                briques.append(brique)
                Brique.nombre_de_briques += 1
        return briques

    def creer_coeur(self):
        """Créer 3 coeur représentant les 3 vies du joueur"""
        vie_coeur = [pygame.image.load("images\\coeur_plein.png").convert_alpha() for _ in range(3)]
        for i in range(len(vie_coeur)):
            vie_coeur[i] = pygame.transform.scale(vie_coeur[i], (30, 30))
        return vie_coeur

    def gerer_collision_balle_raquette(self, balle, raquette):
        if self.collision_balle_raquette(balle, raquette):
            if (raquette.hauteur / 2 + RAYON_BALLE) - abs(raquette.y - balle.y) < (
                    raquette.largeur / 2 + RAYON_BALLE) - abs(
                    raquette.x - balle.x):  # if ((raquette.y - raquette.hauteur // 2) > (balle.y_pre + RAYON_BALLE)) or ((raquette.y + raquette.hauteur // 2) < (balle.y_pre - RAYON_BALLE)):
                balle.vy = -balle.vy
                self.balle.angle = self.balle.calculer_angle()
                self.balle.vitesse_par_angle(self.balle.angle)
            else:
                balle.vx = -balle.vx

    def collision_balle_raquette(self, balle, raquette):
        vertical = abs(raquette.y - balle.y) < raquette.hauteur / 2 + RAYON_BALLE
        horizontal = abs(raquette.x - balle.x) < raquette.largeur / 2 + RAYON_BALLE
        return vertical and horizontal

    def gerer_collision_balle_briques(self, balle, liste_briques):
        colli_x = False
        colli_y = False
        i = -1
        for brique in liste_briques:
            i += 1
            if brique == "0":
                continue
            if self.collision_balle_briques(balle, brique):
                if ((brique.y - brique.hauteur // 2) > (balle.y_pre + RAYON_BALLE)) or (
                        (brique.y + brique.hauteur // 2) < (balle.y_pre - RAYON_BALLE)):
                    colli_y = True
                else:
                    colli_x = True
                brique.vie -= 1
                if brique.vie == 0:
                    Brique.nombre_de_briques -= 1
                    self.score += 1
                    self.briques[i] = "0"
                    self.score_text = myfont_2.render(f"Score : {str(self.score)}", True, BLEU)
        if colli_x:
            balle.vx = -balle.vx
        elif colli_y:
            balle.vy = -balle.vy

    def collision_balle_briques(self, balle, brique):
        vertical = abs(brique.y - balle.y) < brique.hauteur / 2 + RAYON_BALLE
        horizontal = abs(brique.x - balle.x) < brique.largeur / 2 + RAYON_BALLE
        return vertical and horizontal


class Menu:
    """Ecran qui s'ouvre au démarrage du programme.
        Affiche le titre du jeu, et 3 boutons : Jouer (lance la partie au niveau 1)
                                                Niveau (ouvre le menu niveau)
                                                Paramètres (ouvre le menu des paramètre)."""

    def __init__(self, parent):
        self.parent = parent
        self.bouton_jouer = Bouton(self, "Jouer", XMAX // 2 - 53, YMAX // 2 - 30, myfont_3, BLEU)
        self.bouton_niveau = Bouton(self, "Niveau", XMAX // 2 - 63, YMAX // 2 + 40, myfont_3, BLEU)
        self.bouton_info = Bouton(self, "Informations", XMAX // 2 - 119, YMAX // 2 + 110, myfont_3, BLEU)
        self.bouton_parametre = Bouton(self, "    ", 725, 32, myfont_3, BLEU)
        self.text_nom_du_jeu = myfont_5.render(f"Casse-Brique", True, BLEU)
        self.roue_dentee = pygame.image.load("images\\roue_dentee.png").convert_alpha()
        self.roue_dentee = pygame.transform.scale(self.roue_dentee, (40, 40))
        self.clique = False

    def gestion_evenements(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                self.clique = True
            elif event.type == pygame.QUIT:
                sys.exit()

    def mise_a_jour(self):
        if self.clique:
            if self.bouton_jouer.clique_on():
                main.menu_on = False
                main.jeu = Jeu(main, "All", 1, main.vitesse_balle)
                main.jeu_on = True
            elif self.bouton_niveau.clique_on():
                main.menu_on = False
                main.menu_niveau_on = True
            elif self.bouton_info.clique_on():
                main.menu_on = False
                main.info_on = True
            elif self.bouton_parametre.clique_on():
                main.menu_on = False
                main.parametre_on = True
            self.clique = False

    def affichage(self):
        screen.fill(main.couleur)
        # image = pygame.image.load("images\\fond.png").convert_alpha()
        # screen.blit(image, (0, 0))
        screen.blit(self.text_nom_du_jeu, (170, 20))
        screen.blit(self.roue_dentee, (730, 35))
        self.bouton_jouer.affichage()
        self.bouton_niveau.affichage()
        self.bouton_info.affichage()
        self.bouton_parametre.affichage()


class Fin:
    """Ecran de fin, qui s'affiche lorsque le joueur fini tous les niveaux ou a perdu toutes ses vies.
        Affiche le niveau atteint, le score, et 2 boutons : Menu (ouvre le menu de base du jeu)
                                                            Rejouer (relance une partie au niveau 1)."""

    def __init__(self, parent):
        self.parent = parent
        self.bouton_menu = Bouton(self, "Menu", XMAX // 2 - 52, YMAX // 2 + 20, myfont_3, BLEU)
        self.bouton_rejouer = Bouton(self, "Rejouer", XMAX // 2 - 72, YMAX // 2 + 90, myfont_3, BLEU)
        self.text_win = myfont_4.render("GAGNE", True, BLEU)
        self.clique = False

        self.score_text = myfont_4.render(f"Score : {main.jeu.score}", True, BLEU)
        if main.jeu.mode == "All":
            self.niveau_text = myfont_4.render(f"Niveau atteint : {main.jeu.niveau}", True, BLEU)
        elif main.jeu.mode == "Level":
            self.niveau_text = myfont_4.render(f"Niveau {main.jeu.niveau}", True, BLEU)

    def gestion_evenements(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                self.clique = True
            elif event.type == pygame.QUIT:
                sys.exit()

    def mise_a_jour(self):
        if self.clique:  # agir seulement si on clique sur l'ecran
            if self.bouton_menu.clique_on():
                main.fin_du_jeu_on = False
                main.menu_on = True
            if self.bouton_rejouer.clique_on():
                main.fin_du_jeu_on = False
                main.jeu_on = True
                main.jeu.balle = Balle(main.jeu, main.vitesse_balle)
                main.jeu.raquette = Raquette(main.jeu)
                if main.jeu.mode == "All":
                    main.jeu.niveau = 1
                main.jeu.briques = main.jeu.creer_briques(f"niveaux\\niveau_{main.jeu.niveau}.csv")
                main.jeu.coeur = main.jeu.creer_coeur()
                for i in range(3):
                    main.jeu.coeur[i] = pygame.image.load("images\\coeur_plein.png").convert_alpha()
                    main.jeu.coeur[i] = pygame.transform.scale(main.jeu.coeur[i], (30, 30))
                main.jeu.score = 0
            self.clique = False

    def affichage(self):
        screen.fill(main.couleur)
        # image = pygame.image.load("images\\fond.png").convert_alpha()
        # screen.blit(image, (0, 0))
        screen.blit(self.text_win, (XMAX // 2 - 84, 20))
        screen.blit(self.niveau_text, (XMAX // 2 - 215, YMAX // 2 - 180))
        screen.blit(self.score_text, (XMAX // 2 - 215, YMAX // 2 - 110))
        pygame.draw.rect(screen, BLEU, (XMAX // 2 - 225, YMAX // 2 - 190, 450, 132), 1)
        self.bouton_rejouer.affichage()
        self.bouton_menu.affichage()


class MenuNiveau:
    """Menu servant à choisir le niveau auquel commencé.
        Les niveaux disponibles s'affichent en bleu, les niveaux non-disponibles en gris."""

    def __init__(self, parent):
        self.parent = parent
        self.nb_niveaux = file_in_directory("niveaux")
        self.bouton_retour = Bouton(self, "RETOUR", 0, 0, myfont_2, BLEU)
        self.boutons_niveaux = self.creer_boutons_niveaux(self.nb_niveaux)
        self.text_niveau = myfont_2.render(f"NIVEAUX", True, BLEU)
        self.clique = False

    def creer_boutons_niveaux(self, nb_niveaux):
        """Créer 4x4 boutons, mais seulement {nb_niveaux} boutons sont cliquables et lancent le niveau du jeu associé"""
        boutons_niveaux = []
        nb_lignes, nb_colonnes = 4, 4
        largeur_case, hauteur_case = self._decouper_ecran(nb_lignes, nb_colonnes)
        niveau = 1
        for i in range(nb_lignes):
            for j in range(nb_colonnes):
                if niveau > nb_niveaux:
                    couleur_txt = GRIS
                else:
                    couleur_txt = BLEU
                bouton_niveau = Bouton(self, f"{niveau}", largeur_case * j + largeur_case // 3,
                                       hauteur_case * i + 40 + hauteur_case // 4, myfont_5, couleur_txt)
                boutons_niveaux.append(bouton_niveau)
                niveau += 1
        return boutons_niveaux

    def _decouper_ecran(self, nb_lignes, nb_colonnes):
        largeur, hauteur = XMAX, YMAX - 40
        largeur_case, hauteur_case = largeur // nb_colonnes, hauteur // nb_lignes
        return largeur_case, hauteur_case

    def gestion_evenements(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                self.clique = True
            elif event.type == pygame.QUIT:
                sys.exit()

    def mise_a_jour(self):  # j'en suis a la pr renommage variable etc
        if self.clique:
            if self.bouton_retour.clique_on():
                main.menu_on = True
                main.menu_niveau_on = False
            for bouton in self.boutons_niveaux:
                if int(bouton.text) <= self.nb_niveaux and bouton.clique_on():
                    niveau = int(bouton.text)
                    main.menu_niveau_on = False
                    main.jeu = Jeu(main, "Level", niveau, main.vitesse_balle)
                    main.jeu_on = True
            self.clique = False

    def affichage(self):
        screen.fill(main.couleur)
        # image = pygame.image.load("images\\fond.png").convert_alpha()
        # screen.blit(image, (0, 0))
        self.bouton_retour.affichage()
        for bouton in self.boutons_niveaux:
            bouton.affichage()
        screen.blit(self.text_niveau, (XMAX // 2 - 65, 6))

        largeur_case, hauteur_case = self._decouper_ecran(4, 4)
        for i in range(4):
            for j in range(4):
                pygame.draw.rect(screen, BLANC, (largeur_case * j, hauteur_case * i + 40, largeur_case, hauteur_case),
                                 1)  # pr voir rectangle (a supp)


class Parametre:
    """Menu servant à changer les paramètres tels que le niveau de difficulté (vitesse de la balle), et la couleur de fond du jeu."""

    def __init__(self, parent):
        self.parent = parent
        self.bouton_retour = Bouton(self, "RETOUR", 0, 0, myfont_2, BLEU)
        self.bouton_par_default_all = Bouton(self, "Par défaut", 640, 83, myfont_2, BLEU)
        self.bouton_par_default_difficulte = Bouton(self, "Par défaut", 640, 153, myfont_2, BLEU)
        self.bouton_par_default_couleur = Bouton(self, "Par défaut", 640, 223, myfont_2, BLEU)
        self.text_parametre = myfont_4.render(f"PARAMETRES", True, BLEU)
        self.text_difficulte = myfont_3.render("Difficulté", True, BLEU)
        self.text_couleur = myfont_3.render("Couleur", True, BLEU)
        self.barre_difficulte = BarreEchellon(self, 230, 160, 400, 20, 4, BLEU)
        self.listbox_couleur = Listbox(self, 230, 230, 120, 30, 4, BLEU, myfont_2, [NOIR, ROUGE, VERT, JAUNE],
                                       ["Noir", "Rouge", "Vert", "Jaune"])
        self.clique = False

    def gestion_evenements(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                self.clique = True
            elif event.type == pygame.QUIT:
                sys.exit()

    def mise_a_jour(self):
        if self.clique:
            if self.bouton_retour.clique_on():
                main.menu_on = True
                main.parametre_on = False
            if self.barre_difficulte.clique_on():
                self.changer_vitesse_balle(self.barre_difficulte.selection)
            if self.bouton_par_default_difficulte.clique_on() or self.bouton_par_default_all.clique_on():
                self.barre_difficulte.selection = 0
                self.changer_vitesse_balle(self.barre_difficulte.selection)
            if self.listbox_couleur.clique_on():
                self.listbox_couleur.gerer_clique()
                main.couleur = self.listbox_couleur.choix[self.listbox_couleur.selection]
            if self.bouton_par_default_couleur.clique_on() or self.bouton_par_default_all.clique_on():
                self.listbox_couleur.selection = 0
                main.couleur = self.listbox_couleur.selection
            self.clique = False

    def affichage(self):
        screen.fill(main.couleur)
        # image = pygame.image.load("images\\fond.png").convert_alpha()
        # screen.blit(image, (0, 0))
        self.bouton_retour.affichage()
        self.bouton_par_default_all.affichage()
        self.barre_difficulte.affichage()
        self.bouton_par_default_difficulte.affichage()
        self.listbox_couleur.affichage()
        self.bouton_par_default_couleur.affichage()
        screen.blit(self.text_parametre, (XMAX // 2 - 170, 6))
        screen.blit(self.text_difficulte, (20, 150))
        screen.blit(self.text_couleur, (20, 220))

    def changer_vitesse_balle(self, difficulte):
        """Change la vitesse de la balle en fonction de la difficulté donnée en argument"""
        if self.barre_difficulte.nb_echellon == 2:
            echelle = 1
        else:
            echelle = 1 / (self.barre_difficulte.nb_echellon - 1)
        main.vitesse_balle = 2 + echelle * difficulte
        try:
            main.jeu.balle.vitesse = 2 + echelle * difficulte
        except:
            pass


class Informations:
    """Menu explicatif"""
    def __init__(self, parent):
        self.parent = parent
        self.bouton_retour = Bouton(self, "RETOUR", 0, 0, myfont_2, BLEU)
        self.titre_text = myfont_4.render("INFORMATIONS", True, BLEU)
        self.info_text_1 = myfont_2.render("Bienvenu à toi cher joueur !", True, BLEU)
        self.info_text_2 = myfont_1.render("Le but du jeu est simple : casser toutes les briques. Pour cela, vous", True, BLEU)
        self.info_text_3 = myfont_1.render("contrôlerez une raquette qui vous permettra de faire rebondir une balle, qui", True, BLEU)
        self.info_text_4 = myfont_1.render("ira détuire les briques au dessus. C'est aussi simple que ça !!", True, BLEU)
        self.info_text_5 = myfont_1.render("Plus la balle rebondit à gauche de la raquette, plus elle partira vers la", True, BLEU)
        self.info_text_6 = myfont_1.render("gauche, et inversement pour la droite.", True, BLEU)
        self.info_text_7 = myfont_1.render("Mais attention ! Si la balle touche le bas de l'écran, vous perdrez une vie.", True, BLEU)
        self.info_text_8 = myfont_1.render("Vous avez un total de 3 vies.", True, BLEU)
        self.info_text_9 = myfont_1.render("Dans le menu principal, vous pouvez cliquer sur le bouton « Niveau » pour", True, BLEU)
        self.info_text_10 = myfont_1.render("accéder au menu des niveaux, qui vous permettra de jouer le niveau que vous", True, BLEU)
        self.info_text_11 = myfont_1.render("souhaité. Les niveaux en gris ne sont pas encore disponibles.", True, BLEU)
        self.info_text_12 = myfont_1.render("Vous pouvez aussi cliquer sur le symbole en forme d'engrenage, ce qui", True, BLEU)
        self.info_text_13 = myfont_1.render("ouvrira le menu des paramètres. Vous pouvez y modifier la difficulté, ou la", True, BLEU)
        self.info_text_14 = myfont_1.render("couleur du fond.", True, BLEU)
        self.info_text_15 = myfont_1.render("Allez, maintenant c'est l'heure d'exploser tous les records, bonne chance !!!", True, BLEU)
        self.texts = [self.info_text_1, self.info_text_2, self.info_text_3, self.info_text_4, self.info_text_5, self.info_text_6, self.info_text_7, self.info_text_8, self.info_text_9, self.info_text_10, self.info_text_11, self.info_text_12, self.info_text_13, self.info_text_14, self.info_text_15]
        self.clique = False

    def gestion_evenements(self):
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                self.clique = True
            elif event.type == pygame.QUIT:
                sys.exit()

    def mise_a_jour(self):
        if self.clique:
            if self.bouton_retour.clique_on():
                main.info_on = False
                main.menu_on = True
            self.clique = False

    def affichage(self):
        screen.fill(main.couleur)
        # image = pygame.image.load("images\\fond.png").convert_alpha()
        # screen.blit(image, (0, 0))
        self.bouton_retour.affichage()
        screen.blit(self.titre_text, (XMAX // 2 - 191, 6))
        screen.blit(self.info_text_1, (20, 130))
        for i in range(7):
            screen.blit(self.texts[i+1], (20, 200 + (22 * i)) )
        for i in range(6):
            screen.blit(self.texts[i+8], (20, 376 + (22 * i)) )
        screen.blit(self.info_text_15, (20, 536))


class Bouton:
    """Créer un bouton sur lequel l'utilisateur peut cliquer.
        Lorsque le joueur passe le curseur sur le bouton, un rectangle se dessine autour."""

    def __init__(self, parent, text, x, y, font, couleur):
        self.parent = parent
        self.x, self.y = x, y
        self.text = text
        self.couleur = couleur
        self.text_surface = font.render(f"{text}", True, couleur)
        dimensions = self.text_surface.get_rect()
        _, _, self.largeur, self.hauteur = dimensions
        self.rect = pygame.Rect((x, y), (self.largeur + 10, self.hauteur + 10))
        self.focus_in = False

    def _focus_in(self):
        """Retourne True si l'objet a le focus de la souris, sinon retourne False"""
        x, y = pygame.mouse.get_pos()
        if self.rect.collidepoint(x, y):
            self.focus_in = True
            return True
        self.focus_in = False
        return False

    def clique_on(self):
        """Méthode appelée que si un clique a été détecté sur la page courante"""
        if self._focus_in():
            self.focus_in = False
            return True

    def affichage(self):
        if self._focus_in():
            pygame.draw.rect(screen, self.couleur, self.rect, 1)
        screen.blit(self.text_surface, (self.x + 5, self.y + 5))


class BarreEchellon:
    """Créer une barre, avec différents niveaux, que l'utilisateur peut sélectionner à sa guise."""

    def __init__(self, parent, x, y, largeur, hauteur, nb_echellon, couleur):
        if nb_echellon < 2:
            raise ValueError("Le nombre d'echellon doit être supérieur (ou égale) à 2")
        if largeur < nb_echellon * 20:
            raise ValueError("La largeur est trop petite pas rapport au nombre d'echellon donné")
        self.parent = parent
        self.x, self.y = x, y
        self.largeur, self.hauteur = largeur, hauteur
        self.nb_echellon = nb_echellon
        self.distance_bloc = (self.largeur - self.nb_echellon * 20) // (
                self.nb_echellon - 1)  # 20 = largeur d'un rectangle_echellon  # distance pr le trait
        self.distance_echellon = (self.largeur - 20) // (self.nb_echellon - 1)  # distance pr placer les blocs
        self.couleur = couleur
        self.echellons, self.numeros = self.creer_echellon(self.nb_echellon)
        self.selection = 0
        self.focus_in = False

    def creer_echellon(self, nb_echellon):
        """Créer {nb_echellon} echellons, puis les retourne ainsi qu'une liste de numéros (sous forme de font.render) allant de 0 à {nb_echellon} - 1"""
        echellons = []
        numeros = []
        for i in range(nb_echellon):
            x, y = self.x + self.distance_echellon * i, self.y
            echellons.append(pygame.Rect((x, y), (20, 20)))
            numeros.append(myfont_1.render(f"{i}", True, NOIR))
        return echellons, numeros

    def _focus_in(self):
        """Retourne True si l'objet a le focus de la souris, sinon retourne False"""
        x, y = pygame.mouse.get_pos()
        i = 0
        for echellon in self.echellons:
            if echellon.collidepoint(x, y):
                self.focus_in = True
                self.selection = i
                return True
            i += 1
        self.focus_in = False
        return False

    def clique_on(self):
        """Méthode appelée que si un clique a été détecté sur la page courante"""
        if self._focus_in():
            self.focus_in = False
            return True
        return False

    def affichage(self):
        pygame.draw.rect(screen, self.couleur, (self.x, self.y + self.hauteur // 2 - 2, self.largeur, 4), 0)
        # pygame.draw.rect(screen, self.couleur, (self.x, self.y, self.largeur, self.hauteur), 1)
        for i in range(len(self.echellons)):
            if i == self.selection:
                # pygame.draw.rect(screen, JAUNE, (self.x + self.distance_echellon * i, self.y, 20, 20), 0)
                pygame.draw.circle(screen, JAUNE, ((self.x + 10) + self.distance_echellon * i, (self.y + 10)), 12, 0)
            else:
                # pygame.draw.rect(screen, self.couleur, (self.x + self.distance_echellon * i, self.y, 20, 20), 0)
                pygame.draw.circle(screen, self.couleur, ((self.x + 10) + self.distance_echellon * i, (self.y + 10)),
                                   12, 0)
            screen.blit(self.numeros[i], (self.x + self.distance_echellon * i + 4, self.y + 2))


class Listbox:
    """Créer une listbox.
        Lorsque l'utilisateur clique dessus, ouvre une liste de choix possibles.
        Quand l'utilisateur clique sur un choix, la liste se referme et la première ligne est modifié avec ce choix."""

    def __init__(self, parent, x, y, largeur, hauteur, nb_lignes, couleur, font, choix, nom_choix):
        self.parent = parent
        self.x, self.y = x, y
        self.largeur, self.hauteur = largeur, hauteur
        self.nb_lignes = nb_lignes
        self.couleur = couleur
        self.font = font
        self.choix = choix
        self.nom_choix = nom_choix
        self.lignes = self.creer_lignes()
        self.premiere_ligne = pygame.Rect((self.x, self.y), (self.largeur, 30))
        self.selection = 0
        self.focus_in = False
        self.ouvert = False

    def creer_lignes(self):
        """Créer autant de lignes (rectangle + texte) que de choix possibles dans la listbox"""
        lignes = []
        for i in range(len(self.nom_choix)):
            ligne_rect = pygame.Rect((self.x, self.y + 30 * (i + 1)), (self.largeur, 30))
            ligne_text = self.font.render(f"{self.nom_choix[i]}", True, self.couleur)
            lignes.append((ligne_rect, ligne_text))
        return lignes

    def _focus_in(self):
        """Retourne True si l'objet a le focus de la souris, sinon retourne False"""
        x, y = pygame.mouse.get_pos()
        if self.ouvert:
            i = 0
            for ligne in self.lignes:
                if ligne[0].collidepoint(x, y):
                    self.focus_in = True
                    self.selection = i
                    return True
                i += 1
            self.focus_in = False
            return False
        elif not self.ouvert:
            if self.premiere_ligne.collidepoint(x, y):
                self.focus_in = True
                return True
            self.focus_in = False
            return False

    def clique_on(self):
        """Méthode appelée que si un clique a été détecté sur la page courante"""
        if self._focus_in():
            self.focus_in = False
            return True
        return False

    def gerer_clique(self):
        """Ouvre la listbox si elle est fermée ou inversement"""
        self.ouvert = (True if self.ouvert == False else False)

    def affichage(self):
        if self.ouvert:
            pygame.draw.rect(screen, BLANC, (self.x, self.y, self.largeur, self.hauteur), 0)
            screen.blit(self.font.render(f"{self.nom_choix[self.selection]}", True, GRIS), (self.x, self.y))
            for i in range(len(self.lignes)):
                pygame.draw.rect(screen, BLANC, (self.x, self.y + 30 * (i + 1), self.largeur, self.hauteur), 0)
                screen.blit(self.lignes[i][1], (self.x, self.y + 30 * (i + 1)))
            pygame.draw.rect(screen, NOIR, (self.x - 1, self.y - 1, self.largeur + 2, self.hauteur + 2), 1)
        elif not self.ouvert:
            pygame.draw.rect(screen, BLANC, (self.x, self.y, self.largeur, self.hauteur), 0)
            screen.blit(self.font.render(f"{self.nom_choix[self.selection]}", True, GRIS), (self.x, self.y))
            pygame.draw.rect(screen, NOIR, (self.x - 1, self.y - 1, self.largeur + 2, self.hauteur + 2), 1)


main = Main()

while True:
    if main.menu_on:
        main.menu.gestion_evenements()
        main.menu.mise_a_jour()
        main.menu.affichage()
        pygame.display.flip()
    elif main.menu_niveau_on:
        main.menu_niveau.gestion_evenements()
        main.menu_niveau.mise_a_jour()
        main.menu_niveau.affichage()
        pygame.display.flip()
    elif main.info_on:
        main.info.gestion_evenements()
        main.info.mise_a_jour()
        main.info.affichage()
        pygame.display.flip()
    elif main.parametre_on:
        main.parametre.gestion_evenements()
        main.parametre.mise_a_jour()
        main.parametre.affichage()
        pygame.display.flip()
    elif main.jeu_on:
        main.jeu.gestion_evenements()
        main.jeu.mise_a_jour()
        if main.fin_du_jeu_on:
            main.jeu_on = False
        main.jeu.affichage()
        pygame.display.flip()
    elif main.fin_du_jeu_on:
        main.fin.gestion_evenements()
        main.fin.mise_a_jour()
        main.fin.affichage()
        pygame.display.flip()
    clock.tick(240)
