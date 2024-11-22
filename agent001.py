import json
import requests


def send_llm_request(prompt, context=None, json=True):
    headers = {'Content-Type': 'application/json'}
    real_prompt = prompt
    payload = {
        # "model": "llama3.1:8b",
        # "model": "llama3.2:1b",
        "model": "llama3.1:latest",
        "stream": False,
        "prompt": real_prompt,
        "context": context
    }

    if json:
        real_prompt = real_prompt + "\nRespond using JSON."
        payload['format'] = 'json'

    print("<<< " + real_prompt)
    print()
    server = 'http://localhost:11434/api/generate'
    # server = 'http://10.11.2.5:11434/api/generate'
    response = requests.post(server, headers=headers, json=payload)
    # print("RAWDOG RESPONSE: " + str(response))
    response_json = response.json()
    print(">>> " + response_json["response"])
    print()
    print("----------------------------------------------------------------------")
    print()
    return response_json


def main():
    main_prompt = "I want to write a python program that plays tic-tac-toe in the console human vs. computer."

    outline_code, outline_context = outline(main_prompt)
    function_names, function_list_context = function_list(outline_context)

    for function_name in function_names:
        code = implement_function(function_name, function_list_context)
        exec(code)


def outline(main_prompt):
    example_response = """
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
    prompt = (main_prompt +
                    "\n\nGive me an outline of the code that contains only method headers."
                    " Example for a number guessing game:"
#                    "\n\n# BEGIN OF EXAMPLE\n\n"
                    + json.dumps({ 'code': example_response }) +
#                   "\n\n# END OF EXAMPLE"
                    "\n\nGive me only the code."
                    )
    response = send_llm_request(prompt)
    context = response['context']
    code = json.loads(response["response"])["code"]
    return code, context


def function_list(outline_context):
    prompt = ("Give me a list of all the functions I have to implement."
              "\n\nExample: " + json.dumps({ 'function_list': ['get_user_guess', 'generate_computer_number', 'check_guess', 'play_game'] }) +
              "\n\nGive me only the list.")
    response = send_llm_request(prompt, context = outline_context)
    context = response['context']
    function_list = json.loads(response["response"])["function_list"]
    return function_list, context


def implement_function(function_name, function_list_context):
    example_response = """
def hello_world():
    print("Hello, World!")
"""

    prompt = ("Implement the function '" + function_name + "' from the above list."
              "\n\nExample: "
              + json.dumps({ 'code': example_response }) +
              "\n\nGive me only the code.")
    response = send_llm_request(prompt, context = function_list_context)
    code = json.loads(response["response"])["code"]
    return code


if __name__ == '__main__':
    main()
