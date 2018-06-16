#! /usr/bin/python3
# source : https://community.home-assistant.io/t/foscam-easily-add-motion-sensor-and-other-control/4433
from io import StringIO
import requests, sys, time, subprocess, smtplib, glob, os, configparser
#import models.tutorials.image.imagenet.classify_image as ci
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def getMotionAlert():
    #url = ""
    response = requests.get(config['env']['url_status'])
    #result = str(response.content).strip().split(';\\n')[6].split('=')[1]
    result = str(response.content).strip().split(';')[6].split('=')[1]  
    # 0-No Alarm, 1-motion alarm, 2-input Alarm
    return result

def getSnapshot():
    response = requests.get(config['env']['url_snap'])
    f = open('images/snap'+time.strftime('%Y-%m-%d-%H:%M:%S')+'.jpg','wb')
    f.write(response.content)
    f.close()

def getMotionStatus(ip, usr, pwd):
    pass

def setMotionStatus(ip, usr, pwd, enabled):
    pass

def send_mail(filename):
    gmailUser = 'bored.robot.1701d@gmail.com'
    gmailPassword = config['cred']['passwd']
    recipient = 'rajanish.rajagopalan@gmail.com'
    message = 'Front Door Alert'
    
    msg = MIMEMultipart()
    msg['From'] = gmailUser
    msg['To'] = recipient
    msg['Subject'] = 'Front Door ' + time.strftime('%Y%m%d-%H:%M:%S')
    msg.attach(MIMEText(message))
    
    attachment = open(filename, "rb")
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(part)
    
    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmailUser, gmailPassword)
    mailServer.sendmail(gmailUser, recipient, msg.as_string())
    mailServer.close()

def send_crash_email(err_msg):
    gmailUser = 'bored.robot.1701d@gmail.com'
    gmailPassword = config['Cred']['passwd']
    recipient = 'rajanish.rajagopalan@gmail.com'
    message = 'Guard crashed - ' + str(err_msg)
    
    msg = MIMEMultipart()
    msg['From'] = gmailUser
    msg['To'] = recipient
    msg['Subject'] = 'Guard Crashed at ' + time.strftime('%Y%m%d-%H:%M:%S')
    msg.attach(MIMEText(message))
    
    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmailUser, gmailPassword)
    mailServer.sendmail(gmailUser, recipient, msg.as_string())
    mailServer.close()

def monitor():
    try:
        while True:
            result = getMotionAlert()
            result = '1' 
            if result=='1':
                getSnapshot()
                #subprocess.call('models/tutorials/image/imagenet/classify_image.py --image_file=/home/rajanish/Projects/test.jpg',shell=True)
                list_of_files = glob.glob('images/*')
                latest_file = max(list_of_files, key=os.path.getctime)
                send_mail(latest_file)
                time.sleep(60)
                #print('Some one is here')
            else:
                pass
                #print('All Clear: Sleeping for 5 seconds')
            time.sleep(3) # wait for x seconds before checking the camera alert status again
    except (TimeoutError, ConnectionResetError, ConnectionRefusedError, ConnectionAbortedError,
            BrokenPipeError, ConnectionError, OSError, ValueError) as e:
        print (time.strftime('%Y%m%d-%H:%M:%S'),e)
        time.sleep(60)
        monitor()
    except Exception as e:
        print('### Failed :' + time.strftime('%Y-%m-%d-%H:%M:%S'))
        send_crash_email(e)
        print(e)

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.sections()
    config.read('Config.ini')
    monitor()