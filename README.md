# soMedia
<a href="http://www.djangoproject.com/"><img src="https://www.djangoproject.com/m/img/badges/djangomade124x25.gif" border="0" alt="Made with Django." title="Made with Django." /></a>
![ScreenShot](/libs/static/images/page-shot.png)

A simple social Media Application for sharing images amongst users. This application was developed for teaching django to new learners and to expose them to the numerous functionalities of django.

## Features
- Registration
- Login
- Profile Editing
- Custom User Model
- Working with ModelForms and normal Forms
- Simple TemplateTags
- Managing Admin
- Simple Signals
- Add Posts
- Add Comments to Posts
- Follow other Users to view their Posts
- Unfollowing Followed Users
- Simple Bootstrap
- View Other Users Profile

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

- 3 drawings, one for each pipeline - slides?
 each box represents a process and/or? data, and the edges?
 and a screenshot of the pipeline in action, e.g., search results page / search page
  add the screenshot to the drawing at that box.
