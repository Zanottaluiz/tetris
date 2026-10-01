import pygame
import random
import sys

pygame.init()

# ---------------------- CONFIGURAÇÕES ----------------------
LARGURA_TELA = 800
ALTURA_TELA = 720

COLUNAS = 10
LINHAS = 20
TAMANHO_BLOCO = 30

LARGURA_TABULEIRO = COLUNAS * TAMANHO_BLOCO
ALTURA_TABULEIRO = LINHAS * TAMANHO_BLOCO

X_TABULEIRO = 230
Y_TABULEIRO = 60

FPS = 60

tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Tetris em Python")

relogio = pygame.time.Clock()

fonte_titulo = pygame.font.SysFont("arial", 42, bold=True)
fonte_media = pygame.font.SysFont("arial", 25, bold=True)
fonte_pequena = pygame.font.SysFont("arial", 18)

# Cores
FUNDO = (20, 23, 32)
TABULEIRO_FUNDO = (30, 35, 48)
LINHA_GRADE = (55, 62, 80)
BRANCO = (245, 245, 245)
CINZA = (170, 175, 185)
PRETO = (10, 10, 10)

# Cores das peças: I, J, L, O, S, T, Z
CORES = [
    (0, 220, 230),    # Ciano: I
    (60, 90, 230),    # Azul: J
    (255, 150, 35),   # Laranja: L
    (245, 220, 45),   # Amarelo: O
    (55, 205, 95),    # Verde: S
    (180, 70, 220),   # Roxo: T
    (235, 65, 65)     # Vermelho: Z
]

# Formatos das sete peças. Cada número é uma rotação possível.
PECAS = [
    # I
    [
        ["....",
         "1111",
         "....",
         "...."],

        ["..1.",
         "..1.",
         "..1.",
         "..1."]
    ],

    # J
    [
        ["1..",
         "111",
         "..."],

        [".11",
         ".1.",
         ".1."],

        ["...",
         "111",
         "..1"],

        [".1.",
         ".1.",
         "11."]
    ],

    # L
    [
        ["..1",
         "111",
         "..."],

        [".1.",
         ".1.",
         ".11"],

        ["...",
         "111",
         "1.."],

        ["11.",
         ".1.",
         ".1."]
    ],

    # O
    [
        ["11",
         "11"]
    ],

    # S
    [
        [".11",
         "11.",
         "..."],

        [".1.",
         ".11",
         "..1"]
    ],

    # T
    [
        [".1.",
         "111",
         "..."],

        [".1.",
         ".11",
         ".1."],

        ["...",
         "111",
         ".1."],

        [".1.",
         "11.",
         ".1."]
    ],

    # Z
    [
        ["11.",
         ".11",
         "..."],

        ["..1",
         ".11",
         ".1."]
    ]
]


def desenhar_texto(texto, fonte, cor, x, y, centralizado=False):
    """Desenha um texto na tela."""
    imagem = fonte.render(texto, True, cor)
    retangulo = imagem.get_rect()

    if centralizado:
        retangulo.center = (x, y)
    else:
        retangulo.topleft = (x, y)

    tela.blit(imagem, retangulo)


def escurecer(cor, fator=0.65):
    """Retorna uma versão mais escura de uma cor RGB."""
    return (
        int(cor[0] * fator),
        int(cor[1] * fator),
        int(cor[2] * fator)
    )


def criar_tabuleiro():
    """Cria uma matriz vazia de 20 linhas por 10 colunas."""
    return [[None for _ in range(COLUNAS)] for _ in range(LINHAS)]


def nova_peca():
    """Sorteia uma peça e a coloca no topo, centralizada."""
    indice = random.randrange(len(PECAS))
    formato = PECAS[indice][0]

    return {
        "indice": indice,
        "rotacao": 0,
        "x": COLUNAS // 2 - len(formato[0]) // 2,
        "y": 0
    }


def formato_atual(peca):
    """Retorna a matriz de texto equivalente à rotação atual."""
    return PECAS[peca["indice"]][peca["rotacao"]]


def posicoes_blocos(peca, rotacao=None):
    """
    Devolve todas as posições ocupadas pela peça.
    Cada item retornado é uma tupla (x, y).
    """
    if rotacao is None:
        rotacao = peca["rotacao"]

    formato = PECAS[peca["indice"]][rotacao]
    blocos = []

    for linha, texto in enumerate(formato):
        for coluna, valor in enumerate(texto):
            if valor == "1":
                x = peca["x"] + coluna
                y = peca["y"] + linha
                blocos.append((x, y))

    return blocos


