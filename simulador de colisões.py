import pygame
import sys
import math
import random
import os

# 1. Configurações da simulação
LARGURA = 800
ALTURA = 600
FPS = 60
DT = 1 / FPS
PRETO = (0, 0, 0)


# 2. Molde de cada bola
class Bola:
    def __init__(self, x, y, vx, vy, massa, raio, cor):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.massa = massa
        self.raio = raio
        self.cor = cor

    def mover(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Paredes esquerda e direita
        if self.x - self.raio <= 0:
            self.x = self.raio
            self.vx = abs(self.vx)
        elif self.x + self.raio >= LARGURA:
            self.x = LARGURA - self.raio
            self.vx = -abs(self.vx)

        # Teto e chão
        if self.y - self.raio <= 0:
            self.y = self.raio
            self.vy = abs(self.vy)
        elif self.y + self.raio >= ALTURA:
            self.y = ALTURA - self.raio
            self.vy = -abs(self.vy)

    def desenhar(self, superficie):
        pygame.draw.circle(superficie, self.cor, (int(self.x), int(self.y)), self.raio)


# 3. Física da colisão
def resolver_colisao(b1, b2):
    dx = b2.x - b1.x
    dy = b2.y - b1.y
    distancia = math.sqrt(dx**2 + dy**2)
    soma_raios = b1.raio + b2.raio

    # Verifica se houve colisão e evita divisão por zero se estiverem no mesmo ponto
    if distancia < soma_raios and distancia > 0:
        # Vetor normal unitário (aponta do centro de b1 para o centro de b2)
        nx = dx / distancia
        ny = dy / distancia

        # Separa as bolas caso tenham se sobreposto
        sobreposicao = soma_raios - distancia
        b1.x -= nx * (sobreposicao / 2)
        b1.y -= ny * (sobreposicao / 2)
        b2.x += nx * (sobreposicao / 2)
        b2.y += ny * (sobreposicao / 2)

        # Velocidade relativa projetada na direção da normal
        dvx = b2.vx - b1.vx
        dvy = b2.vy - b1.vy
        vel_normal = dvx * nx + dvy * ny

        # Calcula a troca de momento se as bolas estiverem se aproximando
        if vel_normal < 0:
            impulso = -(2 * vel_normal) / (1 / b1.massa + 1 / b2.massa)

            b1.vx -= (impulso / b1.massa) * nx
            b1.vy -= (impulso / b1.massa) * ny
            b2.vx += (impulso / b2.massa) * nx
            b2.vy += (impulso / b2.massa) * ny


# 4. Sorteio de posição e carregamento das bolas pelo arquivo de texto
def gerar_posicao_aleatoria(raio, bolas_existentes, x_fixo=None, y_fixo=None):
    for _ in range(1000):  # Limite de tentativas para evitar loop infinito
        x = x_fixo if x_fixo is not None else random.uniform(raio, LARGURA - raio)
        y = y_fixo if y_fixo is not None else random.uniform(raio, ALTURA - raio)

        sobreposta = False
        for outra in bolas_existentes:
            dx = outra.x - x
            dy = outra.y - y
            distancia = math.sqrt(dx**2 + dy**2)
            if distancia < raio + outra.raio:
                sobreposta = True
                break

        if not sobreposta:
            return x, y

    return x, y  # Se a tela estiver lotada após 1000 tentativas, devolve a última


def carregar_bolas(nome_arquivo):
    bolas = []
    raio_maximo = min(LARGURA, ALTURA) / 2

    # Se o arquivo não estiver na pasta atual do terminal, procura na mesma pasta do código .py
    if not os.path.exists(nome_arquivo):
        pasta_do_codigo = os.path.dirname(os.path.abspath(__file__))
        nome_arquivo = os.path.join(pasta_do_codigo, nome_arquivo)

    try:
        with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
            for num_linha, linha in enumerate(arquivo, start=1):
                linha = linha.strip()

                # Pula linhas vazias ou comentários que começam com #
                if not linha or linha.startswith("#"):
                    continue

                # Aceita vírgula ou ponto como separador decimal
                partes = linha.replace(",", ".").split()

                if len(partes) < 6:
                    print(f"Aviso (linha {num_linha}): parâmetros insuficientes, linha ignorada.")
                    continue

                try:
                    vx = float(partes[2])
                    vy = float(partes[3])
                    massa = float(partes[4])
                    raio = int(float(partes[5]))

                    x_fixo = None if partes[0].lower() == "auto" else float(partes[0])
                    y_fixo = None if partes[1].lower() == "auto" else float(partes[1])
                except ValueError:
                    print(f"Aviso (linha {num_linha}): valor numérico inválido, linha ignorada.")
                    continue

                if massa <= 0 or raio <= 0:
                    print(f"Aviso (linha {num_linha}): massa e raio devem ser maiores que zero, linha ignorada.")
                    continue

                if raio >= raio_maximo:
                    print(f"Aviso (linha {num_linha}): raio grande demais para a janela, linha ignorada.")
                    continue

                if x_fixo is None or y_fixo is None:
                    x, y = gerar_posicao_aleatoria(raio, bolas, x_fixo, y_fixo)
                else:
                    x, y = x_fixo, y_fixo

                # Sorteia uma cor viva (entre 80 e 255 para não ficar escura no fundo preto)
                cor = (
                    random.randint(80, 255),
                    random.randint(80, 255),
                    random.randint(80, 255)
                )

                bolas.append(Bola(x, y, vx, vy, massa, raio, cor))

    except FileNotFoundError:
        print(f"Erro: arquivo '{nome_arquivo}' não encontrado!")
        sys.exit()

    return bolas


# Carrega os dados antes de abrir a janela gráfica (evita janela piscando em caso de erro)
if len(sys.argv) > 1:
    arquivo_entrada = sys.argv[1]
else:
    arquivo_entrada = "parametros.txt"

bolas = carregar_bolas(arquivo_entrada)

if not bolas:
    print("Aviso: nenhuma bola válida foi carregada do arquivo.")


# 5. Inicialização do Pygame e loop principal
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Simulador de Colisões 2D")
relogio = pygame.time.Clock()

rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    # Passo 1: Move todas as bolas
    for bola in bolas:
        bola.mover(DT)

    # Passo 2: Verifica colisão entre todos os pares únicos de bolas
    for i in range(len(bolas)):
        for j in range(i + 1, len(bolas)):
            resolver_colisao(bolas[i], bolas[j])

    # Passo 3: Limpa a tela e desenha o novo estado
    tela.fill(PRETO)
    for bola in bolas:
        bola.desenhar(tela)

    pygame.display.flip()
    relogio.tick(FPS)

pygame.quit()
sys.exit()