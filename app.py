# USAGE

# import the necessary packages
#Used for Face Recognition
import face_recognition
# load the video and processthe video frame
import cv2
#import os.path
# read and write contents to CSV FIle
import os
# to get the time stamp
from datetime import datetime

from flask import Flask,render_template,request,redirect,session,flash,url_for,jsonify
from functools import wraps
from flask_mysqldb import MySQL
from chat import get_response


app=Flask(__name__)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='anam'
app.config['MYSQL_CURSORCLASS']='DictCursor'
mysql=MySQL(app)
app.secret_key='secret123'



@app.route('/') 
@app.route('/login',methods=['POST','GET'])
def login():
    status=True
    if request.method=='POST':
        email=request.form["email"]
        pwd=request.form["password"]
        cur=mysql.connection.cursor()
        cur.execute("select * from users where email=%s and password=%s",(email,pwd))
        data=cur.fetchone()
        if data:
            session['logged_in']=True
            session['username']=data["username"]
            flash('Login Successfully','success')
            return redirect('home')
        else:
            flash('Invalid Login. Try Again','danger')
    return render_template("login.html")

def is_logged_in(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if 'logged_in' in session:
			return f(*args,**kwargs)
		else:
			flash('Unauthorized, Please Login','danger')
			return redirect(url_for('login'))
	return wrap

@app.route('/reg',methods=['POST','GET'])
def reg():
    status=False
    if request.method=='POST':
        name=request.form["username"]
        email=request.form["email"]
        pwd=request.form["password"]
        cur=mysql.connection.cursor()
        cur.execute("insert into users(username,email,password) values(%s,%s,%s)",(name,email,pwd))
        mysql.connection.commit()
        cur.close()
        flash('Registration Successfully. Login Here...','success')
        return redirect(url_for('login'))
    return render_template("register.html",status=status)



@app.route('/home', methods=['GET'])
@is_logged_in
def home():
    return render_template('index.html')

@app.route("/logout")
def logout():
	session.clear()
	flash('You are now logged out','success')
	return redirect(url_for('login'))

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/faq', methods=['GET'])
def faq():
    return render_template('faq.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
   
        # Load images.
        print("[INFO] quantifying faces...")   
        image_1 = face_recognition.load_image_file("dataset/dhoni/Dh (9).jpg")
        image_1_face_encoding = face_recognition.face_encodings(image_1)[0]
            
        image_2 = face_recognition.load_image_file("dataset/modi/modi (10).jpg")
        image_2_face_encoding = face_recognition.face_encodings(image_2)[0]
        
        image_3 = face_recognition.load_image_file("dataset/yuvraj/yuvi (10).jpg")
        image_3_face_encoding = face_recognition.face_encodings(image_3)[0]
                
        image_4 = face_recognition.load_image_file("dataset/sharukh/sha (5).jpg")
        image_4_face_encoding = face_recognition.face_encodings(image_4)[0]
        
        #mypart
        image_5 = face_recognition.load_image_file("dataset/ElonMask/image19.jpeg")
        image_5_face_encoding = face_recognition.face_encodings(image_5)[0]
              
            
        # Create arrays of known face encodings and their names
        known_face_encodings = [
                
                image_1_face_encoding,
                image_2_face_encoding,
                image_3_face_encoding,
                image_4_face_encoding,
                image_5_face_encoding
                
            ]
        known_face_names = [
               
                "MS Dhoni",
                "Norendro Modi",
        	    "Youvraj",
                "Sharukh Khan",
                "Elon Musk"
            ]
            
        # Initializing  variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True
            
        # Get a reference to webcam #0 (the default one)
        
        print("[INFO] starting video stream...")
        video_capture = cv2.VideoCapture(0)
        
        # loop over frames from the video file stream
        while True:
         # grab the frame from the threaded video stream
            ret, frame = video_capture.read()
            
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            
            # Convert the image from BGR color (which OpenCV uses) to
            #RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]
            
            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            face_names = []
            name = ""
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
            
                 # If a match was found in known_face_encodings, just use the first one.
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    #Enter Tracking log
                    logFile = open('log.csv', mode="a")
                    # set the file pointer to end of the file
                    pos = logFile.seek(0, os.SEEK_END)
                    # If this is a empty log file then write the column headings
                    if pos == 0:
                        logFile.write("Year,Month,Day,Time,Name,Attendance")
                    #Set Date and Time
                    ts = datetime.now()
                    newDate = ts.strftime("%m-%d-%y")
                    year = ts.strftime("%Y")
                    month = ts.strftime("%m")
                    day = ts.strftime("%d")
                    
                    time1 = ts.strftime("%H:%M:%S")
                    info = "{},{},{},{},{},{}\n".format(year, month,day, time1,name,"Present")
                    logFile.write(info)
                    logFile.close()
                


              
            face_names.append(name)
            
            
            #process_this_frame = not process_this_frame
            
           
            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                   # Scale back up face locations since the frame we detected in was scaled to 1/4 size
                   top *= 4
                   right *= 4
                   bottom *= 4
                   left *= 4
                   cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                   cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                   # Draw a label with a name below the face
                   font = cv2.FONT_HERSHEY_DUPLEX
                   # Draw a box around the face
                   cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            
            
            # Display the resulting image
            cv2.imshow('Video', frame)
          
        
         
            # Hit 'q' on the keyboard to quit!
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
           

            
        # Release handle to the webcam
        video_capture.release()
        cv2.destroyAllWindows()
        return render_template("login.html")

@app.post("/chatbot")
def chatbot():
    text = request.get_json().get("message")
    # TODO: check if text is valid 
    response = get_response(text)
    message={"answer": response}
    return jsonify(message)




if __name__ == '__main__':
      app.run(host='0.0.0.0', port=8000, debug=True)