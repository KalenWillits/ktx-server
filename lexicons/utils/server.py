from datetime import datetime
import pprint

pp = pprint.PrettyPrinter(indent=4)


def on_connect(ws=None, sv=None, db=None):
    '''
    Placeholder that runs after a websocket connection starts and is authenticated.
    '''


def on_disconnect(ws=None, sv=None, db=None):
    '''
    Placeholder that runs after a websocket disconnets.
    '''

def on_start(sv=None, db=None):
    '''
    Placeholder that runs when the server starts.
    '''

def on_shutdown(sv=None, db=None):
    '''
    Placeholder that runs when the server shuts down.
    '''


def on_log(ws=None, sv=None, db=None, status=None, data=None, error=None):
    '''
    Default log function that prints to the console in debug mode.
    '''

    out = f'{str(datetime.now().time())}: [{status}]'

    if data:
        pretty_data = pp.pformat(data)
        if status == 'SIGNAL':
            out += f' <- {pretty_data}'

        elif status == 'BROADCAST':
            out += f' -> {pretty_data}'

        else:
            out += pretty_data
    else:
        data = ''


    if sv.debug:
        print(str(datetime.now()), f'[{status}]', data)
