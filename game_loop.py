import json
import queue
import threading
import uuid

import pygame

import client
import resources


class Game:
    WIDTH = 800
    HEIGHT = 600
    FPS = 60

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    SKY_BLUE = (61, 224, 219)

    def __init__(self):
        pygame.init()

        self.background = resources.Background()
        self.foreground = resources.Foreground(8)
        self.player = resources.Player(True)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.start_screen = resources.StartScreen()
        pygame.display.set_caption("Fluffy Duck")
        self.clock = pygame.time.Clock()
        self.client_uuid = uuid.uuid4().__str__()
        self.client_status = "lobby"
        self.multiplayer = False
        self.q_to_send = queue.Queue()
        self.q_to_receive = queue.Queue()
        self.players_data = {}

    def loop(self):
        game_pending = False
        running = True

        while running:
            print(self.q_to_send.qsize(), self.q_to_receive.qsize())
            delta_time = self.clock.tick(self.FPS) / 1000

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    self.client_status = "quit"
                if not game_pending and event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE and self.multiplayer is False:
                        game_pending = True
                        self.client_status = "fly"
                    elif event.key == pygame.K_m and self.multiplayer is False:
                        self.multiplayer = True
                        self.foreground.clear_map()
                        send_message_th = threading.Thread(target=client.run_client,
                                                           args=(self.q_to_send, self.q_to_receive, self.client_uuid))
                        send_message_th.start()
                    elif event.key == pygame.K_r and self.multiplayer:
                        self.client_status = "ready"

            # Aktualizacja logiki gry
            if game_pending is True:
                self.player.tick(delta_time, events)
                self.foreground.tick(self.player, events, delta_time)
                if self.foreground.f_line_tick(self.player):
                    game_pending = "end"
                    self.client_status = "end"
            if self.multiplayer:
                for player in self.players_data.values():
                    player.tick(delta_time, events)

                if self.q_to_send.qsize() == 0:
                    client_data = {"uuid": self.client_uuid,
                                   "status": self.client_status,
                                   "x": round(self.foreground.player_x),
                                   "y": round(self.player.y),
                                   "ver_velocity": round(self.player.ver_velocity, 2),
                                   "hor_velocity": round(self.foreground.player_vel, 2)}
                    self.q_to_send.put(json.dumps(client_data))
                while self.q_to_receive.qsize() > 0:
                    response = self.q_to_receive.get()
                    if "the_map" in response:
                        self.foreground.load_map(**response["the_map"])
                    if "server_info" in response and "status" in response["server_info"]:
                        self.client_status = response["server_info"]["status"]
                    players_dicts = response.get("new_mess")
                    if players_dicts is None:
                        continue

                    # print(players_dicts)
                    for player_dict in players_dicts:
                        player_obj: resources.Player = self.players_data.get(player_dict.get("uuid"))
                        if player_obj is not None:
                            if "status" in player_dict:
                                # print(player_dict["x"], self.player.x, self.player.X, end="    ")
                                player_obj.refresh_pos(
                                    player_dict["x"] - self.foreground.player_x + self.player.X,
                                    player_dict["y"],
                                    player_dict["ver_velocity"],
                                )
                        elif player_dict.get("uuid") is not None:
                            this_uuid = player_dict["uuid"]
                            self.players_data[this_uuid] = resources.Player(uuid=this_uuid)
                            print("Nowy gracz")

            # Renderowanie
            self.screen.fill(self.SKY_BLUE)
            self.background.draw(self.screen)
            self.foreground.draw(self.screen)
            self.player.draw(self.screen)
            for player_obj in self.players_data.values():
                player_obj.draw(self.screen)
                # print(player_obj.x, player_obj.y)
            if not game_pending:
                self.start_screen.draw(self.screen, self.multiplayer)
                if self.multiplayer and self.client_status == "set":
                    cd = self.start_screen.draw_countdown(self.screen, delta_time)
                    if cd:
                        self.client_status = "fly"
                        game_pending = True
            pygame.display.flip()

        pygame.quit()
