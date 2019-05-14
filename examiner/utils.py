from __future__ import print_function
import os
import sys
import base64
import pickle
import os.path
import subprocess
import jalali,calendar

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase 
from email.mime.multipart import MIMEMultipart 

SCOPES = 'https://mail.google.com/'
FNULL = open(os.devnull, 'w')

def certificate_maker(file_name,p_name,serie_num,topic,stime,ref_num,prefix=''):
    f = open("template.tex", "r")
    tex_template = f.read()
    f.close()

    tex_p = tex_template.replace('{{{name}}}',p_name)
    tex_p = tex_p.replace('{{{series}}}',serie_num)
    tex_p = tex_p.replace('{{{topic}}}',topic)
    tex_p = tex_p.replace('{{{stime}}}',stime)
    tex_p = tex_p.replace('{{{ref}}}',ref_num)

    f = open(prefix+file_name+'.tex','w') 
    f.write(tex_p) 
    f.close() 
    flags = ''
    if prefix:
        flags = '-output-directory='+prefix
    subprocess.call(['xelatex', flags, prefix+file_name+'.tex'],
                    stdout=FNULL, stderr=subprocess.STDOUT)
    subprocess.call(['rm', prefix+file_name+'.aux'])
    subprocess.call(['rm', prefix+file_name+'.log'])
    subprocess.call(['rm', prefix+file_name+'.tex'])

def answer_it(service,msgfrom,msgsub,msgid,message_text='hi, there!',attachment=None):  
    message = create_message(sender='datascienceworkshops98@gmail.com',
                             to=msgfrom,
                             subject='Re: '+msgsub,
                             message_text=message_text,
                             replyto=msgid,
                             attachment=attachment)

    send_message(service, "me", message)


def fetch_them(prex='XX',sess_num=0,prefix='./test/',labelIds=['INBOX','UNREAD','CATEGORY_PERSONAL'],trace=0):

    sess_num = 'S'+str(sess_num).zfill(2)
    creds = check_token()
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    results = service.users().messages().list(userId='me', labelIds=labelIds).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
        exit()
    else:
        msgprops = []
        pesinfo = []
        succeed = []
        
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            hdrs = msg['payload']['headers']
            prts = msg['payload']['parts']
            msgid = findinheader(hdrs,'Message-ID')
            msgfrom = findinheader(hdrs,'From')
            msgdate = findinheader(hdrs,'Date')
            msgsub = findinheader(hdrs,'Subject')
            
            if msgsub[:2].upper()!=prex:
                continue
            try:
                ifex,num,fname,lname = msgsub.split('-')
            except:
                print('Something is wrong with',msgsub)
                msgprops.append([msgid,msgfrom,msgdate,msgsub])
                pesinfo.append([None,None])
                succeed.append(getfile)
                continue
            
            getfile = False
            if ifex.upper()==prex and num.upper()==sess_num:
                for part in msg['payload']['parts']:
                    try:
                        if part['filename']:
                            if 'data' in part['body']:
                                data=part['body']['data']
                            else:
                                att_id=part['body']['attachmentId']
                                att=service.users().messages().attachments().get(userId='me', messageId=message['id'],id=att_id).execute()
                                data=att['data']
                            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                            path = prefix+fname+'-'+lname
                            data = file_data.decode(sys.stdout.encoding)
                            assert '##########' in data,'error'
                            if os.path.exists(path):
                                print('It exists: ',end='')
                                assert 0,'error'
                            with open(path, 'w') as f:
                                f.write(data)
                            getfile = True
                    except:
                        pass
                
                if getfile:  
                    print(ifex,num,fname,lname)
                    if trace:         
                        service.users().messages().modify(userId='me', id=message['id'],body={ 'removeLabelIds': ['UNREAD']}).execute() 
                else:
                    print('Something went wrong with',msgsub)
                msgprops.append([msgid,msgfrom,msgdate,msgsub])
                pesinfo.append([fname,lname])
                succeed.append(getfile)
                
        return service,msgprops,pesinfo,succeed


def findinheader(header,name):
    for i in header:
        if i['name']==name:
            return i['value']

def check_token(creds = None):
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def ch_mkdir(directory):
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except:
            print('could not make the directory!')

def create_message(sender, to, subject, message_text,replyto=None,attachment=None):
#    message = MIMEText(message_text)
#    message['to'] = to
#    message['from'] = sender
#    message['subject'] = subject

#    if replyto is not None:
#        message['In-Reply-To'] = replyto
#        message['References'] = replyto

    # instance of MIMEMultipart 
    msg = MIMEMultipart() 
      
    # storing the senders email address   
    msg['From'] = sender 
      
    # storing the receivers email address  
    msg['To'] = to
      
    # storing the subject  
    msg['Subject'] = subject
    
    if replyto is not None:
        msg['In-Reply-To'] = replyto
        msg['References'] = replyto

    # attach the body with the msg instance 
    msg.attach(MIMEText(message_text, 'plain')) 
 
    if attachment is not None:
        # open the file to be sent  
        fileadd = attachment
        
        attachment = open(fileadd, "rb") 
        filename = fileadd.split('/')[-1]
          
        # instance of MIMEBase and named as p 
        p = MIMEBase('application', 'octet-stream') 
          
        # To change the payload into encoded form 
        p.set_payload((attachment).read()) 
          
        # encode into base64 
        encoders.encode_base64(p) 
           
        p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
          
        # attach the instance 'p' to instance 'msg' 
        msg.attach(p) 
      
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode()).decode()}
  
  
def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('The message is sent, Id: %s' % message['id'])
    return message
  except HttpError as error:
    print('An error occurred: %s' % error)


def date_convert(x):
    p_month = [ 
'فروردین',
'اردیبهشت',
'خرداد',
'تیر',
'مرداد',
'شهریور',
'مهر',
'آبان',
'آذر',
'دی',
'بهمن',
'اسفند'
]

    return p_month[x-1]

def dt_conv(datetime):
    dw,day,month,year,tim,delt =  datetime.split(' ')
    months_name2num = dict((v,k) for k,v in enumerate(calendar.month_abbr))
    #tim = tim.split(':')
    #tim[0] = int(tim[0])+int(delt[1:3])
    #tim[1] = int(tim[1])+int(delt[3:])
    #hour = tim[0]
    month = months_name2num[month]
    year,month,day = jalali.Gregorian(int(year),month,int(day)).persian_tuple()
    month = date_convert(month)
    ptime = str(day)+' '+month+' '+str(year)
    return ptime
