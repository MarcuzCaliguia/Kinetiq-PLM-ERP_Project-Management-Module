To run:
Create virtual environment in root directory:
python -m venv venv
Activate venv in root directory:
venv\scripts\activate
Once activated, run this (venv) :
pip install -r requirements.txt
then:
cd backend
code .

run the terminal on backend dir:
python manage.py runserver

open terminal:
npm run dev

for rds:
ssh -i "<path/to/pem>" -L 15432:kinetiq-postgresql.c30ww0i2ytkm.ap-southeast-1.rds.amazonaws.com:5432 ec2-user@3.1.102.192
password is in databases section in project_management_backend.settings (required for pg admin)
Register server in pgAdmin 4 with the settinga:
Host name/address: 127.0.0.1
Port: 15432
username: postgres
*server name can be anything*



Software requirements:
Python 3.13.3

install fnm:
winget install Schniz.fnm

Node.JS
fnm install 22

