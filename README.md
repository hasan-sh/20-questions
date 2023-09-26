# 20-questions
This repository is dedicated to our thesis project of the bachelor degree 2022, Vrije Universiteit.



## play.py

This file (`play.py`) is used to start the game. It can be executed through the command line and accepts several optional arguments for easier execution.

### Arguments:

- `-q` : Specifies which bot to play against. The options are "Entropy", "Base", or "Random". More bots are available in different branches. 
- `-o` : Specifies if the opponent is a human or not. The options are "True" or "False".
- `-d` : Sets the development mode. When in development mode, questions and answers are printed.
- `-url` : Specifies the URL of the dataset to use. This dataset should be running on a local server.

## tournament.py

This file (`tournament.py`) is used to start the game. It can be executed through the command line and accepts several optional arguments for easier execution.

### Arguments:

- `-r` : Specifies the number of repetitions.
- `-p` : Specifies which bot to play against. The options are "Entropy", "Base", or "Random". More bots are available in different branches. 
- `-url` : Specifies the URL of the dataset to use. This dataset should be running on a local server.

## Prerequisites

Before running the files, make sure you have the required dependencies installed. Please refer to the documentation for more information.

## Running the Game

To start the game, run the following command:

```
python play.py [arguments]
```

To start a tournament, run the following command:

```
python tournament.py [arguments]
```

Replace `[arguments]` with the desired arguments based on the options mentioned above.
