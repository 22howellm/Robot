from flask import Flask, render_template, session, request, redirect, flash, url_for, jsonify, Response, logging
from interfaces import databaseinterface
try:
    from interfaces import camerainterface, soundinterface
    import robot #robot is class that extends the brickpi class
except:
    pass
import global_vars as GLOBALS #load global variables
import logging, time 
from datetime import *

def session_init_time():
    session['time_init'] == time.time()
    return

def session_clear(duration):
    session_cleared = False
    if float(time.time()) - float(session['time_init']) > duration:
        session.clear()
        session_cleared = True
    return session_cleared
#Creates the Flask Server Object
app = Flask(__name__); app.debug = True
SECRET_KEY = 'my random key can be anything' #this is used for encrypting sessions
app.config.from_object(__name__) #Set app configuration using above SETTINGS
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
GLOBALS.DATABASE = databaseinterface.DatabaseInterface('databases/RobotDatabase.db', app.logger)

#Log messages
def log(message):
    app.logger.info(message)
    return

#create a login page
@app.route('/', methods=['GET','POST'])
def login():
    if not 'loggingattempt' in session:
        session['loggingattempt'] = 0
    if 'userid' in session:
        return redirect('/dashboard')
    message = ""
    if request.method == "POST":
        email = request.form.get("email")
        userdetails = GLOBALS.DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
        log(userdetails)
        if userdetails:
            user = userdetails[0] #get first row in results
            if (user['password'] == request.form.get("password") and session['loggingattempt'] < 100):
                session['password'] = user['password']
                session['userid'] = user['userid']
                session['permission'] = user['permission']
                session['name'] = user['name']
                return redirect('/dashboard')
            else:
                message = "Login Unsuccessful"
                session['loggingattempt'] += 1
        else:
            message = "Login Unsuccessful"
    return render_template('login.html', data = message)    
# Load the ROBOT
@app.route('/robotload', methods=['GET','POST'])
def robotload():
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.stop_all()
        GLOBALS.ROBOT.CurrentRoutine = "stop"
    sensordict = None
    if not GLOBALS.CAMERA:
        log("LOADING CAMERA")
        try:
            GLOBALS.CAMERA = camerainterface.CameraInterface()
        except Exception as error:
            log("FLASK APP: CAMERA NOT WORKING")
            GLOBALS.CAMERA = None
        if GLOBALS.CAMERA:
            GLOBALS.CAMERA.start()
    if not GLOBALS.ROBOT:
        try: 
            log("FLASK APP: LOADING THE ROBOT")
            GLOBALS.ROBOT = robot.Robot(20, app.logger)
            GLOBALS.ROBOT.configure_sensors() #defaults have been provided but you can 
            GLOBALS.ROBOT.reconfig_IMU()
        except:
            print('Error found with loading robot (approx line 60)')
    if not GLOBALS.SOUND:
        log("FLASK APP: LOADING THE SOUND")
        GLOBALS.SOUND = soundinterface.SoundInterface()
        #GLOBALS.SOUND.say("I am ready")
    sensordict = GLOBALS.ROBOT.get_all_sensors()
    return jsonify(sensordict)
# ---------------------------------------------------------------------------------------
#My functions
def passwordsecure():
    if not 'userid' in session:
        return redirect('/')
    userdetails = GLOBALS.DATABASE.ViewQuery("SELECT * FROM users WHERE userid = ?", (session['userid'],))
    if not 'password' in session:
        session.clear()
        return redirect('/')
    password = session['password']
    password2 = userdetails[0]['password']
    if password2 != password:
        session.clear()
        return redirect('/')

# Dashboard
@app.route('/dashboard', methods=['GET','POST'])
def robotdashboard():
    passwordsecure()
    enabled = int(GLOBALS.ROBOT != None)
    return render_template('dashboard.html', robot_enabled = enabled )

#Used for reconfiguring IMU
@app.route('/reconfig_IMU', methods=['GET','POST'])
def reconfig_IMU():
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.reconfig_IMU()
        sensorconfig = GLOBALS.ROBOT.get_all_sensors()
        return jsonify(sensorconfig)
    return jsonify({'message':'ROBOT not loaded'})

#calibrates the compass but takes about 10 seconds, rotate in a small 360 degrees rotation
@app.route('/compass', methods=['GET','POST'])
def compass():
    data = {}
    if GLOBALS.ROBOT:
        data['message'] = GLOBALS.ROBOT.calibrate_imu(10)
    return jsonify(data)

@app.route('/sensors', methods=['GET','POST'])
def sensors():
    data = {}
    if GLOBALS.ROBOT:
        data = GLOBALS.ROBOT.get_all_sensors()
    return jsonify(data)

# YOUR FLASK CODE------------------------------------------------------------------------

@app.route('/lob', methods=['GET','POST'])
def lob():
    data = {}
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.spin_medium_motor(555)
        GLOBALS.ROBOT.spin_medium_motor(555)
    return jsonify(data)

@app.route('/shoot', methods=['GET','POST'])
def shoot():
    data = {}
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.spin_medium_motor(-555)
        GLOBALS.ROBOT.spin_medium_motor(-555)
    return jsonify(data)

