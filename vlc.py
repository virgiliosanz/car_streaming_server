""" Module to control a VLC using the rc interfaze.
    see: https://wiki.videolan.org/documentation:modules/rc/
"""
import telnetlib as telnet
import subprocess
import time

HOST = 'localhost'
PORT = 8888
IP_MULTICAST = '239.255.1.2'

_PROMPT = '> '.encode()
_telnet = telnet.Telnet()

def connect():
    """connect to vlc sesion using rc interfaz on HOST & PORT"""
    _telnet.open(HOST, PORT)
    _telnet.set_debuglevel(1)
    _telnet.read_until(_PROMPT)


def service_restart():
    os.system('service vlc start')
    os.system('service vlc stop')


def pause():
    """ Pause streaming """
    _x('pause')


def play():
    """ Play current video file """
    _x('play')


def stop():
    """ Stopstreaming """
    _x('stop')


def add(path):
    """ add and play [path] file """
    clear()
    _x('add %s' % (path,))
    play()


def clear():
    """ Clear playlist - stop streaming"""
    _x('clear')


def shutdown():
    """ Shutdown vlc """
    _x('shutdown')
    _SOCK.close()


def seek(secs):
    """ Go to [secs] position in video stream"""
    _x('seek %d' % secs)


def get_time():
    """ Get current play time """
    return _int(_x('get_time'))


def get_length():
    """ get stream length (secs) """
    return _int(_x('get_length'))


def atracks():
    """ Return list of audio tracks in stream. VLC Format:
    +----[ audio-es ]
    | -1 - Disable
    | 1 - Track 1 - [Spanish]
    | 2 - Track 2 - [English] *
    +----[ end of audio-es ]

    returns

    {'id':1, 'name':'Track 1 - [Spanish]', 'active':False},
    {'id':2, 'name':'Track 2 - [English]', 'active':True}

    """
    ret = _x('atrack')

    tracks = []
    lines = ret.split('\n')

    for line in lines[2:-1]:
        start = line.find('- ') + 2
        asterisk = line.find('*')
        if asterisk == -1:
            track = line[start:]
            active = False
        else:
            track = line[start:asterisk]
            active = True

        tracks.append({
            'id': _int(line[1:3]),
            'name': track,
            'active': active
        })

    return tracks


def atrack(track):
    """ Change audio track to track [track] """
    _x('atrack -1')
    time.sleep(1)
    _x('atrack %d' % int(track))


def is_playing():
    """ Return whether stream is being played """
    return _int(_x('is_playing'))


def filename():
    """ Return current playing filenam + path """
    ret = _x('status')
    start = ret.find('file://')
    if (start == -1):
        return ''
    end = ret[start + 7:].find(' )')
    return ret[start + 7:start + 7 + end]


def _x(cmd):
    """Prepare a command and send it to VLC"""
    if not cmd.endswith('\n'):
        cmd = cmd + '\n'
    cmd = cmd.encode()
    _telnet.write(cmd)

    ret = _telnet.read_until(_PROMPT)
    ret = ret.decode('utf-8')[:-4]

    return ret

def _int(s):
    ret = ''.join(filter(lambda x: x.isdigit(), s))
    if ret == '':
        return 0
    else:
        return int(ret)