def posicao_valida(tabuleiro, peca, dx=0, dy=0, rotacao=None):
    """Verifica se uma peça pode ocupar uma nova posição."""
    for x, y in posicoes_blocos(peca, rotacao):
        novo_x = x + dx
        novo_y = y + dy

        if novo_x < 0 or novo_x >= COLUNAS:
            return False

        if novo_y >= LINHAS:
            return False

        if novo_y >= 0 and tabuleiro[novo_y][novo_x] is not None:
            return False

    return True


def fixar_peca(tabuleiro, peca):
    """Transforma a peça ativa em blocos permanentes do tabuleiro."""
    for x, y in posicoes_blocos(peca):
        if y >= 0:
            tabuleiro[y][x] = peca["indice"]


def limpar_linhas(tabuleiro):
    """
    Remove linhas cheias, desloca as demais para baixo
    e retorna a quantidade de linhas apagadas.
    """
    linhas_restantes = [
        linha for linha in tabuleiro
        if any(celula is None for celula in linha)
    ]

    linhas_removidas = LINHAS - len(linhas_restantes)

    while len(linhas_restantes) < LINHAS:
        linhas_restantes.insert(0, [None for _ in range(COLUNAS)])

    for y in range(LINHAS):
        tabuleiro[y] = linhas_restantes[y]

    return linhas_removidas


def desenhar_bloco(coluna, linha, cor, deslocamento_x=0, deslocamento_y=0, tamanho=TAMANHO_BLOCO):
    """Desenha um bloco com aparência levemente tridimensional."""
    x = deslocamento_x + coluna * tamanho
    y = deslocamento_y + linha * tamanho

    retangulo = pygame.Rect(x, y, tamanho, tamanho)

    pygame.draw.rect(tela, cor, retangulo)
    pygame.draw.rect(tela, escurecer(cor), retangulo, 2)

    brilho = (
        min(cor[0] + 55, 255),
        min(cor[1] + 55, 255),
        min(cor[2] + 55, 255)
    )

    pygame.draw.line(
        tela,
        brilho,
        (x + 3, y + 3),
        (x + tamanho - 4, y + 3),
        2
    )

    pygame.draw.line(
        tela,
        brilho,
        (x + 3, y + 3),
        (x + 3, y + tamanho - 4),
        2
    )


def desenhar_tabuleiro(tabuleiro):
    """Desenha o fundo, a grade e os blocos fixos."""
    fundo = pygame.Rect(
        X_TABULEIRO,
        Y_TABULEIRO,
        LARGURA_TABULEIRO,
        ALTURA_TABULEIRO
    )

    pygame.draw.rect(tela, TABULEIRO_FUNDO, fundo)

    # Grade
    for coluna in range(COLUNAS + 1):
        x = X_TABULEIRO + coluna * TAMANHO_BLOCO
        pygame.draw.line(
            tela,
            LINHA_GRADE,
            (x, Y_TABULEIRO),
            (x, Y_TABULEIRO + ALTURA_TABULEIRO)
        )

    for linha in range(LINHAS + 1):
        y = Y_TABULEIRO + linha * TAMANHO_BLOCO
        pygame.draw.line(
            tela,
            LINHA_GRADE,
            (X_TABULEIRO, y),
            (X_TABULEIRO + LARGURA_TABULEIRO, y)
        )

    # Blocos já fixados
    for linha in range(LINHAS):
        for coluna in range(COLUNAS):
            indice_cor = tabuleiro[linha][coluna]

            if indice_cor is not None:
                desenhar_bloco(
                    coluna,
                    linha,
                    CORES[indice_cor],
                    X_TABULEIRO,
                    Y_TABULEIRO
                )

    pygame.draw.rect(tela, BRANCO, fundo, 3)


def desenhar_peca(peca):
    """Desenha a peça que o jogador está controlando."""
    cor = CORES[peca["indice"]]

    for x, y in posicoes_blocos(peca):
        if y >= 0:
            desenhar_bloco(x, y, cor, X_TABULEIRO, Y_TABULEIRO)


def desenhar_proxima_peca(peca):
    """Desenha a prévia da próxima peça na área lateral."""
    painel_x = 570
    painel_y = 210
    tamanho = 24

    pygame.draw.rect(
        tela,
        TABULEIRO_FUNDO,
        (painel_x, painel_y, 150, 130),
        border_radius=8
    )

    pygame.draw.rect(
        tela,
        LINHA_GRADE,
        (painel_x, painel_y, 150, 130),
        2,
        border_radius=8
    )

    formato = formato_atual(peca)
    cor = CORES[peca["indice"]]

    largura_formato = len(formato[0]) * tamanho
    altura_formato = len(formato) * tamanho

    inicio_x = painel_x + (150 - largura_formato) // 2
    inicio_y = painel_y + (130 - altura_formato) // 2

    for linha, texto in enumerate(formato):
        for coluna, valor in enumerate(texto):
            if valor == "1":
                x = inicio_x + coluna * tamanho
                y = inicio_y + linha * tamanho

                retangulo = pygame.Rect(x, y, tamanho, tamanho)
                pygame.draw.rect(tela, cor, retangulo)
                pygame.draw.rect(tela, escurecer(cor), retangulo, 2)


