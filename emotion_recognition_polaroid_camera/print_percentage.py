import RPi.GPIO as GPIO
from escpos.printer import Usb
import boto3
import time
import os

PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN, GPIO.IN)
IMAGEPATH = '/home/pi/Pictures/face.jpg'
FEATURES_BLACKLIST = ("Landmarks", "Emotions", "Pose", "Quality", "BoundingBox", "Confidence")
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

while FLAG:
    if(GPIO.input(PIN)):
        print(GPIO.input(PIN))
        print("Caught")
        os.system('fswebcam -S 10 ' + IMAGEPATH)
        usb = Usb(0x067b, 0x2303,0, out_ep=0x2)
        usb.cut()
        usb.image(IMAGEPATH)

        with open(IMAGEPATH, 'rb') as source_image:
            source_bytes = source_image.read()

        for face in detect_faces(source_bytes):
            print("Face ({Confidence}%)".format(**face))
        for emotion in face['Emotions']:
            print("  {Type} : {Confidence}%".format(**emotion))
            usb.text("  {Type} : {Confidence}% \n".format(**emotion))
        for quality, value in face['Quality'].items():
            print("  {quality} : {value}".format(quality=quality, value=value))
            usb.text("  {quality} : {value}\n".format(quality=quality, value=value))

        usb.cut()
        FLAG = False
        GPIO.cleanup()
    else:
        print("nothing special")
        time.sleep(1)
