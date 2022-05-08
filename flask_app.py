from select import select
from tkinter.tix import Select
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

#Checks if there is a mission active or not
def Check_Mission_status():
        most_recent = GLOBALS.DATABASE.ViewQuery("SELECT Mission_Concluded FROM MissionTBL ORDER BY MissionID DESC LIMIT 1")
        if most_recent == False: #if there is no mission recorded in the database
            return(False)
        else:
            most_recent = most_recent[0]
        if most_recent['Mission_Concluded'] == 'True':
            return(False)
        else:
            return(True)

def Update_Current_MissionID(): #updates the current missionId in the session
    session['Mission_Active'] = Check_Mission_status()
    if session['Mission_Active'] == True:
        missionid = GLOBALS.DATABASE.ViewQuery("SELECT MissionID FROM MissionTBL where Mission_Concluded = 'False'")
        session['Current_MissionID'] = missionid[0]['MissionID']
    else:
        session['Current_MissionID'] = None

#Log messages
def log(message):
    app.logger.info(message)
    return

#create a login page
@app.route('/', methods=['GET','POST'])
def login():
    session['Mission_Active'] = Check_Mission_status()
    Update_Current_MissionID()
    if 'userid' in session:
        return redirect('/dashboard')
    message = ""
    if request.method == "POST":
        email = request.form.get("email")
        userdetails = GLOBALS.DATABASE.ViewQuery("SELECT * FROM UserTBL WHERE Email = ?", (email,))
        log(userdetails)
        if userdetails:
            user = userdetails[0] #get first row in results
            if (user['Password'] == request.form.get("password")):
                session['password'] = user['Password']
                session['userid'] = user['Userid']
                session['permission'] = user['Permission']
                session['name'] = user['Name']
                return redirect('/dashboard')
            else:
                message = "Login Unsuccessful"
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
"""def passwordsecure():
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
"""

# Dashboard
@app.route('/dashboard', methods=['GET','POST'])
def robotdashboard():
    #passwordsecure()
    Update_Current_MissionID()
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
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        GLOBALS.ROBOT.spin_medium_motor(555)
        GLOBALS.ROBOT.spin_medium_motor(555)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Delivered package'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))
    return jsonify(data)

@app.route('/shoot', methods=['GET','POST'])
def shoot():
    data = {}
    if GLOBALS.ROBOT:
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        GLOBALS.ROBOT.spin_medium_motor(-555)
        GLOBALS.ROBOT.spin_medium_motor(-555)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Delivered package directly'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))
    return jsonify(data)

@app.route('/turn90', methods=['GET','POST'])
def turn90():
    data = {}
    if GLOBALS.ROBOT:
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        GLOBALS.ROBOT.rotate_power_degrees_IMU(10,90,-0.6)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Turn 90'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))
    return jsonify(data)

@app.route('/moveforward', methods=['GET','POST'])
def moveforward():
    data = {}
    if GLOBALS.ROBOT:
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        GLOBALS.ROBOT.move_power(50,1.1)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Forward Fast'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))
    return jsonify(data)

@app.route('/movebackwards', methods=['GET','POST'])
def movebackwards():
    data = {}
    if GLOBALS.ROBOT:
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        GLOBALS.ROBOT.move_power(-50,1.1)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Backwards Fast'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))
    return jsonify(data)

@app.route('/moveforwardslow', methods=['GET','POST'])
def moveforwardslow():
    data = {}
    if GLOBALS.ROBOT:
        data['heading'] = GLOBALS.ROBOT.get_compass_IMU()
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        data['elapsedtime'] = GLOBALS.ROBOT.move_power(20,1.9)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Forward Slow'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))
    return jsonify(data)

@app.route('/movebackwardsslow', methods=['GET','POST'])
def movebackwardsslow():
    data = {}
    if GLOBALS.ROBOT:
        data['heading'] = GLOBALS.ROBOT.get_compass_IMU()
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        data['elapsedtime'] = GLOBALS.ROBOT.move_power(-20,-1.9)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Backwards slow'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))
    return jsonify(data)

@app.route('/turnleft', methods=['GET','POST'])
def turnleft():
    data = {}
    if GLOBALS.ROBOT:
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        GLOBALS.ROBOT.rotate_power(-25)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Fast Left'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))
    return jsonify(data)

