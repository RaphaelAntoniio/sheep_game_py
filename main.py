import pygame
import random
import time
import sys
import os

# Função para obter o caminho correto para os recursos (imagens, etc.)
def resource_path(relative_path):
    """ Retorna o caminho absoluto para o recurso, seja no script ou no exe. """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# Inicialização do Pygame
pygame.init()

# Configuração da tela
janela = pygame.display.set_mode([960, 540])
pygame.display.set_caption('First Game')

# Configuração do jogador
player_y_pos = 430
player_x_pos = 390
player_sheep_speed = 10

# Configuração dos inimigos
enemy_speed = 2  # Velocidade dos inimigos

# Configuração de tiros
player_shoots = []  # Lista para armazenar os tiros do jogador
enemy_shoots = []  # Lista para armazenar os tiros dos inimigos
shoot_speed = 5
last_shoot_time = 0
shoot_interval = 1   # Intervalo de tiro em segundos

# Contador de fases
fase = 1
font = pygame.font.Font(None, 36)  # Fonte padrão com tamanho 36

# Inicialização das imagens
imagem_fundo = pygame.image.load(resource_path('img/space bg game.png'))
nave_player = pygame.image.load(resource_path('img/sprite_nave_pequena.png'))
nave_enemy = pygame.image.load(resource_path('img/nave_inimiga_pequena.png'))
shoot = pygame.image.load(resource_path('img/missil_pequeno.png'))
life = pygame.image.load(resource_path('img\life_player.jpg'))

# Transformar imagens para ajustar o tamanho
shoot = pygame.transform.scale(shoot, (30, 30))
life = pygame.transform.scale(life, (50, 50))

# Função para gerar inimigos
def gerar_inimigos(fase_atual):
    num_enemies = 1 + (fase_atual - 1) * 2
    # Cada inimigo agora tem sua própria variável last_shoot_time
    return [{"x": random.randint(0, 910), "y": random.randint(-200, 0), "last_shoot_time": 0} for _ in range(num_enemies)]

# Gerar os inimigos iniciais
enemies = gerar_inimigos(fase)

# Adiciona as três vidas no canto inferior direito
vidas = 3
life_width, life_height = 50, 50  # Dimensões da imagem "life"
spacing = 10  # Espaço entre as vidas

# Transformar imagens para ajustar o tamanho
life = pygame.transform.scale(life, (life_width, life_height))

# Loop principal do jogo
loop = True
while loop:

    for events in pygame.event.get():
        if events.type == pygame.QUIT:
            loop = False

    # Controle do jogador
    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_UP]:
        player_y_pos -= player_sheep_speed
    if teclas[pygame.K_DOWN]:
        player_y_pos += player_sheep_speed
    if teclas[pygame.K_LEFT]:
        player_x_pos -= player_sheep_speed
    if teclas[pygame.K_RIGHT]:
        player_x_pos += player_sheep_speed

    # Atirar (player)
    current_time = time.time()
    if teclas[pygame.K_SPACE] and current_time - last_shoot_time >= shoot_interval:
        player_shoots.append({"x": player_x_pos + 22, "y": player_y_pos})
        last_shoot_time = current_time

    # Correção de posição do jogador para ficar dentro da tela
    if player_x_pos < 0:
        player_x_pos = 960
    if player_x_pos > 960:
        player_x_pos = 0
    if player_y_pos < 0:
        player_y_pos = 540
    if player_y_pos > 540:
        player_y_pos = 0

    # Atualizar posição dos inimigos
    for enemy in enemies:
        enemy["y"] += enemy_speed
        if enemy["y"] > 540:  # Reaparece no topo após sair da tela
            enemy["y"] = -20
            enemy["x"] = random.randint(0, 960)

        # Atirar (inimigo)
        if current_time - enemy["last_shoot_time"] >= shoot_interval:
            enemy_shoots.append({"x": enemy["x"] + 15, "y": enemy["y"] + 30})
            enemy["last_shoot_time"] = current_time

    # Atualizar posição dos tiros do jogador
    for shoot_obj in player_shoots[:]:
        shoot_obj["y"] -= shoot_speed
        if shoot_obj["y"] < 0:
            player_shoots.remove(shoot_obj)

    # Atualizar posição dos tiros dos inimigos
    for shoot_obj in enemy_shoots[:]:
        shoot_obj["y"] += shoot_speed
        if shoot_obj["y"] > 540:
            enemy_shoots.remove(shoot_obj)

    # Detectar colisões (tiro do jogador com inimigos)
    for enemy in enemies[:]:
        enemy_rect = pygame.Rect(enemy["x"], enemy["y"], 50, 50)
        for shoot_obj in player_shoots[:]:
            shoot_rect = pygame.Rect(shoot_obj["x"], shoot_obj["y"], 15, 30)
            if enemy_rect.colliderect(shoot_rect):
                enemies.remove(enemy)
                player_shoots.remove(shoot_obj)

    # Detectar colisões (tiro dos inimigos com o jogador)
    player_rect = pygame.Rect(player_x_pos, player_y_pos, 50, 50)
    for shoot_obj in enemy_shoots[:]:
        shoot_rect = pygame.Rect(shoot_obj["x"], shoot_obj["y"], 15, 30)
        if player_rect.colliderect(shoot_rect):
            vidas -= 1
            enemy_shoots.remove(shoot_obj)
            if vidas == 0:
                print("Game Over!")
                loop = False

    # Verificar se todos os inimigos foram destruídos
    if not enemies:
        fase += 1
        enemies = gerar_inimigos(fase)

    # Desenhar o contador de fases
    fase_texto = font.render(f"Fase: {fase}", True, (255, 255, 255))  # Texto branco
    janela.blit(imagem_fundo, (0, 0))
    janela.blit(fase_texto, (10, 10))  # Posição do texto no canto superior esquerdo

    # Exibição das imagens
    janela.blit(nave_player, (player_x_pos, player_y_pos))

    for enemy in enemies:
        janela.blit(nave_enemy, (enemy["x"], enemy["y"]))

    for shoot_obj in player_shoots:
        janela.blit(shoot, (shoot_obj["x"], shoot_obj["y"]))

    for shoot_obj in enemy_shoots:
        janela.blit(shoot, (shoot_obj["x"], shoot_obj["y"]))

    # Desenhar as vidas no canto inferior direito
    for i in range(vidas):
        x_pos = 960 - (life_width + spacing) * (i + 1)  # Posição da vida ajustada
        y_pos = 540 - life_height - spacing  # Altura fixa
        janela.blit(life, (x_pos, y_pos))

    pygame.display.update()
