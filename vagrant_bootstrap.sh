echo "vagrant bootstrap"

# Updating packages
sudo apt-get update
sudo apt-get install -y python3-pip
sudo apt-get install -y git
sudo apt-get install -y libpq-dev

if test ! -d friendly-octo-waffle; then
    git clone https://github.com/jsoeterbroek/friendly-octo-waffle.git
fi

cd friendly-octo-waffle/
git pull
git submodule update --init

cat > app/secret_settings.py << EOF
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_SECRET_KEY = 'changeme'
SECRET_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'keys.sqlite3'),
    }
}
SECRET_USE_TZ = False
EOF

pip3 install -r requirements-diagnosis-keys.txt
pip3 install -r requirements.txt

python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py runscript fetch
python3 manage.py generate_static_site

exit 0
