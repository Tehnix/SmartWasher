# SmartWasher
Smart scheduling for washing machines. Check out the [Demo Presentation](static/Demo Presentation.pdf), for a better overview.

## Get Started

#### Dependencies
First, set up the system dependencies,

```bash
$ pip install virtualenv
$ brew install mysql # or sudo apt-get install mysql-server libmysqlclient-dev
```

Now you can setup the project dependencies in a virtual environment,

```bash
$ virtualenv .venv && source .venv/bin/activate
$ pip install -r requirements.txt
```

#### Database
You can now set up your database in MySQL. First, start the MySQL server,

```
$ mysql.server start
```

Now you can connect with,

| Configuration | Value     |
| --------------|-----------|
| username      | root      |
| password      |           |
| host          | 127.0.0.1 |

Create a database `smartwasher`, and execute the SQL from the `SmartWasher Original Data (Cleaned).sql` file.

#### Running the Application
To run the server (assuming you're still in the virtualenv),

```bash
$ python main.py
```

You can then manipulate the data via the `cli.py` app,

```bash
$ python cli.py
Choose an action:
    1: Simulate silent state
    2: Simulate running state
    3: Simulate running state with steps
    4: Reset steps
    q: quit
>> 2
Adding running data
...
```
