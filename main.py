import socket
import threading
import time
import json
import select

import tkinter
import Chatter

# GLOBAL VARIABLES

try:
    G = Chatter.Game()
except ConnectionRefusedError:
    print("[-] Server is not active, please turn it on")
    quit()

L = Chatter.DesktopApplication.Login()
L.run()

client = Chatter.Client(L.name)
print(f'Client created with name of {client.name}')


win_count = 0

class NumpadWindow():
    def __init__(self, GameInstance : Chatter.Game):

        self.window_width = 470
        self.window_height = 550

        self.message = ""
        self.gameInstance = GameInstance
        self.payload = json.loads(self.gameInstance.connection.recv())
        print(self.payload)
        self.equation = self.payload["question"]

        self.main_window = tkinter.Tk()

        self.waitingMessage = tkinter.StringVar()
        self.waitingMessage.set("Waiting for the server...")
        self.winningCountMessage = tkinter.StringVar()
        self.winningCountMessage.set(f'You have won {win_count} times')
        self.currentAnswerMessage = tkinter.StringVar()
        self.currentAnswerMessage.set(f'Current answer: {self.message}')
        self.currentEquationMessage = tkinter.StringVar()
        self.currentEquationMessage.set(f'Current equation: {self.equation}')

        self.main_window.title("Math Game")
        self.main_window.resizable(width = False, height = False)
        self.main_window.configure(width = self.window_width, height = self.window_height)

        self.waitingLabel = tkinter.Label(self.main_window, textvariable = self.waitingMessage, font = "100")
        self.waitingLabel.place(relwidth = 1, y = 20)

        self.wincountLabel = tkinter.Label(self.main_window, textvariable = self.winningCountMessage, font = "100")
        self.wincountLabel.place(relwidth = 1)

        self.currentResponse = tkinter.Label(self.main_window, textvariable = self.currentAnswerMessage, font = "100")
        self.currentResponse.place(relwidth = 1, y = 40)

        self.questionLabel = tkinter.Label(self.main_window, textvariable = self.currentEquationMessage, font = "100")
        self.questionLabel.place(relwidth = 1, y = 60)
        # BUTTON SETTINGS
        self.numpadVerticalOffset = 100
        self.numpadButtonHeight = 50
        self.numpadButtonFont = "14"
        self.numpadButtonWidth = self.window_width / 3

        buttons = [self.make_button(element) for element in range(1, 10)]
        buttons.append(self.make_button(0))

        self.submit_button = tkinter.Button(self.main_window, text="Submit", command = self.send_func)
        self.delete_button = tkinter.Button(self.main_window, text="Delete", command = self.delete_last_char)
        self.refresh_button = tkinter.Button(self.main_window, text="Refresh", command = self.refresh_screen)

        x_pos, y_pos = 0, 0
        for x, button in enumerate(buttons):
            if(x % 3 == 0 and x > 0):
                x_pos = 0
                y_pos+=1
            button.place(x = x_pos * self.numpadButtonWidth if x_pos > 0 else x_pos,
                         y = self.numpadVerticalOffset + (self.numpadButtonHeight * y_pos),
                         width = self.numpadButtonWidth,
                         height = self.numpadButtonHeight
                        )
            x_pos+=1

        self.submit_button.place(x = 0,
                                 y = self.numpadVerticalOffset + self.numpadButtonHeight * (y_pos + 1),
                                 width = self.numpadButtonWidth,
                                 height = self.numpadButtonHeight
                                )
        self.delete_button.place(x = self.numpadButtonWidth,
                                 y = self.numpadVerticalOffset + self.numpadButtonHeight * (y_pos + 1),
                                 width = self.numpadButtonWidth,
                                 height = self.numpadButtonHeight
                                )
        self.refresh_button.place(x = self.numpadButtonWidth + 1,
                                 y = self.numpadVerticalOffset + self.numpadButtonHeight * (y_pos + 1),
                                 width = self.numpadButtonWidth,
                                 height = self.numpadButtonHeight
                                )

    def make_button(self, index):
        return tkinter.Button(self.main_window, font = self.numpadButtonFont, text = str(index), command = lambda : self.append_message(str(index)))
    def run(self):
        self.main_window.mainloop()

    def append_message(self, message):
        self.message+=message
        self.currentAnswerMessage.set(f'Current answer: {self.message}')

    def delete_last_char(self):
        if not(self.message):
            return
        container = list(self.message)
        container.pop()
        self.message = ''.join(container)
        self.currentAnswerMessage.set(f'Current answer: {self.message}')

    def send_func(self):
        outbound = {
            "name": client.name,
            "answer": self.message
        }
        dumped = json.dumps(outbound)
        print(dumped)
        self.gameInstance.connection.send(dumped)

    def refresh_screen(self):
        print(self.gameInstance.connection.recv())

N = NumpadWindow(G)
N.run()