def desenhar_interface(pontuacao, linhas, nivel, proxima, pausado=False):
    """Desenha título, estatísticas, controles e peça seguinte."""
    desenhar_texto(
        "TETRIS",
        fonte_titulo,
        BRANCO,
        LARGURA_TELA // 2,
        26,
        centralizado=True
    )

    desenhar_texto("PONTOS", fonte_pequena, CINZA, 570, 75)
    desenhar_texto(str(pontuacao), fonte_media, BRANCO, 570, 100)

    desenhar_texto("LINHAS", fonte_pequena, CINZA, 570, 135)
    desenhar_texto(str(linhas), fonte_media, BRANCO, 570, 160)

    desenhar_texto("NÍVEL", fonte_pequena, CINZA, 570, 195)
    desenhar_texto(str(nivel), fonte_media, BRANCO, 570, 220)

    desenhar_texto("PRÓXIMA", fonte_pequena, CINZA, 570, 250)
    desenhar_proxima_peca(proxima)

    desenhar_texto("CONTROLES", fonte_pequena, CINZA, 570, 380)

    controles = [
        "← →  Mover",
        "↓  Descer",
        "↑ / X  Girar",
        "Espaço  Queda",
        "P  Pausar",
        "R  Reiniciar",
        "ESC  Sair"
    ]

    for indice, texto in enumerate(controles):
        desenhar_texto(
            texto,
            fonte_pequena,
            BRANCO,
            570,
            410 + indice * 31
        )

    if pausado:
        camada = pygame.Surface((LARGURA_TABULEIRO, ALTURA_TABULEIRO), pygame.SRCALPHA)
        camada.fill((0, 0, 0, 180))
        tela.blit(camada, (X_TABULEIRO, Y_TABULEIRO))

        desenhar_texto(
            "PAUSADO",
            fonte_titulo,
            BRANCO,
            X_TABULEIRO + LARGURA_TABULEIRO // 2,
            Y_TABULEIRO + ALTURA_TABULEIRO // 2 - 20,
            centralizado=True
        )

        desenhar_texto(
            "Pressione P para continuar",
            fonte_pequena,
            CINZA,
            X_TABULEIRO + LARGURA_TABULEIRO // 2,
            Y_TABULEIRO + ALTURA_TABULEIRO // 2 + 30,
            centralizado=True
        )


def queda_sombra(tabuleiro, peca):
    """Calcula quantas células a peça cairia até tocar em algo."""
    distancia = 0

    while posicao_valida(tabuleiro, peca, dy=distancia + 1):
        distancia += 1

    return distancia


