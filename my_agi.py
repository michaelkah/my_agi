import json
import requests

def send_llm_request(prompt, context = None):
    headers = {'Content-Type': 'application/json'}
    real_prompt = prompt + " Respond using JSON."
    payload = {
        "model": "llama3.1:latest",
        "stream": False,
        "prompt": real_prompt,
        "context": context,
        "format": "json"
    }
    print("<<< " + real_prompt)
    print()
    response = requests.post('http://localhost:11434/api/generate', headers=headers, json=payload)
    response_json = response.json()
    # print(response_json)
    print(">>> " + response_json["response"])
    print()
    print("----------------------------------------------------------------------")
    print()
    return response_json

def main():
    main_prompt = "I want to write a python program that plays tic-tac-toe in the console human vs. computer."

    first_prompt = (main_prompt +
                    " Please give me a list of names of python funtions that I have to implement including a short description."
                    " Order the list in which I should implement the functions."
                    " Example for a number guessing game:"
                    " {'functions': ["
                    " {'name': 'generate_secret_number', 'docstring': 'Generate a secret number between 1 and 100'},"
                    " {'name': 'get_user_guess', 'docstring': 'Ask the user for their guess'},"
                    " {'name': 'compare_guessed_number', 'docstring': 'Compare the user's guess with the secret number'},"
                    " {'name': 'play_game', 'docstring': 'Main loop. Play the number guessing game'}"
                    "]}\n")
    first_response = send_llm_request(first_prompt)
    first_context = first_response['context']
    functions = json.loads(first_response["response"])["functions"]

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
    main()
