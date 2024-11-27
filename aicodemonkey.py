from dotenv import load_dotenv
import os
import requests
from ollama import generate

main_prompt = ("""
                add a new rest endpoint to vsent.
                parameters for the endpoint: string name.
                return value: boolean whether the string is longer than 3 chars or not.
                name of the endpoint: strlen
                """)

def search_gitlab_projects(search_string):
    headers = {
        "Private-Token": os.getenv("GITLAB_ACCESS_TOKEN")
    }
    params = {
        "search": search_string
    }
    gitlab_base_url = os.getenv("GITLAB_BASE_URL")
    url = f"{gitlab_base_url}/api/v4/projects"
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        projects = response.json()
        
        # Extract project names
        project_names = [project['name'] for project in projects]
        return project_names

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

def clone(repo):
    pass
    # git clone https://<your-access-token>@gitlab.com/<namespace>/<repository>.git

def extract_project_name(main_prompt):
    response = generate(model='llama3.1', system='You are a helpful software developer. A coworker asks you to make some changes to a certain project. What is the name of the project? You answer only with the name of the project and nothing else.', prompt=main_prompt)
    print(f">>> {response['response']}")
    return response['response']

def extract_tasks(main_prompt):
    response = generate(model='llama3.1', system='You are a helpful software developer. A coworker asks you to make some changes to a certain project. What changes does the coworker want to make?', prompt=main_prompt)
    print(f">>> {response['response']}")
    return response['response']

if __name__ == "__main__":
    load_dotenv()
    project_name = extract_project_name(main_prompt=main_prompt)
    print(search_gitlab_projects(search_string=project_name))
    print(extract_tasks(main_prompt=main_prompt))