@app.route('/turnright', methods=['GET','POST'])
def turnright():
    data = {}
    if GLOBALS.ROBOT:
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        GLOBALS.ROBOT.rotate_power(25)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Fast Right'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))
    return jsonify(data)

@app.route('/turnleftslow', methods=['GET','POST'])
def turnleftslow():
    data = {}
    if GLOBALS.ROBOT:
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        GLOBALS.ROBOT.rotate_power(-10)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Slow Left'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))

    return jsonify(data)

@app.route('/turnrightslow', methods=['GET','POST'])
def turnrightslow():
    data = {}
    if GLOBALS.ROBOT:
        starttime = datetime.now()
        endtime = None
        start_heading = GLOBALS.ROBOT.get_compass_IMU()
        GLOBALS.ROBOT.rotate_power(10)
        endtime = datetime.now()
        final_heading = start_heading = GLOBALS.ROBOT.get_compass_IMU()
        Mission_status = Check_Mission_status()
        if Mission_status == True:
            Update_Current_MissionID()
            missionid = session['Current_MissionID']
            action = 'Slow Right'
            GLOBALS.DATABASE.ModifyQuery('INSERT INTO ActionTBL (Missionid, Action_Type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading) VALUES (?,?,?,?,?,?)',(missionid,action,starttime,endtime,start_heading,final_heading))
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
    #passwordsecure()
    data = None
    if GLOBALS.ROBOT:
        data = GLOBALS.ROBOT.get_all_sensors()
    else:
        redirect('/dashboard')
    return render_template("sensorview.html", data = data)

#mission view page allows the medic manager to create a mission and save data around that mission
@app.route('/mission', methods=['GET','POST'])
def mission():
    data = {}
    Mission_Active = False #until proven otherwise
    Mission_Active = Check_Mission_status()#code defined near the start which checks if there is an active mission
    userid = int(session['userid'])
    missionid = None
    name = GLOBALS.DATABASE.ViewQuery("SELECT Name FROM UserTBL WHERE Userid = ?", (userid,))
    name = name[0]['Name']
    data['name'] = name
    data['Mission_Active'] = Mission_Active
    if request.method =="POST":
        Mission_Active = Check_Mission_status()
        data['Mission_Active'] = Mission_Active
        notes = request.form.get('notes')
        if Mission_Active == True:
            importance = request.form.get('importance')
        starttime = datetime.now()
        if notes == 'start': 
            location = request.form.get('location')
            if Mission_Active == False:
                GLOBALS.DATABASE.ModifyQuery("INSERT INTO MissionTBL (location, userid, Start_Time, Mission_Concluded) VALUES (?,?,?,?)",(location,userid,starttime,'False'))
                Mission_Active = Check_Mission_status()
                data['Mission_Active'] = Mission_Active
                return render_template('mission.html', message = 'mission started',data=data)
            else:
                return render_template('mission.html', message = 'mission already underway',data=data)
        elif notes == 'end':
            if Mission_Active == False:
                return render_template('mission.html', message = 'No current mission',data=data)
            else:
                missionid = GLOBALS.DATABASE.ViewQuery("SELECT MissionID FROM MissionTBL where Mission_Concluded = 'False'")
                missionid = missionid[0]['MissionID']
                endtime = datetime.now()
                GLOBALS.DATABASE.ModifyQuery('UPDATE MissionTBL SET Mission_Concluded = ?, End_Time = ? WHERE MissionID = ?', ('True',endtime,missionid))
                Mission_Active = Check_Mission_status()
                data['Mission_Active'] = Mission_Active
                return render_template('mission.html', message = 'Mission completed', data=data)
        else:
            if Mission_Active == False:
                return render_template('mission.html', message = 'No current mission',data=data)
            else:
                missionid = GLOBALS.DATABASE.ViewQuery("SELECT MissionID FROM MissionTBL where Mission_Concluded = 'False'")
                missionid = missionid[0]['MissionID']
                time = datetime.now()
                GLOBALS.DATABASE.ModifyQuery('INSERT INTO MedicallogTBL (MissionID, Time_Published, Note, Importance) VALUES (?,?,?,?)', (missionid,time,notes,importance))
                return render_template("mission.html", message = 'Notes Submitted', data=data)
    return render_template("mission.html", data=data)

