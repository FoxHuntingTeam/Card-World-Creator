import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = str(os.getenv("BOT_TOKEN"))

ABOUT_MESSAGE = ("This program was created to help you create cards in the NACAMA CARD, Viresets Card bots.\n\n"
                "Created by _White Fox")

HELP_MESSAGE = (f"This program was created to help you create cards in the NACAMA CARD, Viresets Card bots.\n\n"
                f"To start making cards you need to create a project with the number and type of cards you will make. After that, select this project.\n"
                f"!!!WARNING. If there are no changes, restart the program.\n"
                f"In the Statistics tab, you can find out how many cards have been created and how many more are needed.\n"
                f"In the Maps tab, you can create the maps themselves, view the data in the table, change these data, and also create txt files of your maps. The files are created in the project folder\n"
                f"When you have the cards ready, go to the Photoshop tab and adjust the frame for Photoshop, each frame must be saved. There is no save message. Both frame and background maps must be 825 x 1250.")