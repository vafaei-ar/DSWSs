from __future__ import print_function
import os
import sys
import base64
import pickle
import os.path
import subprocess
import unicodedata
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


def fetch_them(service,prex='XX',
               sess_num=0,
               prefix='./test/',
               labelIds=['INBOX','UNREAD','CATEGORY_PERSONAL'],
               trace=0,
               onlyone=None,
               replace=0):

    sess_num = 'S'+str(sess_num).zfill(2)
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    results = service.users().messages().list(userId='me', labelIds=labelIds).execute()
    messages = results.get('messages', [])
    
    
#    for message in messages:
#        msg = service.users().messages().get(userId='me', id=message['id']).execute()
#        hdrs = msg['payload']['headers']
#        msgsub = findinheader(hdrs,'Subject')
#        if msgsub[:2].upper().strip()!=prex:
#            print(msgsub,msgsub[:2].upper().strip())
#    print(len(messages))
#    exit()


    message = messages[0]
    msg = service.users().messages().get(userId='me', id=message['id']).execute()
    hdrs = msg['payload']['headers']
    msgsub = findinheader(hdrs,'Subject')
#    print(msgsub,msgsub[:2].upper().strip(),prex,msgsub,msgsub[:2].upper().strip()==prex)

    if not messages:
        print("No messages found.")
        exit()
    else:
        msgprops = []
        pesinfo = []
        succeed = []
        
        for message in messages:
            getfile = 0
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            hdrs = msg['payload']['headers']
            prts = msg['payload']['parts']
            msgid = findinheader(hdrs,'Message-ID')
            msgfrom = findinheader(hdrs,'From')
            msgdate = findinheader(hdrs,'Date')
            msgsub = findinheader(hdrs,'Subject')
            
            msgsub = msgsub.replace('Fwd: ','')
            msgsub = msgsub.replace('Re: ','')
            
            xx = msgsub[:6].upper().strip()
            xx = unicodedata.normalize('NFC', xx.encode().decode('utf8'))
            
            if xx!=prex+'-'+sess_num:
                continue
            try:
                ifex,num,fname,lname = msgsub.split('-')
            except:
                print('Something is wrong with the subject:',msgsub)
                getfile = 5
                msgprops.append([message['id'],msgid,msgfrom,msgdate,msgsub])
                pesinfo.append([None,None])
                succeed.append(getfile)
                if trace:         
                    service.users().messages().modify(userId='me', id=message['id'],body={ 'removeLabelIds': ['UNREAD']}).execute()  
                continue
            
            xx = ifex.upper().strip()
            if unicodedata.normalize('NFC', xx.encode().decode('utf8'))==prex and num.upper()==sess_num:
                for part in msg['payload']['parts']:

                    if part['filename']:
                    
                        try:
                            if 'data' in part['body']:
                                data=part['body']['data']
                            else:
                                att_id=part['body']['attachmentId']
                                att=service.users().messages().attachments().get(userId='me', messageId=message['id'],id=att_id).execute()
                                data=att['data']
                                
                            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                            path = prefix+fname+'-'+lname
                            
                            data = file_data.decode(sys.stdout.encoding)#,"ignore")
                        except:
                            print('Something is wrong with the file type or download!')
                            getfile = 3

                        if not '##########' in data:
                            if getfile==0:
                                print('Hash error!')
                                getfile = 4                        
                        
                        if os.path.exists(path) and not replace:
                            getfile = 2
                            print('File exists')
                            
                        if getfile==0:
                            with open(path, 'w') as f:
                                f.write(data)
                            getfile = 1
                
                msgprops.append([message['id'],msgid,msgfrom,msgdate,msgsub])
                pesinfo.append([fname,lname])
                succeed.append(getfile)
                if onlyone:
                    break
            else:
                print('Something is wrong with the subject:',msgsub)
                getfile = 5
                msgprops.append([message['id'],msgid,msgfrom,msgdate,msgsub])
                pesinfo.append([None,None])
                succeed.append(getfile)
                if trace:         
                    service.users().messages().modify(userId='me', id=message['id'],body={ 'removeLabelIds': ['UNREAD']}).execute()  
                    
            if trace:         
                service.users().messages().modify(userId='me', id=message['id'],body={ 'removeLabelIds': ['UNREAD']}).execute()     
     
        if onlyone and len(msgprops)==1:
            msgprops = msgprops[0]
            pesinfo = pesinfo[0]
            succeed = succeed[0] 
        return msgprops,pesinfo,succeed


