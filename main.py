# ------------------------ Import Libraries and Packages ------------------------
import os
import pickle
import time
import cv2
import face_recognition
import tkmessagebox
from flask import Flask, render_template, request, Response
from imutils import paths
from pymongo import MongoClient


# ------------------------ Connect to MongoDB Server & Create FLASK app ------------------------
# Flask App Create
app = Flask(__name__, template_folder='templates', static_folder='static')

# MongoDB Database Connection
mongodb_uri = "mongodb+srv://zamilza51:zamilza51@cluster0.msilet9.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongodb_uri)
# Database Create
db = client["Security_Surveillance"]
# Collections Create
log_sign = db["Login_Signup"]
register = db["Face_Info_Registration"]

cfp = os.path.dirname(cv2.__file__) + "/data/haarcascade_frontalface_alt2.xml"
face_cascade = cv2.CascadeClassifier(cfp)


# ------------------------ Connect all Web Pages ------------------------
# Program Pages Start (home)
@app.route('/')
def home_page():
    return render_template('Main.html')


# Home Page Before LogIn
@app.route('/Main')
def home_before_login_page():
    video.release()
    return render_template('Main.html')


# Home Page After LogIn
@app.route('/Home')
def home_after_login_page():
    video.release()
    return render_template('Home.html')


# LogIn Page
@app.route('/Login')
def login_page():
    return render_template('Login.html')


# SignUp Page
@app.route('/SignUp')
def sign_up_page():
    return render_template('SignUp.html')


# Registration Page
@app.route('/Registration')
def registration_page():
    video.release()
    return render_template('Registration.html')


# Update_Information Page
@app.route('/Update_Information')
def update_info_page():
    video.release()
    return render_template('Update_Information.html')


# Surveillance Page
@app.route('/Surveillance')
def surveillance_page():
    return render_template('Surveillance.html')


# About Page
@app.route('/About')
def about_page():
    return render_template('About.html')


# About Page 2
@app.route('/About_After_LogIn')
def about2_page():
    video.release()
    return render_template('About_After_LogIn.html')


# ------------------------ Functions for Each Features ------------------------
# User SignUp Form
@app.route('/signup_form', methods=['POST', 'GET'])
def signup_form():
    if request.method == 'POST':
        ins_name = request.form['Institute_Name']
        email = request.form['Email']
        username = request.form['Username']
        pwd = request.form['Password']
        cn_pwd = request.form['Confirm_Password']

        if log_sign.find_one({"Username": username}) is None:
            if pwd == cn_pwd:
                # valid and Insert
                UserDocument = {
                    "Institute_Name": ins_name,
                    "Email": email,
                    "Username": username,
                    "Password": pwd
                }
                log_sign.insert_one(UserDocument)
                return render_template('login.html')
            else:
                return render_template('SignUp.html',
                                       info="Enter Same Password Twice !")  # Not Same Password and enter same password
        else:
            return render_template('SignUp.html',
                                   info="User Name Exist ! Try another.")  # Invalid User and try new username


# User LogIn Form
@app.route('/login_form', methods=['POST', 'GET'])
def login_form():
    if request.method == 'POST':
        username = request.form['Username']
        pwd = request.form['Password']

        if log_sign.find_one({"Username": username}) is None:
            return render_template('login.html', info='Invalid User')
        else:
            if log_sign.find_one({"Password": pwd}) is None:
                return render_template('login.html', info='Invalid Password')
            else:
                return render_template('Home.html', info=username)


# Member Registration Form
@app.route('/registration_form', methods=['POST', 'GET'])
def registration_form():
    if request.method == 'POST':
        full_name = request.form['Full_Name']
        nsu_id = request.form['NSU_ID']
        department = request.form['Department']
        email = request.form['Email']
        contact_num = request.form['Contact_Number']
        designation = request.form['Designation']

        if register.find_one({"NSU_ID": nsu_id}) is None:
            if register.find_one({"Email": email}) is None:
                if os.path.isdir(f'faces/{nsu_id}') is False:
                    # valid and Insert
                    UserDocument = {
                        "Full_Name": full_name,
                        "NSU_ID": nsu_id,
                        "Department": department,
                        "Email": email,
                        "Contact_Number": contact_num,
                        "Designation": designation
                    }
                    # Insert Data In MongoDB
                    register.insert_one(UserDocument)
                    # Create a directory for the user
                    os.makedirs(f'faces/{nsu_id}')
                    # Initialize webcam
                    cap = cv2.VideoCapture(0)

                    # Register faces
                    total_time = 10
                    start_time = time.time()
                    count = 0
                    while time.time() - start_time < total_time:
                        if count < 20:
                            ret, img = cap.read()
                            cv2.imshow('Capturing image', img)

                            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                            faces = face_cascade.detectMultiScale(gray, 1.2, 5)
                            for (x, y, w, h) in faces:
                                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                                roi_gray = gray[y:y + h, x:x + w]
                                # roi_color = img[y:y + h, x:x + w]
                                cv2.imwrite(f'faces/{nsu_id}/{count}.jpg', roi_gray)
                                count += 1
                            cv2.waitKey(50)

                    # Release webcam
                    cap.release()
                    cv2.destroyAllWindows()

                    return render_template('Home.html', info=" Successfully Registered. ")
                else:
                    return render_template('Registration.html',
                                           info=" This Person is Already Registered in faces !!")  # person registered
            else:
                return render_template('Registration.html',
                                       info=" This Person's Email is Already Registered !!")  # person is registered
        else:
            return render_template('Registration.html',
                                   info=" This Person's ID is Already Registered in DB !!")  # person is registered