@app.route('/medical_notes', methods=['GET','POST'])
def medical_notes():
    data = {}
    message = ''
    results = GLOBALS.DATABASE.ViewQuery('SELECT MissionTBL.MissionID, UserTBL.name, MissionTBL.Start_time, MissionTBL.End_time,MissionTBL.Location,MissionTBL.Mission_Concluded FROM MissionTBL INNER JOIN UserTBL ON MissionTBL.Userid = UserTBL.Userid')
    if request.method == 'POST':
        mission = request.form.getlist("selectedmission")
        if len(mission) > 1:
            return render_template('medical_notes.html',message = 'You can only select on mission',data=results)
        elif len(mission) == 1:
            selected_mission = mission[0]
            session['selected_mission'] = selected_mission
            return redirect('/medical_notes_extended')
        else:
            return render_template('medical_notes.html',message = 'Please select a mission',data=results)
    return render_template('medical_notes.html',message = '',data=results)

@app.route('/medical_notes_extended', methods=['GET','POST'])
def medical_notes_extended():
    data = {}
    MissionID = int(session['selected_mission'])
    results = GLOBALS.DATABASE.ViewQuery('SELECT MedicallogID, Time_Published, Note, Importance FROM MedicallogTBL WHERE MissionID = ?', (MissionID,))
    if request.method == 'POST':
        return redirect('/medical_notes')
    return render_template('medical_notes_extended.html',data=results)

@app.route('/action_log', methods=['GET','POST'])
def action_log():
    data = {}
    message = ''
    results = GLOBALS.DATABASE.ViewQuery('SELECT MissionTBL.MissionID, UserTBL.name, MissionTBL.Start_time, MissionTBL.End_time,MissionTBL.Location,MissionTBL.Mission_Concluded FROM MissionTBL INNER JOIN UserTBL ON MissionTBL.Userid = UserTBL.Userid')
    if request.method == 'POST':
        mission = request.form.getlist("selectedmission")
        if len(mission) > 1:
            return render_template('action_log.html',message = 'You can only select on mission',data=results)
        elif len(mission) == 1:
            selected_mission = mission[0]
            session['selected_mission'] = selected_mission
            return redirect('/action_log_extended')
        else:
            return render_template('action_log.html',message = 'Please select a mission',data=results)
    return render_template('action_log.html',message = '',data=results)


@app.route('/action_log_extended', methods=['GET','POST'])
def action_log_extended():
    data = {}
    MissionID = int(session['selected_mission'])
    results = GLOBALS.DATABASE.ViewQuery('SELECT Actionlogid, Action_type, Action_Start_Time, Action_End_Time, Start_Heading, End_Heading FROM ACTIONTBL WHERE MissionID = ?', (MissionID,))
    if request.method == 'POST':
        return redirect('/action_log')
    return render_template('action_log_extended.html',data=results)

@app.route('/tile_log', methods=['GET','POST'])
def tile_log():
    data = {}
    message = ''
    results = GLOBALS.DATABASE.ViewQuery('SELECT MissionTBL.MissionID, UserTBL.name, MissionTBL.Start_time, MissionTBL.End_time,MissionTBL.Location,MissionTBL.Mission_Concluded FROM MissionTBL INNER JOIN UserTBL ON MissionTBL.Userid = UserTBL.Userid')
    if request.method == 'POST':
        mission = request.form.getlist("selectedmission")
        if len(mission) > 1:
            return render_template('tile_log.html',message = 'You can only select on mission',data=results)
        elif len(mission) == 1:
            selected_mission = mission[0]
            session['selected_mission'] = selected_mission
            return redirect('/tile_log_extended')
        else:
            return render_template('tile_log.html',message = 'Please select a mission',data=results)
    return render_template('tile_log.html',message = '',data=results)

@app.route('/tile_log_extended', methods=['GET','POST'])
def tile_log_extended():
    data = {}
    MissionID = int(session['selected_mission'])
    results = GLOBALS.DATABASE.ViewQuery('SELECT * FROM TileTBL WHERE MissionID = ?', (MissionID,))
    if request.method == 'POST':
        return redirect('/tile_log')
    return render_template('tile_log_extended.html',data=results)
#Automatic search code ------------------------------------------------------------------------------------------------------------------------

#automatic mode when turned on will automatically search the area
@app.route('/automatic_mode', methods=['GET','POST'])
def automatic_mode():
    data = []
    if request.method == 'POST':
        if GLOBALS.ROBOT:
            while True:
                GLOBALS.ROBOT.automatic_search()
                if GLOBALS.ROBOT.CurrentRoutine == "stop":
                    break
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