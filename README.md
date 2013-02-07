###django-deploy

Fabric script that deploys django applications (manages gunicorn) on linux machines with timestamp directories for releases and shared directories for virtualenvs, logs, gunicorn pids, and settings.  

Inspired by ruby's capistrano.

#### Usage

``` fab setup ``` and ``` fab deploy ``` and more.

1. Fill template deploy_settings.py.template and remove .template extension
2. settings_files in deploy_settings.py contains an array of sharable
settings.  These settings get copied over to shared/settings.  They 
could be imported in your django settings file and symlinked in the 
main project directory.
or simply copied over
