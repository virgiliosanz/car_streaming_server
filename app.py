""" HTTP Interfaz for streaming using vlc """
import os
import time
import logging
from flask import Flask, redirect, url_for, render_template, request
import vlc

app = Flask(__name__)
ROOT_DIR = '/Users/vsanz/Desktop/Pelis/videos'

def _connect_vlc():
    try:
        vlc.connect()
    except:
        logging.warning('VLC está caido - reconect!')
        vlc.service_restart();
        vlc.connect()

def _referrer():
    if request.referrer:
        return request.referrer
    else:
        return url_for('index')

def _folder_info(path):

    if not path:
        path = ''

    folder = {}
    ppath = ''
    folder['current'] = []
    for p in path.split('/'):
        ppath = os.path.join(ppath, p)
        folder['current'].append({'name': p, 'path': ppath})

    folder['dirs'] = []
    folder['videos'] = []
    full_path = os.path.join(ROOT_DIR, path)

    for p in os.listdir(full_path):
        if os.path.isfile(os.path.join(full_path, p)):
            donde = 'videos'
        else:
            donde = 'dirs'

        folder[donde].append({
            'name': p.replace("_", " "),
            'path': os.path.join(path, p)
        })

    return folder

def _video_info():
    """ Get info for current video streaming sesion """
    video = {}
    try:
        video['multicast_ip'] = vlc.IP_MULTICAST
        video['time_current'] = int(vlc.get_time() / 60)
        video['time_total'] = int(vlc.get_length() / 60)
        if (video['time_total'] == 0):
            video['time_percent'] = 0
        else:
            video['time_percent'] = int((video['time_current'] / video['time_total']) * 100)

        video['atracks'] = vlc.atracks()
        video['name'] = os.path.splitext(os.path.basename(vlc.filename()))[0].replace('_', ' ')
        video['active'] = vlc.is_playing()
    except:
        logging.warning("Error getting video data")

    return video


@app.route('/')
def index():
    video = _video_info()
    folder = _folder_info(request.args.get('path'))

    return render_template("index.html", video=video, folder=folder)


@app.route('/video')
def video():
    fpath = os.path.join(ROOT_DIR, request.args.get('path'))
    try:
        vlc.add(fpath)
    except:
        _vlc_connect()

    return redirect(_referrer())

@app.route('/play')
def play():
    vlc.play()
    return redirect(_referrer())

@app.route('/pause')
def pause():
    vlc.pause()
    return redirect(_referrer())

@app.route('/stop')
def stop():
    vlc.stop()
    return redirect(_referrer())

@app.route('/seek/<minutes>')
def seek(minutes):
    vlc.seek(int(minutes)* 60)
    return redirect(_referrer())

@app.route('/reload')
def reload():
    return redirect(_referrer())

@app.route('/restart_vlc')
def restart_vlc():
    os.system('service vlc restart')
    os.system('service vlc start')
    vlc.connect()
    return redirect(_referrer())


@app.route('/reboot')
def reboot():
    os.system('reboot')
    return "Restarting Raspberry Pi"


@app.route('/shutdown')
def shutdown():
    os.system('halt')
    return "Apagando Raspberry Pi"

@app.route('/atrack/<track>')
def atrack(track):
    vlc.atrack(track)
    return redirect(_referrer())

if __name__ == '__main__':
    _connect_vlc()
    app.run(debug=True, host='0.0.0.0')
    #app.run(host='0.0.0.0')
    #app.run(host='0.0.0.0', port=80)
