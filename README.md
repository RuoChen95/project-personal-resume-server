# project-personal-resume-server
It's a Flask app coded by Ruochen Xie, which has the function of CRUD the resume data and show the data in the form of JSON. The front-end project is here: https://github.com/RuoChen95/project-personal-resume

This is a personal project.

*STATUS: Unfinished*

## Example of output
If running locally, it's a website which has a url: http://0.0.0.0:5001/.

## Design of the code
 1. connect db
 2. define router
 2. define session
 3. execute sql using session
 4. show the data to front end in JSON

## Improvements
 1. Implement a decorator function to check user login status
 2. Implement the ON DELETE CASCADE

## How to run it

### Setup Project:
  1. Install [Vagrant](https://www.vagrantup.com/) and [VirtualBox](https://www.virtualbox.org/)
  2. Download or Clone [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository. The file have a directory called vagrant.
  3. Put the project and the vangrant setup file into the same directory.
  
### Launching the Virtual Machine:
  1. Launch the Vagrant VM inside Vagrant sub-directory in the downloaded fullstack-nanodegree-vm repository using command:

  ```
    $ vagrant up
  ```
  2. Then Log into this using command:
  
  ```
    $ vagrant ssh
  ```
  3. Change directory to /vagrant and look around with ls. (*如果出现文件无法同步的情况，尝试使用vagrant reload排查错误*)
  
### Setting up the Database:

  You can use the personalResume.db directly or using the following command to creat a clean personalResume.db:

  1. Create the database using the command:`python database_setup.py`
  2. Use `python setResume.py` to populate the database
  
  The database includes two tables which can be observed through database_setup.py:
  * The PersonName table includes the name and id.
  * The ResumeItem table includes the type, id, content, personName_id.
  
### Set up
  The web server contains four features:

  1. The CRUD of personName table
  2. The CRUD of resumeItem table
  3. Return menu info using JSON
  4. authentication of github account

  run it using 
  ```
    python __init__.py
  ```

## Application Code Style

  Passing the pycodestyle (`pycodestyle --first webserverUsingFlask.py`) checking.