import socket
import imutils  # pip install imutils
import pyaudio
import wave
import cv2, struct
import pickle

#To capture the videos
cam = True
if cam == True:
    proc = cv2.VideoCapture(0)
else:
    proc = cv2.VideoCapture(r"C:\Users\jana\Desktop\cnproj\jan.mp4")


#For socket connection
cli= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hip = '192.168.56.1'

port = 9777
cli.connect((hip, port))
print('server listening at', (hip, port))

#opening wave file in read mode
wf = wave.open(r'C:\Users\jana\Desktop\cnproj\2.wav', 'rb')

p = pyaudio.PyAudio()  # Pyaudio is a class and stored in variable(instance)

CHUNK = 1024
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                input=True,
                channels=wf.getnchannels(),
                frames_per_buffer=CHUNK,
                rate=wf.getframerate()
                )


j = int(input("INPUT 1: FOR AUDIO TRANSMISSION  2: FOR VIDEO PROCTORING :  "))

if cli:
    while True:
        if j == 2:
            #For sending video to server
            img, frame = proc.read()                      #reads the video
            picA = pickle.dumps(frame)                    #convert into byte stream
            mes = struct.pack("Q", len(picA)) + picA  #string of bytes is made to send
            cli.sendall(mes)                #sends the message
            msg2 = cli.recv(2048).decode()      #the message is recieved if video is not alligned or
                                                          #visible properly
            if msg2=='0':
                #shows in the client scene when video is not visible properly
                cv2.putText(frame, f'{"FACE NOT ALLIGNED PROPERLY"}', (80, 40), cv2.FONT_HERSHEY_PLAIN, 2, (245, 55, 98), 3)
            cv2.imshow(f"TO: {hip}", frame)           #to show the video in client screen
            k = cv2.waitKey(1)
            if k == ord("q"):                           #quits the screen if q is pressed
                cli.close()
                break

        elif j == 1:
            # For sending audio to server
            dat = None
            try:
                data = wf.readframes(CHUNK)
                a = pickle.dumps(dat)
                mes = struct.pack("Q", len(a)) + a
                cli.sendall(mes)
                s = len(dat)
                #shows image when audio is transmitting
                g = cv2.imread(r'C:\Users\jana\Desktop\cnproj\AFI.png')
                g = imutils.resize(g, width=380)
                cv2.imshow(" TO IMAGE", g)
                k = cv2.waitKey(1)
                if k == ord("q"):
                    break

            except:
                cli.close()
        else:
            print("ENTERED A INCORRECT NUMBER")
            break


