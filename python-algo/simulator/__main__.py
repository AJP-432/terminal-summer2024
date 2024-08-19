import json
import pygame
from .sim_game_state import SimGameState



class Simulator:
    def __init__(self, last_action_frame: json, test: json, using_pygame: bool = False) -> None:
        self.last_action_frame = last_action_frame
        self.test = test
        self.game_state = SimGameState(self.last_action_frame, self.test)
        self.using_pygame = using_pygame

        if using_pygame:
            self.pygame_init()

    def pygame_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((700,900))
        pygame.display.set_caption("Terminal Tower Defense")
        
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
    
    def run_simulation(self) -> list[str]:
        running = True
        while running:
            if self.using_pygame:
                self.screen.fill((200, 200, 200))
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                mx, my = pygame.mouse.get_pos()
                x_index, y_index = (mx - 12)//25, 26 - (my - 50 - 12)//25
                # copilot, fix the y index so that higher on the screen is a higher y index
                print(x_index, y_index) 
            
            # if not self.game_state.is_round_over():
            if True:
                self.game_state.run_frame()
                if self.using_pygame:
                    self.game_state.draw(self.screen, self.font)
            
            if self.using_pygame:
                pygame.display.update()

        if self.using_pygame:
            pygame.quit()
        
        return self.game_state.get_results()
    
import os
if __name__ == "__main__":
    obj = {
    "turnInfo": 
    [
        1,
        2,
        57
    ],
    "p1Stats": 
    [
        22,
        12.4,
        2.3,
        52933
    ],
    "p2Stats": 
    [
        25,
        9.5,
        0.3,
        82365
    ],
    "p1Units": 
    [
        [
        ],
        [
        ],
        [
            [
                24,
                13,
                75,
                "2"
            ],
            [
                22,
                11,
                75,
                "8"
            ],
            [
                10,
                9,
                28,
                "10"
            ],
            [
                17,
                9,
                75,
                "12"
            ],
            [
                14,
                6,
                75,
                "14"
            ],
            [
                13,
                6,
                75,
                "44"
            ]
        ],
        [
        ],
        [
        ],
        [
        ],
        [
        ],
        [
        ]
    ],
    "p2Units": 
    [
        [
            [
                4,
                14,
                40,
                "51"
            ]
        ],
        [],
        [
            [
                3,
                17,
                30,
                "18"
            ],
            [
                0,
                14,
                30,
                "20"
            ],
            [
                1,
                15,
                30,
                "22"
            ],
            [
                1,
                14,
                30,
                "24"
            ],
            [
                2,
                14,
                30,
                "26"
            ],
            [
                2,
                15,
                30,
                "28"
            ],
            [
                3,
                14,
                39,
                "47"
            ],
            [
                3,
                15,
                75,
                "49"
            ]
        ],
        [
        ],
        [
        ],
        [],
        [],
        [
            [
                4,
                14,
                0,
                "52"
            ]
        ]
    ]
}
    test = {
        "p1Units": [[],[],[],[[3, 10, 12, ""]],[],[],[], []],
        "p2Units": [[],[],[],[],[],[],[],[]]
    }

    sim = Simulator(obj, test, using_pygame=True)
    results = sim.run_simulation()
    print(results)
