import pygame
import math
import random
import os
import time

pygame.init()
pygame.font.init()


# create window
WIDTH = 750
HEIGHT = 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Cruiser")
icon = pygame.image.load(os.path.join("assets", "icon32.png"))
pygame.display.set_icon(icon)


# load assets
BG = pygame.image.load(os.path.join("assets", "background.jpg"))
ENEMY1 = pygame.image.load(os.path.join("assets", "enemy164.png"))
ENEMY2 = pygame.image.load(os.path.join("assets", "enemy264.png"))
ENEMY3 = pygame.image.load(os.path.join("assets", "enemy364.png"))
PLAYER = pygame.image.load(os.path.join("assets", "player64.png"))
BULLET1 = pygame.image.load(os.path.join("assets", "bullet1.png"))
BULLET2 = pygame.image.load(os.path.join("assets", "bullet2.png"))
BULLET3 = pygame.image.load(os.path.join("assets", "bullet3.png"))
BULLET_PLAYER = pygame.image.load(os.path.join("assets", "bullet_player.png"))
TITLE = pygame.transform.scale(pygame.image.load(os.path.join("assets", "title64.png")), (600, 300))
START_BTN = pygame.image.load(os.path.join("assets", "start32.png"))
QUIT_BTN = pygame.image.load(os.path.join("assets", "quit32.png"))


# Health attributes
HEALTH_1 = 50
HEALTH_2 = 75
HEALTH_3 = 100
HEALTH_PLAYER = 100

class Bullet:

    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, speed):
        self.y += speed 

    def out_of_bounds(self):
        if (self.y > HEIGHT or self.y < 0 - 20):
            return True
        return False

    def collision(self, obj):
        return collide(self, obj)
    

class Ship:
    COOLDOWN = 30   

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = []
        self.cooldown = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)

    def draw_bullets(self, window):
        for bullet in self.bullets:
            bullet.draw(window)
        
    def cooldown_check(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        
    def shoot(self):
        if self.cooldown == 0:
            bullet = Bullet(self.x - 20, self.y - 50, self.bullet_img)
            self.bullets.append(bullet)
            self.cooldown = self.COOLDOWN

    def move_bullets(self, speed, obj):
        self.cooldown_check()
        for bullet in self.bullets:
            bullet.move(speed)
            if bullet.out_of_bounds():
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                obj.health -= 10
                self.bullets.remove(bullet)

    def get_height(self):
        return self.ship_img.get_height()

    def get_width(self):
        return self.ship_img.get_width()


class Player(Ship):

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = PLAYER
        self.bullet_img = BULLET_PLAYER
        self.max_health = HEALTH_PLAYER
        self.mask = pygame.mask.from_surface(self.ship_img)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.get_height() + 10, self.get_width(), 5))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.get_height() + 10, self.get_width() * (self.health / self.max_health), 5))

    def move_bullets(self, speed, objs):
        self.cooldown_check()
        for bullet in self.bullets:
            bullet.move(speed)
            if bullet.out_of_bounds():
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj) and not(obj.dead):
                        obj.health -= 30
                        if obj.health <= 0:
                            obj.dead = True
                            # objs.remove(obj)
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
        

