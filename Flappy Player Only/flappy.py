import pygame  # pip install pygame
import os
import random

# DEFININDO DIMENSÕES DA TELA E REFERENCIANDO IMAGENS

TELA_LARGURA = 500
TELA_ALTURA = 800

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_imgs = os.path.join(diretorio_atual, "imgs")

IMAGEM_CANO = pygame.transform.scale2x(
    pygame.image.load(os.path.join(caminho_imgs, "pipe.png"))
)
IMAGEM_CHAO = pygame.transform.scale2x(
    pygame.image.load(os.path.join(caminho_imgs, "base.png"))
)
IMAGEM_BACKGROUND = pygame.transform.scale2x(
    pygame.image.load(os.path.join(caminho_imgs, "bg.png"))
)
IMAGENS_PASSARO = [
    pygame.transform.scale2x(
        pygame.image.load(os.path.join(caminho_imgs, "bird1.png"))
    ),
    pygame.transform.scale2x(
        pygame.image.load(os.path.join(caminho_imgs, "bird2.png"))
    ),
    pygame.transform.scale2x(
        pygame.image.load(os.path.join(caminho_imgs, "bird3.png"))
    ),
]

pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont("segoe_ui", 25)


class Passaro:  # DEFININDO AS INTERAÇÕES DOS PÁSSAROS
    IMGS = IMAGENS_PASSARO  # recebe os sprites dos pássaros

    ROTACAO_MAXIMA = 25  # evita que o pássaro rode demais
    VELOCIDADE_ROTACAO = 20  # evita que o pássaro rode rápido demais
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):  # inicializando variáveis para os métodos
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5  # altura do pulo
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        # movimento em parábola
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        # restringir deslocamento para que o pássaro não caia imediatamente
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # ângulo do pássaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA

        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # desenha sprite por sprite
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 5:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO * 2

        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        pos_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=pos_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):  # recebe a máscara para colisão
        return pygame.mask.from_surface(self.imagem)


class Cano:  # DEFININDO AS INTERAÇÕES DOS CANOS
    DISTANCIA = 200  # distancia entre o cano de cima e o debaixo
    VELOCIDADE = 5  # velocidade com que o cano irá se movimentar

    def __init__(self, x):  # inicializando variáveis para os métodos
        self.x = x
        self.altura = 0
        self.pos_top = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):  # y aleatório dos canos top e bottom
        self.altura = random.randrange(50, 450)
        self.pos_base = self.altura + self.DISTANCIA
        self.pos_top = self.altura - self.CANO_TOPO.get_height()

    def mover(self):  # tira VELOCIDADE de x, movimentando os canos à essquerda
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):  # desenha os canos na tela
        tela.blit(self.CANO_TOPO, (self.x, self.pos_top))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, Passaro):
        # recebe a máscara de colisão do pássaro e dos canos
        passaro_mask = Passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        # distância entre os canos de cima e baixo e o pássaro
        distancia_topo = (self.x - Passaro.x, self.pos_top - round(Passaro.y))
        distancia_base = (self.x - Passaro.x, self.pos_base - round(Passaro.y))

        # verifica se o pássaro sobrepôs algum cano (colidiu)
        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


class Chao:  # DEFININDO AS INTERAÇÕES DO CHÃO
    VELOCIDADE = 5  # velocidade com que o chão irá se movimentar
    LARGURA = IMAGEM_CHAO.get_width()  # recebendo a largura do chão
    IMAGEM = IMAGEM_CHAO  # recebendo a imagem do chão

    def __init__(self, y):  # inicializando variáveis para os métodos
        self.y = y  # o chão se encontra no final do eixo y fornecido como parâmetro
        self.x0 = 0  # margem esquerda do chão
        self.x1 = self.LARGURA  # margem direita do chão

    def mover(self):  # retira VELOCIDADE do eixo x, movendo o chão à esquerda
        self.x0 -= self.VELOCIDADE
        self.x1 -= self.VELOCIDADE

        # quando o sprite à esquerda sair da tela (x < 0), ele é movido para a direita do outro sprite

        if self.x0 + self.LARGURA < 0:
            self.x0 = self.x1 + self.LARGURA
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x0 + self.LARGURA

    def desenhar(self, tela):  # desenha dois sprites do chão
        tela.blit(self.IMAGEM, (self.x0, self.y))
        tela.blit(self.IMAGEM, (self.x1, self.y))


def desenhar_tela(tela, passaros, canos, chao, pontos):  # MÉTODO DE DESENHAR NA TELA
    tela.blit(IMAGEM_BACKGROUND, (0, 0))  # desenha na tela o background, em (0, 0)

    for passaro in passaros:  # desenha todos os pássaros passados por parâmetro
        passaro.desenhar(tela)

    for cano in canos:  # desenha todos os canos passados por parâmetro
        cano.desenhar(tela)

    chao.desenhar(tela)  # desenha o chão

    texto = FONTE_PONTOS.render(
        f"Pontuação: {pontos}", 1, (255, 255, 255)
    )  # define o texto da pontuação; e
    tela.blit(texto, (TELA_LARGURA - 10 - texto.get_width(), 10))  # o desenha na tela

    pygame.display.update()  # mantém a tela atualizada


def main():  # CÓDIGO PRINCIPAL
    passaros = [Passaro(230, 250)]  # pássaros que aparecerão
    chao = Chao(730)  # define o chão (y)
    canos = [Cano(700)]  # canos que aparecerão (x)

    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))  # define a tela do jogo
    pontos = 0  # define a pontuação

    relogio = pygame.time.Clock()  # define o clock do game

    rodando = True
    while rodando:
        relogio.tick(30)  # define o tick do game

        for evento in pygame.event.get():
            if (  # caso feche a janela ou aperte esc, o jogo fecha
                evento.type == pygame.QUIT  # A+BC
                or (evento.type == pygame.KEYDOWN)
                and (evento.key == pygame.K_ESCAPE)
            ):
                rodando = False
                pygame.quit()
                quit()
            if evento.type == pygame.KEYDOWN:  # caso aperte espaço, os pássaros pulam
                if evento.key == pygame.K_SPACE:
                    for passaro in passaros:
                        passaro.pular()

        for passaro in passaros:  # move os pássaros
            passaro.mover()

        chao.mover()

        adicionar_cano = False
        remover_canos = []

        for cano in canos:
            for i, passaro in enumerate(passaros):
                # caso o pássaro i colida com o cano, ele é removido e o jogo reseta
                if cano.colidir(passaro):
                    passaros.pop(i)
                    main()
                # se o pássaro passar pelo cano, guarde essa informação
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True

            cano.mover()  # move o cano

            # selecione o cano quando sair da tela
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        # se o pássaro passou pelo cano, some 1 ponto e adicione mais um cano
        if adicionar_cano:
            pontos += 1
            canos.append(Cano(600))

        # remova os canos que saíram da tela
        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            # se o pássaro i bater no chão ou no "teto", resete o jogo
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                main()

        # desenha a tela com os parâmetros passados
        desenhar_tela(tela, passaros, canos, chao, pontos)


if __name__ == "__main__":  # INICIALIZANDO O JOGO
    main()
