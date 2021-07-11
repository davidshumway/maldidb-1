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
 git clone https://github.com/idbac/maldidb
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

Add R01 data files, if present, to a new folder in `./mdb` titled `r01data`:

```bash
mkdir ./mdb/r01data
```

Add NCBI taxonomy data files (available from https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/) `nodes.dmp` and `names.dmp`, if present, to the same `r01data` folder.

Finally, build and run the project:

```bash
docker-compose up --build
```
PostgreSQL does not need to be installed on the system beforehand unless performing a manual installaion.

Running `docker-compose up --build` the first time may take 15-30 minutes to complete. However, successive
builds should complete within 15-30 seconds.

When the build is finished, the site processes will start, including Django.
When Django runs for the first time, the first time that NCBI taxonomy data is present, there will be additional processing time while the taxonomy data is inserted into the database.
A `GinIndex` is also created for indexing the taxonomic data (e.g. http://logan.tw/posts/2017/12/30/full-text-search-with-django-and-postgresql/).

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
 git clone https://github.com/idbac/maldidb
 cd ./mdb
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
 cd ./mdb
 pip install -r requirements.txt
 # Run server
 python manage.py makemigrations
 python manage.py migrate
```

In `mdb/mdb/settings.py`, set `Debug = False`.

Execute `python manage.py runserver` to run the project.
The site should now be available in a browser at `http://localhost:8000/`.

A graph diagram of the application's models may be generated
using ```./manage.py graph_models -a -g -o models.png```.