class Enemy(Ship):

    # Dictionary for types of enemies
    TYPE_MAP = {
        "1": (ENEMY1, HEALTH_1, BULLET1),  
        "2": (ENEMY2, HEALTH_2, BULLET2),
        "3": (ENEMY3, HEALTH_3, BULLET3),
    }

    def __init__(self, x, y, ship_type, health=50):
        super().__init__(x, y, health)
        self.ship_img, self.health, self.bullet_img = self.TYPE_MAP[ship_type]
        self.max_health = self.health
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.dead = False

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.get_height() + 10, self.get_width(), 3))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.get_height() + 10, self.get_width() * (self.health / self.max_health), 3))

    def move(self, speed):
        self.y += speed

    def shoot(self):
        if self.cooldown == 0:
            bullet = Bullet(self.x - 20, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cooldown = self.COOLDOWN


# check if actual objects are colliding, not just the boxes
def collide(object1, object2):
    offset_x = object2.x - object1.x 
    offset_y = object2.y - object1.y
    return object1.mask.overlap(object2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    player_speed = 6
    enemy_speed = 2
    bullet_speed = 5
    wave_size = 0
    wave = 0
    lives = 3

    # fonts 
    main_font = pygame.font.SysFont("comicsans", 40)
    lost_font = pygame.font.SysFont("comicsans", 80)

    # BG scroller attributes
    bgY = 0
    bgY2 = BG.get_height() * -1

    enemies = []
    player = Player(343, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0, bgY))
        WIN.blit(BG, (0, bgY2))

        # labels
        lives_label = main_font.render(f"LIVES: {lives}", True, (255, 255, 255))
        wave_label = main_font.render(f"WAVE: {wave}", True, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(wave_label, (WIDTH - wave_label.get_width() - 10, 10))

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("GAME OVER", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
        
        for enemy in enemies:
            if not(enemy.dead):
                enemy.draw(WIN)
            else:
                enemy.draw_bullets(WIN)

        pygame.display.update()


    # main game loop
    while run:
        clock.tick(FPS)

        if player.health <= 0:
            if lives > 1:
                lives -= 1
                player.health = player.max_health
            elif lives == 1:
                lives = 0

        if lives <= 0:
            redraw_window()
            lost = True
            lost_count += 1

        # pause the game for 3s when lost
        if lost:
            if lost_count > 3 * FPS:
                run = False
            else:
                continue

        # scroll BG
        bgY += 1
        bgY2 += 1

        if bgY > BG.get_height():
            bgY = BG.get_height() * -1
        if bgY2 > BG.get_height():
            bgY2 = BG.get_height() * -1

        redraw_window()

        # check if no enemies left and add new wave
        if len(enemies) == 0:
            wave += 1
            wave_size += 2
            for i in range(wave_size):
                enemy = Enemy(random.randrange(20, WIDTH - 70), random.randrange(-1500, -100), random.choice(["1", "2", "3"]))
                enemies.append(enemy)
        
          # check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        # keybinds and border checking
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_speed > 0:
            player.x -= player_speed
        if keys[pygame.K_d] and player.x + player_speed + player.get_width() < WIDTH:
            player.x += player_speed
        if keys[pygame.K_w] and player.y - player_speed > 0:
            player.y -= player_speed
        if keys[pygame.K_s] and player.y + player_speed + player.get_height() < HEIGHT:
            player.y += player_speed
        if keys[pygame.K_SPACE]:
            player.shoot()

        # take a copy of enemies list in case of any changes
        for enemy in enemies[:]:
            enemy.move(enemy_speed)
            enemy.move_bullets(bullet_speed, player)

            # probability that enemy will shoot every sec
            if not(enemy.dead):
                if random.randrange(0, 2*60) == 1:
                    enemy.shoot()

                # player collides with enemies
                if collide(enemy, player):
                    player.health -= 20
                    enemy.dead = True
                elif enemy.y + enemy.get_height() > HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                enemies.remove(enemy)

        player.move_bullets(-bullet_speed, enemies)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 100)
    quit = False
    while not(quit):
        WIN.blit(BG, (0,0))
        WIN.blit(TITLE, (WIDTH/2 - TITLE.get_width()/2, 30))

        # store the (x,y) pos of the cursor
        mouse = pygame.mouse.get_pos()

        # start button
        START_X1 = WIDTH/2 - START_BTN.get_width()/2
        START_X2 = WIDTH/2 + START_BTN.get_width()/2
        START_Y1 = 425
        START_Y2 = 425 + START_BTN.get_height()

        # cursor hover over button
        if (START_X1 <= mouse[0] <= START_X2) and (START_Y1 <= mouse[1] <= START_Y2):
           WIN.blit(START_BTN, (WIDTH/2 - START_BTN.get_width()/2, 430))
        else:
            WIN.blit(START_BTN, (WIDTH/2 - START_BTN.get_width()/2, 425))

        # quit button
        QUIT_X1 = WIDTH/2 - QUIT_BTN.get_width()/2
        QUIT_X2 = WIDTH/2 + QUIT_BTN.get_width()/2
        QUIT_Y1 = 525
        QUIT_Y2 = 525 + QUIT_BTN.get_height()

        if (QUIT_X1 <= mouse[0] <= QUIT_X2) and (QUIT_Y1 <= mouse[1] <= QUIT_Y2):
            WIN.blit(QUIT_BTN, (WIDTH/2 - QUIT_BTN.get_width()/2, 530))
        else:
            WIN.blit(QUIT_BTN, (WIDTH/2 - QUIT_BTN.get_width()/2, 525))


        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if (QUIT_X1 <= mouse[0] <= QUIT_X2) and (QUIT_Y1 <= mouse[1] <= QUIT_Y2):
                    quit = True
                elif (START_X1 <= mouse[0] <= START_X2) and (START_Y1 <= mouse[1] <= START_Y2):
                    main()

main_menu()
