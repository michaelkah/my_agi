import json
import requests


def send_llm_request(prompt, context=None, json=False):
    headers = {'Content-Type': 'application/json'}
    real_prompt = prompt
    payload = {
        "model": "llama3.1:8b",
        # "model": "llama3.2:1b",
        "stream": False,
        "prompt": real_prompt,
        "context": context
    }

    if json:
        real_prompt = real_prompt + "\nRespond using JSON."
        payload['format'] = 'json'

    print("<<< " + real_prompt)
    print()
    # server = 'http://localhost:11434/api/generate'
    server = 'http://10.11.2.5:11434/api/generate'
    response = requests.post(server, headers=headers, json=payload)
    response_json = response.json()
    # print(response_json)
    print(">>> " + response_json["response"])
    print()
    print("----------------------------------------------------------------------")
    print()
    return response_json


def main(main_prompt):
    first_example_python = """
import random

def get_user_guess():
    # Prompts the user for their guess and returns it as an integer.

def generate_computer_number():
    # Generates a random number between 1 and 100 and returns it.

def check_guess(user_guess, computer_number):
    # Compares the user's guess to the computer's number and provides feedback (higher, lower, correct).

def play_game():
    # Manages the game flow: getting guesses, checking them, and determining the winner.
    """

    first_example_json = { 'main_code': first_example_python }

    first_prompt = (main_prompt +
                    "\n\nGive me an outline of the code that contains only method headers."
                    " Example for a number guessing game:"
                    "\n\n# BEGIN OF EXAMPLE\n\n"
                    + json.dumps(first_example_json) +
                    "\n\n# END OF EXAMPLE"
                    "\n\nGive me only the code."
                    )
    first_response = send_llm_request(first_prompt, json=True)
    first_context = first_response['context']
    main_code = json.loads(first_response["response"])["main_code"]



def second(main_prompt):
    # second_prompt = main_prompt + " These are the steps I have identified: " + json.dumps(response.response_text['response']) + ". Do you think they are reasonable? Give me an improved list of steps." + " Respond using JSON"
    # response_second_api_call = send_llm_request(second_prompt)
    # response2 = json.loads(response_second_api_call.response_text['response'])
    # print(response2)
    # steps2 = response2['steps']
    # print(steps2)

    for func in functions:
        func_prompt = ("Given the following function: " + str(func) + "\n"
                                                                      " Which parameter(s) and return value(s) would be reasonable for this function?"
                                                                      " Example answer for a different function:\n"
                                                                      "{"
                                                                      "'params': [{'user_guess': 'int'}, {'secret_number': 'int'}],"
                                                                      "'return_value': 'bool'"
                                                                      "}\n")
        func_response = send_llm_request(func_prompt, first_context)
        func_context = func_response['context']

        impl_prompt = ("Implement the function.")
        impl_response = send_llm_request(impl_prompt, func_context)


if __name__ == '__main__':
    main("I want to write a python program that plays tic-tac-toe in the console human vs. computer.")
