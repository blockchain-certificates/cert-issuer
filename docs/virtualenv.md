# Python virtual environment

We recommend using virtualenv [details](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for your python development. 
 
1. Ensure virtualenv is installed
   ```bash
   pip install virtualenv

 # below code does not work with ubuntu 16.04.
 # pip -p python3 virtualenv // for python 3
 
 
   ```
2. Create a virtualenv for your project
   ```bash
   virtualenv -p python3 $project_home
   
 #  OR
   
   cd $project_home
   virtualenv venv
   ```

3. Activate the environment
   ```bash
   source ./venv/bin/activate
   ```
4. After you're finished, deactivate the environment by running
   ```bash
   deactivate
   ```
