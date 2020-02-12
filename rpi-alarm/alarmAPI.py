# Raspberry PI GPIO Alarm interface
# Brandon Joffe
# 2016
#
# Copyright 2016, Brandon Joffe, All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This Flask implementation is used to demonstrate the potential of the
# system to be connected to an already existing alarm panel. In order
# to acheive this, slight changes to the code will be required, as well as
# the use of a few electrical components i.e transistor to create a open
# and closed circuit.
import threading
import time
import json
from flask import Flask, render_template, request, Response,jsonify
from pydub import AudioSegment
from pydub.playback import play

app = Flask(__name__)

triggered = False

thread = threading.Thread()
thread.daemon = False

active = 1
disabled = 0

# Dictionary used to store the pin number, name, and pin state:
pins = {
   26 : {'name' : 'alarm', 'state' : disabled},
   13 : {'name' : 'siren', 'state' : disabled},
   19 : {'name' : 'active', 'state' : active}
   }

alarm_state = {'state': 0, 'triggered': triggered}
# Set each pin as an output and set it low:
for pin in pins:
    print(pins[pin])

@app.route("/test", methods = ['GET'])
def test():
    mensagem = {"mensagem":"ativo"}
    return jsonify(mensagem)

@app.route("/", methods = ['GET','POST'])
def main():
    """Returns alarms current state"""
    print("main - Returns alarms current state")
    global alarm_state
    global triggered
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin':
            alarm_state['state'] = active
            alarm_state['triggered'] = triggered
            return jsonify(alarm_state)
        else:
            return 'Access Denied'

@app.route("/change_state", methods = ['GET','POST'])
def change_state():
    """Changes alarm's current state"""
    print("change_state - Changes alarm's current state")
    global triggered
    global alarm_state
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin':
            triggered = not triggered

            if (triggered):
                alarm_state['state'] = active
            else:
                alarm_state['state'] = disabled

            alarm_state['triggered'] = triggered
            return jsonify(alarm_state)
        else:
            return 'Access Denied'

@app.route("/trigger", methods = ['GET','POST'])
def trigger():
    """Triggers the alarm"""
    print("trigger - Triggers the alarm")
    global triggered
    if request.method == 'POST':
        password = request.form.get('password')
        print("A senha é %s"%(password))
        if password == 'admin':
            # play sound.
            playSound()
            triggered = True
            global thread

            if not thread.isAlive():
                print("Ativando a thread...")
                thread = threading.Thread(name='trigger_thread', target = alarmtrigger,args=())
                thread.start()
            alarm_state['state'] = active
            alarm_state['triggered'] = triggered

            return jsonify(alarm_state)
        else:
            return 'Access Denied'

def alarmtrigger():
    global triggered
    while True:
        if triggered == True:
            #GPIO.output(26, not GPIO.input(26))
            print("Ativar som do alarme")
            playSound()
            time.sleep(4)
        else:
            #GPIO.output(26, GPIO.LOW)
            print("Alarme desativado!")
            time.sleep(1)

def playSound():
    song = AudioSegment.from_wav("siren.wav")
    play(song)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=3000, debug=False)
