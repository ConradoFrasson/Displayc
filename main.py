import pygame
from data_provider import DataProvider
import renderer as renderer

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FPS = 30

def _make_window(fullscreen:bool) -> pygame.Surface:
    flags = 0
    if fullscreen:
        flags |= pygame.FULLSCREEN
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        return screen

def main():
    pygame.init()
    pygame.display.set_caption("Dashboard UTForce")

    fullscreen = False
    screen = _make_window(fullscreen)

    try:
        renderer.load_assets()
    except Exception as e:
        print("Erro no load_assets:", e)

    data = DataProvider()
    clock = pygame.time.Clock()

    print("pygame display init:", pygame.display.get_init())
    print("window size:", screen.get_size())
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    screen = _make_window(fullscreen)

        data.update()
        renderer.draw_all(screen, data)

        clock.tick(FPS)
        pygame.quit()

        if __name__ == "__main__":
            main()