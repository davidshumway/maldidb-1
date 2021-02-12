## Overview
- Mass data import from SQLite
- Search and browse data
- User and group management 
- Pipelines:
    - Bin peaks and cosine scoring for search and dendrograms
    - Replicates to collapsed spectra
    - Preprocessing
    - Upload spectra files

## Docker install with docker-compose
```bash
 git clone https://github.com/davidshumway/maldidb
 cd ./maldidb/
 # Use project.env.template to create project.env
 cp project.env.template project.env
```

Edit project.env to include the following:

    POSTGRES_USER=<database user>
    POSTGRES_PASSWORD=<database password>
    POSTGRES_DB=<database name>
    DATABASE=postgres
    DATABASE_HOST=postgresdb
    DATABASE_PORT=5432
    SECRET_KEY=<any key>

Update docker-compose.yaml to point to R01 data files, if present, or
remove the R01 volume, if not present:

```bash
  - /home/ubuntu/r01data:/home/app/r01data/
```

Finally, build and run the project:

```bash
docker-compose up --build
```
PostgreSQL does not need to be installed on the system beforehand unless performing a manual installaion.

Running `docker-compose up --build` the first time may take 15-30 minutes to complete. However, successive
builds should complete within 15-30 seconds.

## Manual install
### Install prerequisites
- R
- IDBacApp (R library)
- PostgreSQL
    - Run `psql` and create an initial database:
```bash
 CREATE DATABASE <database>;
 CREATE USER <user> WITH PASSWORD '<password>';
 ALTER ROLE <user> SET client_encoding TO 'utf8';
 ALTER ROLE <user> SET default_transaction_isolation TO 'read committed';
 ALTER ROLE <user> SET timezone TO 'UTC';
 GRANT ALL PRIVILEGES ON DATABASE <database> TO <user>;
```

### Clone repository and start a test server
```bash
 git clone https://github.com/davidshumway/maldidb
 cd ./maldidb
 # Use project.env.template to create project.env
 # and input settings used in psql. 
 # DATABASE_HOST should be set to "localhost"
 # rather than postgresdb.
 cp project.env.template project.env
 nano project.env
 # Initialize environment variables and virtualenv
 source project.env
 sudo pip3 install virtualenv
 virtualenv venv -p python3
 source venv/bin/activate
 cd ./maldidb
 pip install -r requirements.txt
 # Run server
 python manage.py makemigrations
 python manage.py migrate
```

In `maldidb/soMedia/settings.py`, set `Debug = False`.

Execute `python manage.py runserver` to run the project.
The site should now be available in a browser at `http://localhost:8000/`.

A graph diagram of the application's models may be generated
using ```./manage.py graph_models -a -g -o models.png```.