def res_conv(results):
    out = '\n'
    for i,res in enumerate(results):
        if res:
            out = out+'صحیح .'+str(i)+' سوال'
        else:
            out = out+'اشتباه .'+str(i)+' سوال'
        out = out+'\n'
    return out

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
  
  
def send_message(service, user_id, message, trace=0):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    input('Enter to send!')
    if trace:         
        service.users().messages().modify(userId='me', id=trace,body={ 'removeLabelIds': ['UNREAD']}).execute()
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('The message is sent, Id: %s' % message['id'])
        return message
    except HttpError as error:
        print('An error occurred: %s' % error)

def answer_it(service,msgfrom,msgsub,msgid,message_text='hi, there!',attachment=None, trace=0):  
    message = create_message(sender='datascienceworkshops98@gmail.com',
                             to=msgfrom,
                             subject='Re: '+msgsub,
                             message_text=message_text,
                             replyto=msgid,
                             attachment=attachment)

    send_message(service, "me", message, trace = trace)
    
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
#    datetime = datetime.replace(' (UTC)','')
    datetime = datetime[:31]
    print(datetime)
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
    
    
def check_replay(service,examiner,succeed,msgprops,pesinfo,prefixex,prefixcert, trace=0):

    ref_num0,serie_num,topic = examiner.get_params()
    ID,msgid,msgfrom,msgdate,msgsub = msgprops
    ref_num = str(ref_num0+examiner.n_per)
    ptime = dt_conv(msgdate)
    if trace:
        trace = ID
    
#    # OK    
#    getfile = 1
    if succeed==1:
        fname,lname = pesinfo 
        print('Answering to ',fname,lname,', succeed!')
        file_name = fname+'_'+lname
        fil = open(prefixex+fname+'-'+lname, 'r')
        exerc = fil.read()
        p_name = exerc.split('##########')[-1].strip()
        results = examiner.examine(msgfrom,exerc)
        
        print(succeed)
        
        if all(results):
            certificate_maker(file_name,p_name,serie_num,topic,ptime,ref_num,prefix=prefixcert)
            answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\nHere is your results! :)\n\n\
Cheers,\nExaminer script.',attachment=prefixcert+file_name+'.pdf',trace=trace)
            
        else:
            answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\nSorry, the code could not examine your code and \
provide the certificate for your script. The result is: '+res_conv(results)+'\n\
You may want to check your script with the instructor in person.\n\n\
Cheers,\nExaminer script.',trace=trace)
            os.remove(prefixex+fname+'-'+lname)

#    # FILE EXISTS
#    getfile = 2      
    elif succeed==2:
        print(msgsub,': repeated email!')
        answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\nThis email will be ignored since there is \
a newer email with same subject\n\nCheers,\nExaminer script.',trace=trace)

#    # TYPE OR DOWNLOAD
#    getfile = 3
    elif succeed==3:
        agg = int(input('Type or download problem in '+msgsub+', agree? '))
        if not agg:
            answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\n\
Sorry we could not get the exercise file in the attachment properly. \
You need to check and follow the instructions.\n\n\
For more informations see (https://github.com/vafaei-ar/DSWSs).\n\n\
Cheers,\nExaminer script.',trace=trace)
        else:
            p_name = input('Name? ')
            file_name = p_name
            certificate_maker(file_name,p_name,serie_num,topic,ptime,ref_num,prefix=prefixcert)
            answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\nHere is your results! :)\n\n\
Cheers,\nExaminer script.',attachment=prefixcert+file_name+'.pdf',trace=trace)  

#    # HASH ERROR
#    getfile = 4  
    elif succeed==4:
        answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\nSorry we could not get the exercise properly. \
You may forgot the hash splitting as requested (https://github.com/vafaei-ar/DSWSs).\n\n\
Cheers,\nExaminer script.',trace=trace)

#    # SUBJECT NAME ERROR
#    getfile = 4  
    elif succeed==5:
        answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\nSorry we could not get the exercise properly. \
The email subject does not match the requested pattern (https://github.com/vafaei-ar/DSWSs).\n\n\
Cheers,\nExaminer script.',trace=trace)
  
    else:
        agg = int(input('Something unknown happened to '+msgsub+', agree? '))
        if not agg:
            answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\n\
Sorry we could not get the exercise file in the attachment properly. \
You need to check and follow the instructions.\n\n\
For more informations see (https://github.com/vafaei-ar/DSWSs).\n\n\
Cheers,\nExaminer script.',trace=trace)
        else:
            p_name = input('Name? ')
            file_name = p_name
            certificate_maker(file_name,p_name,serie_num,topic,ptime,ref_num,prefix=prefixcert)
            answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\nHere is your results! :)\n\n\
Cheers,\nExaminer script.',attachment=prefixcert+file_name+'.pdf',trace=trace)  





