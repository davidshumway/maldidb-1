## Installation
### Create a Virtualenv
- Windows
```bash
  pip install virtualenv
  virtualenv .venv
  .venv/Scripts/activate.bat
```

- Linux
```bash
  sudo pip3 install virtualenv
  virtualenv .venv -p python3
  source .venv/bin/activate
```

### Install Requirements
Requires R and IDBacApp (R) to be preinstalled.
```bash
  pip install -r requirements.txt
```

### Run migrations and start server
```bash
  python manage.py makemigrations
  python manage.py migrate
  python manage.py runserver
```
The application should be available through your browser at
http://localhost:8000/.

A graph diagram of the models may then be generated with ```./manage.py graph_models -a -g -o models.png```.

### Overview
- Import from SQLite
- Search and browse data
- User and group management 
- Website layout
- Pipelines:
- - Bin peaks and cosine scoring (i.e., search)
- - Replicates to collapsed spectra (in progress)
- - Preprocessing (in progress)
- - Upload spectra files  (in progress)
- ACS Django publications (review) https://pubs-acs-org.proxy.cc.uic.edu/action/doSearch?AllField=%22django%22

