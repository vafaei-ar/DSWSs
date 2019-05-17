from __future__ import print_function
import sys
from utils import *
from examinertool import Examiner



prefixex = './outcomes/S01/ex/'
prefixcert = './outcomes/S01/certs/'

ch_mkdir(prefixex)
ch_mkdir(prefixcert)

examiner = Examiner(0)



creds = check_token()
service = build('gmail', 'v1', credentials=creds)

while True:

    msgprops,pesinfo,succeed = fetch_them(service,
                                          prex='EX',
                                          sess_num=1,
                                          prefix=prefixex,
                                          trace=0, onlyone=1)
                                          
    if not msgprops:
        print('No email remained!')
        break

    check_replay(service,examiner,succeed,msgprops,pesinfo,
                 prefixex=prefixex,prefixcert=prefixcert,trace=1)






