# aicodemonkey

from pprint import pprint
from textwrap import dedent

def run_command(command):
  import subprocess
  
  print("> " + command)
  result = subprocess.run(
    command,
    shell=True,
    check=False,
    text=True,
    stdout=subprocess.PIPE,  # Explicitly capture stdout
    stderr=subprocess.STDOUT  # Redirect stderr to stdout
  )
  # print(result.stdout)
  print("Return Code: ", result.returncode)
  return result.returncode, result.stdout


def build_project():
  return run_command("export PATH=/usr/local/opt/openjdk/bin:$PATH; cd my_workspace; ./mvnw clean verify")


def list_files():
  return run_command("cd my_workspace; tree -af --gitignore")


def write_files(pathname, content):
    from pathlib import Path

    base_folder = "my_workspace"

    # Create a Path object for the base folder
    base_path = Path(base_folder)
    
    # Convert the pathname into a Path object
    pathname = Path(pathname)
    
    # If pathname is absolute, make it relative to the base_folder
    if pathname.is_absolute():
        pathname = pathname.relative_to(pathname.anchor)

    # Construct the full path by combining the base folder and (possibly adjusted) pathname
    full_path = base_path / pathname
    
    print("> writing ", full_path)

    # Ensure the pathname does not navigate outside the base_folder
    if ".." in full_path.parts:
        raise ValueError("Pathname must not navigate outside the base folder ('..').")

    # Create the parent directories if they don't exist
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write the string to the file
    with full_path.open('w') as file:
        file.write(content)
    
    return 0, "File successfully written"


def read_files(pathname):
    from pathlib import Path

    base_folder = "my_workspace"

    # Create a Path object for the base folder
    base_path = Path(base_folder)
    
    # Convert the pathname into a Path object
    pathname = Path(pathname)
    
    # If pathname is absolute, make it relative to the base_folder
    if pathname.is_absolute():
        pathname = pathname.relative_to(pathname.anchor)

    # Construct the full path by combining the base folder and (possibly adjusted) pathname
    full_path = base_path / pathname

    print("> reading ", full_path)

    # Ensure the pathname does not navigate outside the base_folder
    if ".." in full_path.parts:
        raise ValueError("Pathname must not navigate outside the base folder ('..').")

    with open(full_path, 'r') as file:
        file_content = file.read()

    return 0, file_content


def main():
  import ollama
  
  #  model  = "llama3.2:3b"
  model  = "llama3.1:8b"

  messages = [
    {"role": "system", "content": dedent(
       """\
        You are a senior software developer.
        You and a coworker are working on an existing software project.
        You have to make certain changes to the project.
        First, have a look at the files and directories in the project.
        Then, decide which file(s) you want to create or update.
        You can always read the existing files so that you know how the project is being implemented.
        Adhere to the existing structure and style.
        Implement the requested change(s) and also write some tests.
        Before you start, build the project to see if it works in your environment.
        If there are any errors during the build, try to fix them.
        You are given a list of tools you can call to make the requested changes.
        Call only one tool at a time.
        Before you finish, build the project to ensure that everything still works.
        Think carefully!
        """)},
    {"role": "user", "content": "Make the following changes to the project: Implement a new method that adds to integers."},
  ]
  pprint(">>> " + str(messages))

  for i in range(5):
    response = ollama.chat(
      model=model,
      messages=messages,
      tools=[
        {
          'type': 'function',
          'function': {
            'name': 'list_files',
            'description': 'list all files and directories in the project',
          },
        },
        {
          'type': 'function',
          'function': {
            'name': 'build_project',
            'description': 'build the project',
          },
        },
        {
          'type': 'function',
          'function': {
            'name': 'write_files',
            'description': 'create or update one or more files',
            'parameters': {
                'type': 'object',
                'properties': {
                  'files': {
                    'type': 'list',
                    'description': 'a list of pairs containing the pathname of the file and the new file content, e.g. [("folder/file.txt", "content of this file"),]',
                  },
                },
                'required': ['files',],
            },
          },
        },
        {
          'type': 'function',
          'function': {
            'name': 'read_files',
            'description': 'read the content of one or more files',
            'parameters': {
                'type': 'object',
                'properties': {
                  'files': {
                    'type': 'list',
                    'description': 'a list of pathnames of the files to read',
                  },
                },
                'required': ['files',],
            },
          },
        },
      ],
    )
    pprint("<<< " + str(response['message']))

    # Check if the model decided to use a provided function
    if not response['message'].get('tool_calls'):
      print(">>> FINISHED <<<")
      return

    # Add the model's response to the conversation history
    messages.append(response['message'])

    # Process function calls made by the model
    if response['message'].get('tool_calls'):
      available_functions = {
        'build_project': build_project,
        "list_files": list_files,
        "write_files": write_files,
        "read_files": read_files,
      }
      for tool in response['message']['tool_calls']:
        function_to_call = available_functions[tool['function']['name']]
        return_code, output = function_to_call(**tool['function']['arguments'])
        # Add function response to the conversation
        messages.append(
          {
            'role': 'tool',
            'content': output,
          }
        )


if __name__ == "__main__":
  main()
