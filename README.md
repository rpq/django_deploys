### django_deploys

Fabric script that deploys django applications (manages gunicorn) on linux machines with timestamp directories for releases and shared directories for virtualenvs, logs, gunicorn pids, and settings.  

Inspired by ruby's capistrano.

#### Usage

``` fab setup ``` and ``` fab deploy ``` and more.

1. pip install django_deploys
1. Create a directory for your deploy_settings.py
1. Fill template deploy_settings.py.template
1. settings_files in deploy_settings.py is an array of file paths 
    that have settings related to the deploy.  The file paths set 
    there get copied over to shared/settings on the deploy target 
    directory.  After they are copied over, you may want to set 
    symlinks between the individual files in your checked out 
    project directory and the actual files in the shared/settings 
    directory.
1. run django_deploys.py -l from the directory containing the 
   deploy_settings.py to see a list of available options.
