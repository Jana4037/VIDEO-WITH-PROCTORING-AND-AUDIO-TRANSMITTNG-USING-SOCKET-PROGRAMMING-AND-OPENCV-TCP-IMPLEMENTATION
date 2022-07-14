import socket, cv2
import imutils
import threading
import cv2
import mediapipe as pi
import wave, pyaudio
import time
import pickle
import struct

source=r"C:/Users/jana/Desktop/cnproj/haarcascade_eye.xml"
eye_class = cv2.CascadeClassifier(source)

source2=r"C:/Users/jana/Desktop/cnproj/haarcascade_frontalface_default.xml"
face_class = cv2.CascadeClassifier(source2)

#For storing the video
fourcc=cv2.VideoWriter_fourcc(*'XVID')
out=cv2.VideoWriter('detection2.avi',fourcc,20.0,(640,480))
#face detector (haar-casade)
def face_detector(img, size=0.5):
    gr = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_class.detectMultiScale(gr, 1.3, 5)
    if faces == ():
        return 0,img
    for (fx, fy, fw, fh) in faces:
        fh=fh+45
        fx=fx-42

        fy=fy-42
        fw=fw+45
        cv2.rectangle(img, (fx, fy), (fx + fw, fy + fh), (255, 0, 248), 2)
        rgray = gr[fy:fy + fh, fx:fx + fw]
        rcolor = img[fy:fy + fh, fx:fx + fw]
        eyes = eye_class.detectMultiScale(rgray)
        for (ix, iy, iw, ih) in eyes:
            cv2.rectangle(rcolor, (ix, iy), (ix + iw, iy + ih), (0, 39, 255), 2)
    return 1,img
#face detection(media pipe)
def face_detection(photo):
    FaceDet = pi.solutions.face_detection
    Draw = pi.solutions.drawing_utils
    faceDe = FaceDet.FaceDetection(0.75)
    iRGB = cv2.cvtColor(photo, cv2.COLOR_BGR2RGB)
    output = faceDe.process(iRGB)
    if output.detections:
        for index, detection in enumerate(output.detections):
            bxc = detection.location_data.relative_bounding_box
            hei, wid, c = photo.shape
            borx = int(bxc.xmin * wid), int(bxc.ymin * hei), int(bxc.width * wid), int(bxc.height * hei)
            cv2.rectangle(photo, borx, (255, 0, 255), 2)
            cv2.putText(photo, f'{int(detection.score[0] * 100)}%',
                        (borx[0], borx[1] - 20),cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)
        return 1,photo
    else:
        return 0,photo
#for audio receiving pyaudio stream is used
p = pyaudio.PyAudio()
CHUNK = 1024
stream = p.open(format=p.get_format_from_width(2),
                channels=2,
                rate=44100,
                output=True,
                frames_per_buffer=1024)
#For connection establishment
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hname = socket.gethostname()
hip = socket.gethostbyname(hname)
print('IP OF THE HOST:', hip)
port = 9777
addresssocket = (hip, port)
server_socket.bind(addresssocket)
server_socket.listen()

print("Listening at", addresssocket)

pop=''

j=int(input("INPUT 1: FOR AUDIO TRANSMISSION  2: FOR VIDEO PROCTORING  :  "))
if j==1:
    pop='A'
elif j==2:
    pop='V'
else:
    print("ENTERED INCORRECT NUMBER")



def show_client(addr, server_soc):

    try:
        print('CONNECTED/JOINED TO CLIENT {} '.format(addr),end='\n')
        if server_soc:  # if a client socket exists
            dat = b""
            palo_size = struct.calcsize("Q")
            while True:
                while len(dat) < palo_size:
                    packetofdata = server_soc.recv(50*1024)  # 4K
                    if not packetofdata:
                        break #comes out of loop
                    dat += packetofdata
                pacmsgsize = dat[:palo_size]
                dat = dat[palo_size:]
                sizeofmsg = struct.unpack("Q", pacmsgsize)[0]
                while len(dat) < sizeofmsg:
                    dat += server_soc.recv(4 * 1024)
                frame_data = dat[:sizeofmsg]
                dat = dat[sizeofmsg:]
                frame = pickle.loads(frame_data)

                if pop=='V':             #For video receiving and proctoring purpose
                    text = f"ADDRESS OF THE CLIENT: {addr}"
                    l,frame=face_detection(frame)
                    cv2.imshow(f"RECIEVED FROM {addr}",frame)
                    # sends the  message to client if video is not visible properly
                    if l==0:
                        server_soc.send(b"0")
                    elif l==1:
                         server_soc.send(b"1")
                    out.write(frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break

                if pop=='A':              #For audio receiving and playing purpose
                    stream.write(frame)
                    g = cv2.imread(r'C:\Users\jana\Desktop\cnproj\AFI.png')
                    g = imutils.resize(g, width=380)
                    cv2.imshow("FROM IMAGE", g)
                    key = cv2.waitKey(1)
                    if key == ord("q"):
                        break


            server_soc.close()

    except Exception as e:
        print(f"DISCONNECTION FROM CLIENT {addr} ")
        pass


while True:
        server_soc, addr = server_socket.accept()
        #uses the threading concept
        thre = threading.Thread(target=show_client, args=(addr, server_soc))
        thre.start()
        print("NO OF CLIENTS ", threading.active_count() - 1)
stream.close()