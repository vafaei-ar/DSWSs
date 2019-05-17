from utils import *
import pandas as pd  

class Examiner(object):

    def __init__(self,sess_num):
    
    
        self.prefix = './outcomes/arxiv/'
        mdfilename = 'metadata.csv'
        if not os.path.exists(self.prefix+mdfilename):
            ch_mkdir(self.prefix)
            df = pd.DataFrame(columns=['topic','sessnum','refnum0'])
            df.to_csv(self.prefix+mdfilename,index=0)
        self.df = pd.read_csv(self.prefix+mdfilename)
        self.topic = self.df['topic'].iloc[[sess_num]].values[0]
        self.serie_num = self.df['sessnum'].iloc[[sess_num]].values[0]
        self.ref_num0 = self.df['refnum0'].iloc[[sess_num]].values[0]
        self.sess_num = sess_num
        
        self.filename = 'detail_'+str(sess_num)+'.csv'
        if not os.path.exists(self.prefix+self.filename):
            ch_mkdir(self.prefix)
            df_person = pd.DataFrame(columns=['email','result','refnum'])
            df_person.to_csv(self.prefix+self.filename,index=0) 
        self.df_person = pd.read_csv(self.prefix+self.filename)  
        
        self.n_per,_ = self.df_person.shape
        
    def get_params(self):
        return self.ref_num0,self.serie_num,self.topic

    def examine(self,msgfrom,exerc):
        results = []
        anws = exerc.split('##########')
        nans = len(anws)
        for i in range(nans-1):
            res = exam_core(self.sess_num,i,anws[i])
            results.append(res)
            
        sress = ''.join(['0' if i else '1' for i in results])
        self.df_person.loc[self.n_per+1] = [msgfrom,sress,self.ref_num0+self.n_per+1]
        self.n_per = self.n_per+1
        
        self.df_person.to_csv(self.prefix+self.filename,index=0)
        
        return results
        

def exam_core(serie_num,i_question,answer):
    if serie_num==0:
        if i_question==0:
            return show(answer)
        
        elif i_question==1:
            return show(answer)
        
        elif i_question==2:
            return show(answer)
        
        elif i_question==3:
            return show(answer)
        
        elif i_question==4:
            return show(answer)

    assert 0,'Something went wrong in core!'




def show(answer):
    print('------------------------------------------')
    print(answer)
    x = int(input('Agree?\n'))
    print('------------------------------------------')
    return x 


    
