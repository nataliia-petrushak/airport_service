# AirPro API
API service for cinema management written on DRF

## Features
- JWT authentication
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/
- Managing orders and tickets
- Creating routes, flights with crews
- Creating airplanes
- Filtering flights and routes

### Installing using GitHub
Install PostgresSQL and create db

```shell
git clone https://github.com/nataliia-petrushak/airport_service.git
cd airport_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
set POSTGRES_HOST=<your db hostname>
set POSTGRES_DB=<your db name>
set POSTGRES_USER=<your db username>
set POSTGRES_PASSWORD=secretpassword
=<your db password>
set SECRET_KEY=<your secret key>
python manage.py migrate
python manage.py runserver
```
### Run with docker
Docker should be installed

```shell
docker-compose build
docker-compose up
```

### Getting access
- create user via /api/user/register
- get access token via /api/user/token/

### Getting started
- Download [ModHeader](https://chrome.google.com/webstore/detail/modheader-modify-http-hea/idgpnmonknjnojddfkpgkljpfnnfcklj?hl=en)
- Add name and token
- Now you are authorised and can use the API

### DB Structure
![img.png](img.png)
