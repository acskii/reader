# comfy reader
'An app that contains manga and stories from my sources in one place!'

## Table of Contents
- **<h3><a href="#introduction">Introduction</a></h3>**
- **<h3><a href="#python-set-up">Python Setup</a></h3>**
- **<h3><a href="#set-up">Set-up</a></h3>**
- **<h3><a href="#running">Running Project</a></h3>**
- **<h3><a href="#admin-user">Creating an Admin User</a></h3>**

## Introduction
### This is a Django application
> [!IMPORTANT]
>It is crucial to be mindful of this fact. 
>
>Thus, the user is recommended to be of some basic knowledge of the Django framework, and Python basics to operate this app.

### External caching server is used (Redis)
> [!IMPORTANT]
>A local hosted Redis server was used during development, and thus this app only works is one is setup
>
>It is neccesary to know how to setup and use a basic Redis server.
>
>This is mentioned in the <a href="#set-up">set-up</a> section.

## Python Set-up
>[!NOTE]
>This app supports Python version **3.10** and above.

>[!NOTE]
>Make sure to install PIP alongside Python. 
>
>Verify by typing `pip --version` OR `pip3 --version` in the command line/Linux terminal

Here are instructions for installation on a **Windows** and a **Linux** machine.
### Windows
1) Visit [**python.org**][1] downloads.
2) Download any Python version from 3.10 and **above**.
>[!TIP]
>Download stable releases to avoid unexpected behaviour.
3) To make sure that Python downloaded correctly:
    - Open up command line, search up **cmd** to open.
    - Type this in the command line:

        ```
        > python
        ```

        If this doesn't work, explicitly type the Python version you downloaded

        ```
        > python{version-here}
        ```
        **OR**
        ```
        > python3
        ```

    - The interactive Python shell should open in the command line, if it does then Python is installed correctly.
    - Press **CTRL-C** to close the shell.

### Linux
#### Install using APT installer
1) Open the Linux Terminal by pressing **CTRL-ALT-T** & execute the following Linux Command that will update all the packages installed there.

    ```
    $ sudo apt update
    ```

2) Directly paste the following command in the Terminal & execute it. This will download the Python File

    ```
    $ sudo apt install python[version number]
    ```

3) To make sure that Python downloaded correctly:
    - Open up terminal, press **CTRL-ALT-T** to open.
    - Type this in the terminal line:

        ```
        $ python3
        ```

        If this doesn't work, explicitly type the Python version you downloaded

        ```
        $ python{version-here}
        ```

    - The interactive Python shell should open in the terminal, if it does then Python is installed correctly.
    - Press **CTRL-C** to close the shell.

4) Install PIP
    - Type this in the terminal line:

        ```
        $ sudo apt update
        $ sudo apt install python3-pip
        ```

## Set-up
### Installations
**Firstly,** install Python interpretor *<a href="#python-set-up">here</a>* \
**Secondly,** set-up a *virtual environment* for the project.

- Type in terminal/command line:
    ```
    $ pip3 install virtualenv
    ```

    - If this doesn't work, follow the steps in this [**website**][2]
    
- Create a new virtual environment:
```
$ virtualenv --python3 [name-of-env-here]
```

- To activate the environment in the *current* terminal:
```
$ source [name-of-env-here]/bin/activate
```

**Thirdly,** start up a new Django project to clone the repository in.

- To do so, we need to install Django package in our current environment
>[!IMPORTANT]
>Make sure that you're within the virtual environment

```
(env-name)$ pip3 install Django
```
- If you encounter any issues, visit the official [**Django installation guide**][3]

- Start a new Django project:
    - Navigate to the directory that you want the project to be contained in
    - Then, type this in the terminal/command line:
        ```
        $ django-admin startproject [project-name-here]
        ```
    - Navigate into the project:
        ```
        $ cd [project-name-here]
        ```
**Fourthly,** clone the repository into the newly-created project.
- If you haven't installed GIT, then please do so.
    - Follow the steps mentioned [here for Windows][4], or [here for Linux][5]

- Clone the repository (Example using SSH)
```
(env-name)$ git clone git@github.com:acskii/comfy-reader.git
```

**Fifthly,** install Redis.
- Follow the steps [here for Windows][6], or [here for Linux][7]

**Lastly,** install requirements and dependancies
- Assuming that you are *in the **project directory***, type in terminal/command line:
    ```
    (env-name)$ pip3 install -r requirements.txt
    ```

### Settings
1) Navigate to `reader/`, and open up `settings.py` in a code editor of your choice.
2) There are **three** that need to be checked
    - **Database**

        During development, the app used a **local SQLITE3** database, which could be left unchanged. \
        Another option is to replace the information in this section to accomodate a cloud database e.g. Postgre server \
        Instructions on how to setup a cloud database with be added soon, but if you already have previous knowledge on this technology then feel free to implement it.

    - **Caching**

        After running a Redis server (instructions found <a href="#running">here</a>), add in the local address and port in this setting.
        ``` python
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': 'redis://127.0.0.1:6379',       # change based on local host 'redis://{host}:{port}'
            }
        }
        ```
        >[!IMPORTANT]
        >**DON'T** use browser cache/cookies, as cache data is larger than the maximum limit of **>4KB**\
        >Redis was the solution to this problem.

    
    - **Internationalization**

        Edit the `TIME_ZONE` variable into your prefered timezone.

<h4>You are now ready to <a href="#running">run</a> the application!</h4>

## Running
1) Start up the Redis server
- If **local**, type in terminal line:
```
$ sudo systemctl start redis-server
```
>[!NOTE]
> To close the local server:
>  `$ sudo systemctl start redis-server`

2) Assuming that you are *in the **project directory***, type in the terminal/command line:
```
(env-name)$ python3 manage.py runserver
```

3) Open up your browser, and type in the URL provided in the terminal screen (*usually* 127.0.0.1:8000)

<h4>And.. Done! App is now running!</h4>

## Admin User
Assuming that you are *in the **project directory***, type in the terminal/command line:
```
(env-name)$ python3 manage.py createsuperuser
```
Type in your username, email, and password.\
You can use them to login on the app.

[1]: https://www.python.org/downloads/windows/
[2]: https://virtualenv.pypa.io/en/latest/installation.html#via-pip
[3]: https://docs.djangoproject.com/en/5.1/topics/install/#installing-an-official-release-with-pip
[4]: https://git-scm.com/downloads/win
[5]: https://git-scm.com/downloads/linux
[6]: https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-windows/
[7]: https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/install-redis-on-linux/