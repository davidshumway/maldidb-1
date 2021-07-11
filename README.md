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
When Django runs for the first time, the first time that NCBI taxonomy data is present there will be additional processing time while the taxonomy data is inserted into the database.
A `GinIndex` is also created for indexing the taxonomic data (e.g. http://logan.tw/posts/2017/12/30/full-text-search-with-django-and-postgresql/).

Avoid rebuilding on successive starts by calling ```docker-compose up``` or ```docker-compose start``` to start the system.

For production builds, set `Debug = False` in `./mdb/mdb/settings.py`.

Use ```./manage.py graph_models -a -g -o models.png``` to generate graph diagrams of the application's models.

