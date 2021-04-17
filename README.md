# Python development case
## Prerequisites
* Python 3
* Pip
* git
## Setup
### Getting the source files
Clone the repo into the current folder
```
$ cd <path/to/destination>
$ git clone https://github.com/tomekpur/python_case.git
$ cd python_case
```

### Virtual environment
#### Creating the virtual environment
Create a project folder and a venv folder within
```
$ python3 -m venv venv
```
#### Activate the environment
Before you can continue, activate the corresponding environment
```
$ . venv/bin/activate
```

### Install dependencies
And install the required packages
```
$ pip install -r requirements.txt
```

### Set the environment variables:
Now let's get all the settings ready
```
$ export FLASK_APP=url_shortner
$ export FLASK_ENV=development
```
## Start the application
### Initialize the database
This step is only needed the first time you run the app or if you want a brand new version of the database
```
$ flask init-db
```

After doing all the above, the app is just one step away
```
$ flask run
```

## Unit testing 
###  Starting the unit test with `pytest`
Run the unit tests with the virtual environment activated
```
$ pytest
```

### Coverage reports
In order to get the `coverage` reports
```
$ coverage erase
$ coverage run -m pytest
```
Then choose one of the following
```
$ coverage report         # For simple report in console
$ coverage html           # For extensive reports (in folder 'htmlcov')
```
