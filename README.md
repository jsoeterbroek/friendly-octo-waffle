# friendly-octo-waffle
friendly-octo-waffle



## Installation 
Install all python requirements (preferably in a virtenv):
```
pip3 install -r requirements-diagnosis-keys.txt
pip3 install -r requirements.txt
```

Create database tables: 
```
python3 manage.py makemigrations
python3 manage.py migrate
```

## Vagrant
Install in vagrant:
```
vagrant up --provision
```

## Usage

Run local webserver (optional):
```
python3 manage.py runserver
```

Fetch the (new) keysets:
```
python3 manage.py runscript fetch
```

Generate stats and figures:
```
python3 manage.py runscript stats
```

Generate a frozen static site in flat HTML (optional):
```
python3 manage.py generate_static_site
```

## Live site:

https://jsoeterbroek.github.io/
