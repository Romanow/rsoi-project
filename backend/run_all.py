import subprocess
import sys
import os
import time

os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "1"


def run_service(dir, script_name, name):
    print(f'--- launching <{name}> service')
    p = subprocess.Popen(['python', script_name, '-throw_errors'], cwd=dir,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, )
                         #stdout=subprocess.STDOUT)
    return p

def run_search():
    return run_service(r'./search_service', 'search_service.py', 'search')

def run_auth():
    return run_service(r'auth_service', 'auth_service.py', 'auth')

def run_file():
    return run_service(r'./file_service', 'file_service.py', 'file')

def run_scout():
    return run_service(r'./scout_service', 'scout_service.py', 'scout')


if __name__ == '__main__':
    run_map = {'search': run_search,
               'auth': run_auth,
               'file': run_file,
               'scout': run_scout}

    default_service_names = ['search', 'auth', 'file', 'scout']
    service_names = ['search', 'auth', 'file', 'scout']

    services = [run_map[name]() for name in service_names]

    stop = input('Press [ENTER] to stop: ')

    for service in services:
        service.terminate()