# Encode image from faces directory
@app.route('/encode')
def encod():
    # get paths of each file in folder named Images
    #  here that contains data(folders of various people)
    imagePath = list(paths.list_images("faces"))
    kEncodings = []
    kNames = []

    # loop over the image paths
    for (i, ip) in enumerate(imagePath):
        # extract the person name from the image path
        name = ip.split(os.path.sep)[-2]
        # load the input image and convert it from BGR
        image = cv2.imread(ip)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model='hog')
        # compute the facial embedding for any face
        encodings = face_recognition.face_encodings(rgb, boxes)

        # loop over the encodings
        for encoding in encodings:
            kEncodings.append(encoding)
            kNames.append(name)

    # save encodings along with their names in dictionary data
    data_en_name = {"encodings": kEncodings, "names": kNames}

    # use pickle to save data into a file for later use
    file = open("face_name_encode", "wb")
    # to open file in write mode
    file.write(pickle.dumps(data_en_name))
    # to close file
    file.close()
    return "Images encoded successfully!"


# Surveillance

video = cv2.VideoCapture(0)

face_cascade.load(cv2.samples.findFile("static/haarcascade_frontalface_alt2.xml"))

data = None

try:
    with open('face_name_encode', "rb") as f:
        data = pickle.load(f)
except FileNotFoundError:
    tkmessagebox.showinfo("Camera Surveillance System", "face_name_encode not found!")


# Recognizing faces
def process_frame(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    small_frame = cv2.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
    boxes = face_recognition.face_locations(small_frame, model='hog')
    encodings = face_recognition.face_encodings(small_frame, boxes)

    names = []
    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            count = {}

            for i in matchedIdxs:
                name = data["names"][i]
                count[name] = count.get(name, 0) + 1

            name = max(count, key=count.get)

        names.append(name)

    return boxes, names


# Printing outcome in resized_frame
def gen():
    video = cv2.VideoCapture(0)
    while True:
        ret, frame = video.read()

        if not ret:
            break

        scale_percent = 160
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 135)
        dim = (width, height)
        resized_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

        boxes, names = process_frame(resized_frame)

        for (top, right, bottom, left), name in zip(boxes, names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            if register.find_one({"NSU_ID": name}):
                person = register.find_one({"NSU_ID": name})
                cv2.rectangle(resized_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.rectangle(resized_frame, (left, bottom + 35), (right, bottom - 35), (0, 255, 0), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(resized_frame, name, (left + 6, bottom - 6), font, 1.0, (0, 0, 0), 2)
                cv2.putText(resized_frame, person["Designation"], (left + 6, bottom + 24), font, 1.0, (0, 0, 0), 1)
            else:
                output = name
                cv2.rectangle(resized_frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(resized_frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(resized_frame, output, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        ret, jpeg = cv2.imencode('.jpg', resized_frame)
        frame_data = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n\r\n')


# Sending video frame to web page
@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Member Info  Search And Update Form
@app.route('/search_and_update_form', methods=['POST', 'GET'])
def update_info():
    if request.method == 'POST':
        s_nsu_id = request.form['S_NSU_ID']
        full_name = request.form['Full_Name']
        nsu_id = request.form['NSU_ID']
        department = request.form['Department']
        email = request.form['Email']
        contact_num = request.form['Contact_Number']
        designation = request.form['Designation']

        # Update Persons Details
        UpdateUserDocument = {"$set": {
            "Full_Name": full_name,
            "NSU_ID": nsu_id,
            "Department": department,
            "Email": email,
            "Contact_Number": contact_num,
            "Designation": designation
        }}
        if register.find_one({"NSU_ID": s_nsu_id}) is None:
            return render_template('Update_Information.html', info=" ID NOT FOUND")  # Not Found
        else:
            register.find_one_and_update({"NSU_ID": s_nsu_id}, UpdateUserDocument)
            return render_template('Update_Information.html',
                                   info=" Update Personal Details Successful !!")  # Successful Update


# Main Function To Run Flask App
if __name__ == '__main__':
    app.run(debug=True)

# Close MongoDB Database Connection
client.close()
