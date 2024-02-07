# Reservation Bot

Place a reservation for High Point University's fine dining restaurants

## Usage

To use this program you must first install python for your machine's operating system.  
You can download python from the following link: <https://www.python.org/downloads/>  

To confirm you have installed python, open a terminal (Mac) or command prompt (Windows)  
and type the following command:

```bash
python --version
```

If you have it installed, it should tell you what version of python you are running.  

Next, navigate to the directory where you want to install this repository.  
All users have the Documents/ directory by default but not the programs/ directory. If  
you want to create the programs directory to store this project you can first navigate  
to the Documents/ directory and then create the directory using the following commands:  

```bash
cd Documents
mkdir programs
cd programs
```

Once you are in the directory where you want to install this project, clone the project
repository to your local machine using the following command:

```bash
git clone https://github.com/matthewjburton/reservation-bot
```

After you've cloned the repository, you need to set up your settings that govern  
your reservation details as well as your credentials.  

Create an .env file to manage the configuration for your reservation. You can create and
open this file by running:

```bash
vi .env
```

With the file open, press the i key to enter insert mode. Enter the following information but  
be sure to replace the placeholder text with the information that matches your credentials  
and reservation details.  

```py
USERNAME='username'       # Your HPU username
PASSWORD='password'       # Your HPU password
PHONE='5555555555'        # Youre phone number (all ten digits)
RESTAURANT='Prime'        # Prime, Alo, or Kazoku
GUESTS='6'                # Prime: 1-6, Alo: 1-4, Kazoku: 1-10
TIME='17:30'              # Preferred time of reservation between 16:30 - 20:30 (military time)
```

Press escape to exit insert mode, then save and exit this file by typing:

```bash
:wq
```

This project relies on certain dependencies that require you to download them before it will  
work properly. We will use pip to install these dependencies, so let's check if you have pip  
installed by running the following command:

```bash
pip --version
```

If you see a version number you can proceed to installing the dependencies. However, if pip is not  
installed you will need to download it by running the following command:

```bash
wget https://bootstrap.pypa.io/get-pip.py
```

Now, you should have pip installed, so we can install the dependencies for the project. Run:

```bash
pip install -r requirements.txt
```

Finally, you have everything installed to run the reservation bot. Execute the program by running  
the following command:

```bash
python3 reserve.py
```

Assuming you provided valid input in your .env file, nothing should happen in your terminal  
because the program is wait for midnight to attempt to make a reservation. Leave your computer  
on and charging to gaurantee it will continue running until midnight.
