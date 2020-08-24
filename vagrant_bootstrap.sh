echo "vagrant bootstrap"

# Adding multiverse sources.
cat > /etc/apt/sources.list.d/multiverse.list << EOF
deb http://archive.ubuntu.com/ubuntu trusty multiverse
deb http://archive.ubuntu.com/ubuntu trusty-updates multiverse
deb http://security.ubuntu.com/ubuntu trusty-security multiverse
EOF



# Updating packages
apt-get update
apt-get install -y python3-pip
apt-get install -y git
apt-get install -y libpq-dev

git clone https://github.com/jsoeterbroek/friendly-octo-waffle.git
cd friendly-octo-waffle/


cat > app/secret_settings.py << EOF
import os
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_SECRET_KEY = 'changeme'
SECRET_DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'eks.sqlite3'),
    }
}
SECRET_USE_TZ = False
EOF

pip3 install -r requirements-diagnosis-keys.txt
pip3 install -r requirements.txt

python3 manage.py runscript fetch

exit 0
