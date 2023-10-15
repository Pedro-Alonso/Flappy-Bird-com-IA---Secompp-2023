import pygame  # pip install pygame
import neat  # pip install neat-python
import os
import random

# DEFININDO DIMENSÕES DA TELA E REFERENCIANDO IMAGENS

TELA_LARGURA = 500
TELA_ALTURA = 800

ia_jogando = True
geracao = 0

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


# DEFINIÇÃO DA CLASSE PÁSSARO, RESPONSÁVEL PELA INTERAÇÃO DOS PÁSSAROS COM OS DEMAIS ELEMENTOS
class Passaro:
    # Recebe os sprites dos pássaros
    IMGS = IMAGENS_PASSARO

    # Evita que os pássaros rodem demais
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 7

    def __init__(self, x, y):  # Inicializando construtor
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5  # Altura do pulo
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        self.tempo += 1
        # Fórmula do movimento em parábola
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        # Restringir deslocamento para que o pássaro não caia imediatamente
        if deslocamento > 16:
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        # Ângulo do pássaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA

        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        # Desenha sprite por sprite
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

    def get_mask(self):  # Recebe a máscara para colisão
        return pygame.mask.from_surface(self.imagem)


# DEFINIÇÃO DA CLASSE CANO, RESPONSÁVEL PELA INTERAÇÃO DOS CANOS COM OS DEMAIS ELEMENTOS
class Cano:
    DISTANCIA = 200  # Distância entre os canos superior e inferior
    VELOCIDADE = 7  # Velocidade com que os canos irão se movimentar
    VELOCIDADE_VERTICAL = 2  # Velocidade com que os canos sobem e descem

    def __init__(self, x):  # Inicializando construtor
        self.x = x
        self.altura = 0
        self.pos_top = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()
        self.subindo = True

    def definir_altura(self):
        # Altura y aleatória para posicionar os canos
        self.altura = random.randrange(50, 450)
        self.pos_base = self.altura + self.DISTANCIA
        self.pos_top = self.altura - self.CANO_TOPO.get_height()

    def mover(self):
        # Retira VELOCIDADE da posição x, movimentando os canos à esquerda
        self.x -= self.VELOCIDADE

        if self.subindo:
            self.altura -= self.VELOCIDADE_VERTICAL
            if self.altura < 50:
                self.subindo = False
        else:
            self.altura += self.VELOCIDADE_VERTICAL
            if self.altura > 450:
                self.subindo = False

        self.pos_top = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DISTANCIA

    def desenhar(self, tela):  # Desenha os canos na tela
        tela.blit(self.CANO_TOPO, (self.x, self.pos_top))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, Passaro):
        # Recebe as máscaras de colisão do pássaro e dos canos
        passaro_mask = Passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        # Define a distância entre os canos superior e inferior, e o pássaro
        distancia_topo = (self.x - Passaro.x, self.pos_top - round(Passaro.y))
        distancia_base = (self.x - Passaro.x, self.pos_base - round(Passaro.y))

        # Verifica se o pássaro sobrepôs algum cano (colidiu)
        topo_ponto = passaro_mask.overlap(topo_mask, distancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False


# DEFINIÇÃO DA CLASSE CHAO, RESPONSÁVEL PELA INTERAÇÃO DO CHÃO COM OS DEMAIS ELEMENTOS
class Chao:
    VELOCIDADE = 7  # Velocidade com que o chão irá se movimentar
    LARGURA = IMAGEM_CHAO.get_width()  # Recebe a largura do chão
    IMAGEM = IMAGEM_CHAO  # Recebe o sprite do chão

    def __init__(self, y):  # Inicializando construtor
        # O chão se encontra no final do eixo y fornecido como parâmetro
        self.y = y
        self.x0 = 0  # Define x0 como a margem esquerda do chão
        self.x1 = self.LARGURA  # Define x1 como a margem direita do chão

    def mover(self):
        # Retira VELOCIDADE da posição x, movendo o chão à esquerda
        self.x0 -= self.VELOCIDADE
        self.x1 -= self.VELOCIDADE

        # Quando o sprite à esquerda sair da tela (x < 0), ele é movido para a direita do outro sprite
        if self.x0 + self.LARGURA < 0:
            self.x0 = self.x1 + self.LARGURA
        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x0 + self.LARGURA

    def desenhar(self, tela):  # Desenha dois sprites do chão, um ao lado do outro
        tela.blit(self.IMAGEM, (self.x0, self.y))
        tela.blit(self.IMAGEM, (self.x1, self.y))


# MÉTODO PARA DESENHAR OS ELEMENTOS NA TELA
def desenhar_tela(tela, passaros, canos, chao, pontos):
    tela.blit(
        IMAGEM_BACKGROUND, (0, 0)
    )  # Desenha na tela o background, na posição (0, 0)

    for passaro in passaros:  # Desenha todos os pássaros passados por parâmetro
        passaro.desenhar(tela)

    for cano in canos:  # Desenha todos os canos passados por parâmetro
        cano.desenhar(tela)
        
    # Desenha o texto da pontuação
    pts = FONTE_PONTOS.render(f"Pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(pts, (TELA_LARGURA - 10 - pts.get_width(), 10))

    chao.desenhar(tela)  # Desenha o chão

    pygame.display.update()  # Mantém a tela atualizada


# CÓDIGO PRINCIPAL
def main(genomas, config):

    # Define os pássaros e neurônios, caso a IA esteja jogando
    redes = []
    lista_genomas = []
    passaros = []
    pontos = 0  # Inicia a pontuação

    for _, genoma in genomas:
        rede = neat.nn.FeedForwardNetwork.create(genoma, config)
        redes.append(rede)
        genoma.fitness = 0
        lista_genomas.append(genoma)
        passaros.append(Passaro(230, 250))

    chao = Chao(730)  # Define o chão na posição y
    canos = [Cano(700)]  # Define os canos na posição x

    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))  # Define a tela do jogo
    # Define o clock do game
    relogio = pygame.time.Clock()

    rodando = True
    while rodando:
        relogio.tick(80)

        for evento in pygame.event.get():
            if (  # Caso feche a janela, o jogo fecha
                evento.type == pygame.QUIT
            ):
                rodando = False
                pygame.quit()
                quit()

        # Parâmetros de colisão com o teto/chão
        for i, passaro in enumerate(passaros):
            # Se o pássaro i bater no chão ou no "teto", resete o jogo
            if (passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)
                if ia_jogando:
                    #  Não há punição para que a IA não evite subir ou descer
                    lista_genomas.pop(i)
                    redes.pop(i)

        # Ajuda a IA a encontrar o cano da frente
        indice_cano = 0
        if (
            len(passaros) > 0):  # Se houver pássaros vivos, continue
            if (
                len(passaros) > 0
                and len(canos) > 1
                and passaros[0].x > (canos[0].x + canos[0].CANO_TOPO.get_width())
            ):
                indice_cano = 1
        else:  # Se todos morreram, reinicie o game
            rodar(caminho_config)

        # Movimentos da IA
        for i, passaro in enumerate(passaros):
            passaro.mover()
            # Cada vez que o pássaro i se mover, ele ganha um bônus de 0.1 (treat)
            if ia_jogando:
                lista_genomas[i].fitness += 0.1
                output = redes[i].activate(
                    (  # Camadas de entrada da rede:
                        # Altura do pássaro
                        passaro.y,
                        # Distância do pássaro em relação â quina dos canos
                        abs(passaro.y - canos[indice_cano].altura),  # de cima
                        abs(passaro.y - canos[indice_cano].pos_base),  # debaixo
                    )
                )
                if output[0] > 0.5:
                    passaro.pular()  # Pássaro da IA pula

        chao.mover()

        adicionar_cano = False
        remover_canos = []

        for cano in canos:
            for i, passaro in enumerate(passaros):
                # Caso o pássaro i colida com o cano, ele é removido
                if cano.colidir(passaro):
                    passaros.pop(i)
                    if ia_jogando:
                        # Pune a IA por morrer (-1.0 treat) e exclui o genoma
                        lista_genomas[i].fitness -= 1
                        lista_genomas.pop(i)

                # Se o pássaro passar pelo cano, guarde essa informação
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True

            cano.mover()  # Move o cano

            # Selecione o cano quando sair da tela
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        # Se o pássaro passou pelo cano, some 1 ponto e adicione mais um cano
        if adicionar_cano:
            pontos += 1
            if ia_jogando:
                for genoma in lista_genomas:
                    # Dá um bônus (+5.0 treat) quando a IA passa pelo cano
                    genoma.fitness += 5
            canos.append(Cano(600))

        # Remova os canos que saíram da tela
        for cano in remover_canos:
            canos.remove(cano)

        # Desenha a tela com os parâmetros passados

        desenhar_tela(
            tela,
            passaros,
            canos,
            chao,
            pontos
        )


def rodar(caminho_config):  # IMPORTA AS CONFIGS DA REDE
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        caminho_config,
    )
    populacao = neat.Population(config)

    if ia_jogando:
        populacao.run(main, 50)
    else:
        main(None, None)


if __name__ == "__main__":  # INICIALIZANDO O JOGO
    caminho_config = "config.txt"
    rodar(caminho_config)