def desenhar_sombra(tabuleiro, peca):
    """Mostra uma sombra indicando o local onde a peça irá cair."""
    distancia = queda_sombra(tabuleiro, peca)
    cor = CORES[peca["indice"]]

    cor_sombra = (
        max(25, cor[0] // 3),
        max(25, cor[1] // 3),
        max(25, cor[2] // 3)
    )

    for x, y in posicoes_blocos(peca):
        y += distancia

        if y >= 0:
            retangulo = pygame.Rect(
                X_TABULEIRO + x * TAMANHO_BLOCO + 5,
                Y_TABULEIRO + y * TAMANHO_BLOCO + 5,
                TAMANHO_BLOCO - 10,
                TAMANHO_BLOCO - 10
            )
            pygame.draw.rect(tela, cor_sombra, retangulo, 2)


def nova_partida():
    """Prepara todos os valores necessários para iniciar uma partida."""
    tabuleiro = criar_tabuleiro()
    peca_atual = nova_peca()
    proxima_peca = nova_peca()

    return {
        "tabuleiro": tabuleiro,
        "peca": peca_atual,
        "proxima": proxima_peca,
        "pontuacao": 0,
        "linhas": 0,
        "nivel": 1,
        "pausado": False,
        "game_over": False,
        "ultimo_movimento": pygame.time.get_ticks()
    }


def travar_e_criar_proxima(estado):
    """Fixa a peça, remove linhas completas e cria a próxima."""
    tabuleiro = estado["tabuleiro"]
    peca = estado["peca"]

    fixar_peca(tabuleiro, peca)

    apagadas = limpar_linhas(tabuleiro)

    # Pontuação clássica aproximada, multiplicada pelo nível
    tabela_pontos = {
        0: 0,
        1: 100,
        2: 300,
        3: 500,
        4: 800
    }

    estado["pontuacao"] += tabela_pontos[apagadas] * estado["nivel"]
    estado["linhas"] += apagadas
    estado["nivel"] = estado["linhas"] // 10 + 1

    estado["peca"] = estado["proxima"]
    estado["proxima"] = nova_peca()

    # Se a peça nova não couber, a partida termina
    if not posicao_valida(tabuleiro, estado["peca"]):
        estado["game_over"] = True


def intervalo_queda(nivel):
    """
    Retorna o tempo, em milissegundos, entre quedas automáticas.
    O limite inferior evita que a velocidade fique impossível.
    """
    return max(90, 700 - (nivel - 1) * 55)


def tela_game_over(estado):
    """Exibe a tela final e espera o jogador reiniciar ou sair."""
    while True:
        tela.fill(FUNDO)

        desenhar_texto(
            "GAME OVER",
            fonte_titulo,
            (245, 80, 80),
            LARGURA_TELA // 2,
            230,
            centralizado=True
        )

        desenhar_texto(
            f"Pontuação: {estado['pontuacao']}",
            fonte_media,
            BRANCO,
            LARGURA_TELA // 2,
            310,
            centralizado=True
        )

        desenhar_texto(
            f"Linhas removidas: {estado['linhas']}",
            fonte_pequena,
            CINZA,
            LARGURA_TELA // 2,
            350,
            centralizado=True
        )

        desenhar_texto(
            "Pressione R ou ENTER para jogar novamente",
            fonte_pequena,
            BRANCO,
            LARGURA_TELA // 2,
            430,
            centralizado=True
        )

        desenhar_texto(
            "ESC para sair",
            fonte_pequena,
            CINZA,
            LARGURA_TELA // 2,
            465,
            centralizado=True
        )

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_r, pygame.K_RETURN):
                    return

                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        relogio.tick(FPS)


def jogar():
    """Executa uma partida de Tetris."""
    estado = nova_partida()

    while not estado["game_over"]:
        agora = pygame.time.get_ticks()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if evento.key == pygame.K_r:
                    return

                if evento.key == pygame.K_p:
                    estado["pausado"] = not estado["pausado"]
                    estado["ultimo_movimento"] = pygame.time.get_ticks()
                    continue

                if estado["pausado"]:
                    continue

                peca = estado["peca"]
                tabuleiro = estado["tabuleiro"]

                if evento.key == pygame.K_LEFT:
                    if posicao_valida(tabuleiro, peca, dx=-1):
                        peca["x"] -= 1

                elif evento.key == pygame.K_RIGHT:
                    if posicao_valida(tabuleiro, peca, dx=1):
                        peca["x"] += 1

                elif evento.key == pygame.K_DOWN:
                    if posicao_valida(tabuleiro, peca, dy=1):
                        peca["y"] += 1
                        estado["pontuacao"] += 1

                elif evento.key in (pygame.K_UP, pygame.K_x):
                    total_rotacoes = len(PECAS[peca["indice"]])
                    nova_rotacao = (peca["rotacao"] + 1) % total_rotacoes

                    # Rotação básica com pequenas tentativas laterais
                    if posicao_valida(tabuleiro, peca, rotacao=nova_rotacao):
                        peca["rotacao"] = nova_rotacao

                    elif posicao_valida(tabuleiro, peca, dx=-1, rotacao=nova_rotacao):
                        peca["x"] -= 1
                        peca["rotacao"] = nova_rotacao

                    elif posicao_valida(tabuleiro, peca, dx=1, rotacao=nova_rotacao):
                        peca["x"] += 1
                        peca["rotacao"] = nova_rotacao

                elif evento.key == pygame.K_SPACE:
                    distancia = queda_sombra(tabuleiro, peca)
                    peca["y"] += distancia
                    estado["pontuacao"] += distancia * 2
                    travar_e_criar_proxima(estado)
                    estado["ultimo_movimento"] = pygame.time.get_ticks()

        # Queda automática
        if not estado["pausado"]:
            agora = pygame.time.get_ticks()

            if agora - estado["ultimo_movimento"] >= intervalo_queda(estado["nivel"]):
                if posicao_valida(
                    estado["tabuleiro"],
                    estado["peca"],
                    dy=1
                ):
                    estado["peca"]["y"] += 1
                else:
                    travar_e_criar_proxima(estado)

                estado["ultimo_movimento"] = agora

        # Desenho da tela
        tela.fill(FUNDO)
        desenhar_tabuleiro(estado["tabuleiro"])

        if not estado["pausado"]:
            desenhar_sombra(estado["tabuleiro"], estado["peca"])
            desenhar_peca(estado["peca"])

        desenhar_interface(
            estado["pontuacao"],
            estado["linhas"],
            estado["nivel"],
            estado["proxima"],
            estado["pausado"]
        )

        pygame.display.update()
        relogio.tick(FPS)

    tela_game_over(estado)


# ---------------------- LOOP PRINCIPAL ----------------------
while True:
    jogar()