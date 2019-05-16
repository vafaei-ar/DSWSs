from __future__ import print_function
import sys
from utils import *
from examinertool import Examiner

prefixex = './outcomes/S01/ex/'
prefixcert = './outcomes/S01/certs/'

ch_mkdir(prefixex)
ch_mkdir(prefixcert)

examiner = Examiner(0)

ref_num0,serie_num,topic = examiner.get_params()

service,msgprops,pesinfo,succeed = fetch_them(prex='E',
                                      sess_num=1,
                                      prefix=prefixex,
                                      trace=0)

msg_num = len(succeed)

def res_conv(results):
    out = '\n'
    for i,res in enumerate(results):
        if res:
            out = out+'صحیح .'+str(i)+' سوال'
        else:
            out = out+'اشتباه .'+str(i)+' سوال'
        out = out+'\n'
    return out

for i in range(msg_num):
    msgid,msgfrom,msgdate,msgsub = msgprops[i]
    if succeed[i]:
        fname,lname = pesinfo[i]   
        print('Answering to ',fname,lname,', succeed!')
        file_name = fname+'_'+lname
        fil = open(prefixex+fname+'-'+lname, 'r')
        exerc = fil.read()
        p_name = exerc.split('##########')[-1].strip()
        results = examiner.examine(msgfrom,exerc)
        ref_num = str(ref_num0+examiner.n_per)
        ptime = dt_conv(msgdate)
        
        print(results)
        print(res_conv(results))
        
        if all(results):
            certificate_maker(file_name,p_name,serie_num,topic,ptime,ref_num,prefix=prefixcert)
            answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\n Here is your results! :)\n\n\
            Cheers,\nExaminer script.',attachment=prefixcert+file_name+'.pdf')
            
        else:
            answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\nSorry, the code could not examine your code and \
provide the certificate for your script. The result is: '+res_conv(results)+'\n\
You may want to check your script with the instructor in person.\n\n\
Cheers,\nExaminer script.')
            
    else:
        print('Answering to ',msgsub,', missed!')
        answer_it(service,msgfrom,msgsub,msgid,message_text='Hello;\n\nSorry we could not get the exercise properly. \
You have sent a newer version of the exercise or \
you need to check that you are following the instructions.\n\n\
For more informations see (https://github.com/vafaei-ar/DSWSs).\n\n\
Cheers,\nExaminer script.')


