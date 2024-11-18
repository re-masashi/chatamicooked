import random
import sys

'''
Code by Nafi (aka re-masashi)
simple implementation for easy to remember code
'''

'''
`dictionary` is a set of words to choose from
'''
dictionary = [
    "earth",
    "tiger",
    "apple",
    "bear",
    "car",
    "fly",
    # todo: add more words
]

def game_loop(state):
    '''
    This function handles the game logic.
    it is the main game loop.

    the `state` variable must have the following attributes:
    - "secret-word"
    - "max-attempts"
    - "remaining-attempts"
    - "guessed-letters"

    absence of any of these will lead to a KeyError.

    `stages` prints the body of the hangman based on number of attempts left.

    '''
    if state is None:
        state = {
            "secret-word": random.choice(dictionary),
            "max-attempts": 6,
            "remaining-attempts": 6,
            "guessed-letters": ""
        }

    stages = [
    """
        ------
        |    |
        |
        |
        |
        |
        |
    ------------
    """, 
    """
        ------
        |    |
        |    O
        |
        |
        |
        |
    ------------
    """, 
    """
        ------
        |    |
        |    O
        |    |
        |    |
        |
        |
    ------------
    """, 
    """
        ------
        |    |
        |    O
        |    |
        |    |
        |   /
        |
    ------------
    """, 
    """
        ------
        |    |
        |    O
        |    |
        |    |
        |   / \\
        |
    ------------
    """, 
    """
        ------
        |    |
        |    O
        |  --|
        |    |
        |   / \\
        |
    ------------
    """,
    """
        ------
        |    |
        |    O
        |  --|--
        |    |
        |   / \\
        |
    ------------
    """
    ]

    if state['remaining-attempts'] <= 0:
        game_over(state)
        return False

    if len(state['guessed-letters'])==len("".join(set(state['secret-word']))) and\
        "".join(set(state['secret-word']))=="".join(set(state['secret-word'])):
        print("YAY YOU WON!!")
        return True

    guess_letter(state)

    print(stages[state['max-attempts'] - state['remaining-attempts']])
    print(f'remaining attempts: {state['remaining-attempts']}')
    print_secret(state)
    return game_loop(state)
    
def play_again_prompt():
    '''
    this function asks if the person wants to play again and starts a new game loop if the answer is yes

    Note:
    this can lead to an error when the maximum recursion depth is reached but that isn't happening in any cases less than 400 or 600 "play again" choices.
    '''
    if input("Do you want to play again?").lower().strip()=='yes' :
        print("i see that's a yes")
        game_loop(None)
    else:
        print("oh! bye! please play again")
        sys.exit(0)

def game_over(state):
    '''
    prints a game over message and asks if user wants to play again
    '''
    print(f"OH MY! YOU LOST! NOOOO! The word was `{state['secret-word']}`")
    

def print_secret(state):
    '''
    prints the secret word as a secret
    '''
    word = ""
    for letter in state['secret-word']:
        if letter in state['guessed-letters']:
            word+=letter
        else:
            word+='_'
    print(word)

def guess_letter(state):
    '''
    accepts the input letter and handles it's presence/absence in the secret word
    '''
    try:
        guess = input("Guess a letter: ").lower()
    except KeyboardInterrupt:
        print("\nquitting...")
        sys.exit()
    if len(guess) > 1 or not guess.isalpha():
        print("Only single letters are allowed. Unable to continue...")
        # sys.exit()
        guess_letter(state)
    else:
        if guess in state['secret-word']:
            # return True
            if guess in state['guessed-letters']:
                print("You have already guessed the letter {}".format(guess))
            else:
                print("Yes! The letter {} is part of the secret word".format(guess))
                state['guessed-letters'] = state['guessed-letters']+guess
        else:
            print("No! The letter {} is not part of the secret word".format(guess))
            state['remaining-attempts'] -= 1
    
if __name__ == "__main__":
    game_loop(None)
    