@app.route('/turn90', methods=['GET','POST'])
def turn90():
    data = {}
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.rotate_power_degrees_IMU(10,90,-0.6)
    return jsonify(data)

@app.route('/moveforward', methods=['GET','POST'])
def moveforward():
    data = {}
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.move_power(50,1.1)
    return jsonify(data)

@app.route('/movebackwards', methods=['GET','POST'])
def movebackwards():
    data = {}
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.move_power(-50,1.1)
    return jsonify(data)

@app.route('/moveforwardslow', methods=['GET','POST'])
def moveforwardslow():
    data = {}
    if GLOBALS.ROBOT:
        data['elapsedtime'] = GLOBALS.ROBOT.move_power(20,1.9)
        data['heading'] = GLOBALS.ROBOT.get_compass_IMU()
    return jsonify(data)

@app.route('/movebackwardsslow', methods=['GET','POST'])
def movebackwardsslow():
    data = {}
    if GLOBALS.ROBOT:
        data['elapsedtime'] = GLOBALS.ROBOT.move_power(-20,-1.9)
        data['heading'] = GLOBALS.ROBOT.get_compass_IMU()
    return jsonify(data)

@app.route('/turnleft', methods=['GET','POST'])
def turnleft():
    data = {}
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.rotate_power(-25)
    return jsonify(data)

@app.route('/turnright', methods=['GET','POST'])
def turnright():
    data = {}
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.rotate_power(25)
    return jsonify(data)

@app.route('/turnleftslow', methods=['GET','POST'])
def turnleftslow():
    data = {}
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.rotate_power(-10)
    return jsonify(data)

@app.route('/turnrightslow', methods=['GET','POST'])
def turnrightslow():
    data = {}
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.rotate_power(10)
    return jsonify(data)

@app.route('/stop', methods=['GET','POST'])
def stop():
    data = {}
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.stop_all()
        GLOBALS.ROBOT.CurrentRoutine = "stop"
    return jsonify(data)

#sensor view
@app.route('/sensorview', methods=['GET','POST'])
def sensorview():
    passwordsecure()
    data = None
    if GLOBALS.ROBOT:
        data = GLOBALS.ROBOT.get_all_sensors()
    else:
        redirect('/dashboard')
    return render_template("sensorview.html", data = data)

#mission view page allows the medic manager to create a mission and save data around that mission
@app.route('/mission', methods=['GET','POST'])
def mission():
    data = None
    passwordsecure()
    if request.method =="POST":
        userid = session['userid']
        notes = request.form.get('notes')
        location = request.form.get('location')
        starttime = datetime.now()
        log("FLASK_APP: mission: " + str(location) + " " + str(notes) + " " + str(starttime))
        GLOBALS.DATABASE.ModifyQuery("INSERT INTO missions (location, notes, userid) VALUES (?,?,?)",(location,notes,userid))
        #put start in
        #Get the current mission id and save it into session ['missionid']
        # Get mission history and send to the page
    return render_template("mission.html")

#Automatic search code ------------------------------------------------------------------------------------------------------------------------

#automatic mode when turned on will automatically search the area
@app.route('/automatic_mode', methods=['GET','POST'])
def automatic_mode():
    data = []
    if request.method == 'POST':
        if GLOBALS.ROBOT:
            while True:
                GLOBALS.ROBOT.automatic_search()
            return jsonify(data)
        else:
            print("Robot not here")
    else:
        redirect('/dashboard')
    return jsonify(data)
























# -----------------------------------------------------------------------------------
# CAMERA CODE-----------------------------------------------------------------------
# Continually gets the frame from the pi camera
def videostream():
    """Video streaming generator function."""
    while True:
        if GLOBALS.CAMERA:
            frame = GLOBALS.CAMERA.get_frame()
            if frame:
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 
            else:
                return '', 204
        else:
            return '', 204 

#embeds the videofeed by returning a continual stream as above
@app.route('/videofeed')
def videofeed():
    if GLOBALS.CAMERA:
        log("FLASK APP: READING CAMERA")
        """Video streaming route. Put this in the src attribute of an img tag."""
        return Response(videostream(), mimetype='multipart/x-mixed-replace; boundary=frame') 
    else:
        return '', 204
        
#----------------------------------------------------------------------------
#Shutdown the robot, camera and database
def shutdowneverything():
    log("FLASK APP: SHUTDOWN EVERYTHING")
    if GLOBALS.CAMERA:
        GLOBALS.CAMERA.stop()
    if GLOBALS.ROBOT:
        GLOBALS.ROBOT.safe_exit()
    GLOBALS.CAMERA = None; GLOBALS.ROBOT = None; GLOBALS.SOUND = None
    return

#Ajax handler for shutdown button
@app.route('/robotshutdown', methods=['GET','POST'])
def robotshutdown():
    shutdowneverything()
    return jsonify({'message':'robot shutdown'})

#Shut down the web server if necessary
@app.route('/shutdown', methods=['GET','POST'])
def shutdown():
    shutdowneverything()
    func = request.environ.get('werkzeug.server.shutdown')
    func()
    return jsonify({'message':'Shutting Down'})

@app.route('/logout')
def logout():
    shutdowneverything()
    session.clear()
    return redirect('/')

#---------------------------------------------------------------------------
#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True) #runs a local server on port 5000