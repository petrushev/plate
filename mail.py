
from smtplib import SMTP

from email.mime.text import MIMEText
from email.utils import formataddr, formatdate


class BaseMail(object):
    
    def __init__(self, conf):
        
        self._message = MIMEText('')
        self._message['From'] = formataddr(conf['sender'])
        
        self._sender = conf['sender'][1]
    
        self._recepients=[]
        
        self._conf = conf

    def __setattr__(self, key, val):
        if key=='body':
            self._message._payload=str(val)
        elif key=='subject':
            self._message['Subject']=val
        else:
            object.__setattr__(self, key, val)


    def add_header(self, header_name, header_value):
        self._message.add_header(header_name, header_value)

        
    def add_to(self, name, email):
        if name=='' or name is None:
            name=False
            
        self._recepients.append((name, email))
        

    def send(self):
        if len(self._recepients)==0:
            return

        emails=[email for name, email in self._recepients]
        self._message['To']=", ".join([formataddr(pair)\
                                       for pair in self._recepients])
        
        # start server and send
        conf = self._conf
        self._server = SMTP(conf['smtp']['server'], conf['smtp']['port'])
        if conf['smtp']['tls']: self._server.starttls() 
        
        self._server.login(conf['smtp']['user'], conf['smtp']['password'])
        
        self._server.set_debuglevel(conf['debug_level'])
        
        self._server.sendmail(self._sender, emails, self._message.as_string())
        

    def __del__(self):
        try:
            server = self._server
        except AttributeError:
            pass
        else:
            server.quit()

