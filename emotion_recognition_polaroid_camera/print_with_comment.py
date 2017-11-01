import RPi.GPIO as GPIO
from escpos.printer import Usb
import boto3, time, os, sys, select

SW_PIN = 9
GPIO.setmode(GPIO.BCM)
GPIO.setup(SW_PIN, GPIO.IN)

# IMG PATH
IMGFACE = '/home/pi/Pictures/face.jpg'
IMGHAPPY = '/home/pi/Pictures/print_happy.jpg'
IMGSAD = '/home/pi/Pictures/print_sad.jpg'
IMGCONFUSED = '/home/pi/Pictures/print_confused.jpg'

FLAG = True

def detect_faces(source_bytes):
    session = boto3.Session(aws_access_key_id='<AWS ACCESS KEY ID>',
                        aws_secret_access_key='<AWS SECRET KEY>',
                        region_name='<REGION NAME>')
    client = session.client('rekognition')

    response = client.detect_faces(
        Image={
            'Bytes': source_bytes
        },
        Attributes=['ALL']
    )

    return response['FaceDetails']

try:
    while FLAG:
        os.system('cls' if os.name == 'nt' else 'clear')
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            line = raw_input()
            break
        if GPIO.input(SW_PIN) == GPIO.HIGH:
            print("Caught")
            os.system('fswebcam -S 10 ' + IMGFACE)
            usb = Usb(0x067b, 0x2303,0, out_ep=0x2)
            usb.cut()
            usb.image(IMGFACE)
            with open(IMGFACE, 'rb') as source_image:
                source_bytes = source_image.read()

            time.sleep(1)
            for face in detect_faces(source_bytes):
                usb.text("Face ({0:.2f}%)\n".format(face['Confidence']))

            for emotion in face['Emotions']:
                usb.text("  {Type} : {Confidence}% \n".format(**emotion))
                emotion_type = emotion['Type']
                idx = float("{0:.2f}".format(emotion['Confidence']))

                if emotion_type == "HAPPY" and idx > 70:
                    usb.image(IMGHAPPY)
                if emotion_type == "SAD" and idx > 10:
                    usb.image(IMGSAD)
                if emotion_type == "CONFUSED" and idx > 10:
                    usb.image(IMGCONFUSED)
                if emotion_type == "ANGRY" and idx > 10:
                    usb.image(IMGSAD)

            usb.cut()
            time.sleep(8)
        else:
            print("nothing special")
            time.sleep(1)

except KeyboardInterrupt:
    print ( "KeyboardInterrupt\n" )

finally:
    GPIO.cleanup()
