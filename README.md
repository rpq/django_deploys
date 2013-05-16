### django_deploys

Fabric script that deploys git repository based django applications on Linux machines with timestamp directories for releases and shared directories for virtualenvs, logs, gunicorn pids, and settings.  

Inspired by ruby's capistrano.

#### Usage

``` fab setup ``` and ``` fab deploy ``` and more.

1. Install: pip install django_deploys
1. Configure: Create a directory for your deploy_settings.py
1. Configure: Fill template deploy_settings.py.template and rename as deploy_settings.py in your recently created directory
1. Configure: Copy your django settings.py to be used for your deployment.
1. Configure: Other configuration options include symlinking directories.
1. Run django_deploys.py setup for the initial run
1. Run django_deploys.py deploy or django_deploys.py update for subsequent runs.  deploy will create a timestamped directory in releases and move the current pointer.  update will only update the existing current pointer timestamped directory with code and migrations.
1. run django_deploys.py -l from the directory containing the 
deploy_settings.py to see a full list of available options.
