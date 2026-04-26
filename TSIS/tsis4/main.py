# main.py

from db import create_tables
from game import SnakeGame


def main():
    create_tables()
    game = SnakeGame()
    game.run()


if __name__ == "__main__":
    main()