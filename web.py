
from werkzeug.wrappers import Request, Response
from werkzeug.utils import redirect as http_redirect
from simplejson import dumps as json_dumps

def render(tpl_env, template, view):
    return tpl_env.get_template(template).render(**view)


class BaseController(object):
    
    def __init__(self, request, tpl_env, appspace, **kwargs):
        
        self._request = request
        self.appspace = appspace
        
        self._tpl_env=tpl_env
        
        # set blank template and empty view obj
        self.template = None
        self.view={'path': request.path,
                   'get': request.args}
        
        # set the controller log
        self._log=""
        
        # init response obj
        self._response = Response('', content_type="text/html; charset=UTF-8")
        self._response.status_code=200
        
        # rest of the initializers (db, session, etc) 
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    
    @property
    def request(self):
        return self._request
    
    @property
    def tpl_env(self):
        return self._tpl_env
    
    @property
    def log(self):
        return self._log
    
    def init(self):
        pass
    
    def exit(self):
        pass

    @property
    def response(self):
        if self.template:
            self._response.data = render(self._tpl_env, self.template, self.view)
            self._response.content_length = len(self._response.data)
        return self._response

    def add_log(self, text):
        self._log = self._log+text+"\n"
    
    def redirect(self, uri, permanent=False):
        code = 302
        if permanent: code = 301
        self.template = None
        self._response = http_redirect(uri, code)

    def not_found(self, template=None):
        self.template = template
        self._response.status_code = 404
        
    def method_not_allowed(self, template=None):
        self.template = template
        self._response.status_code = 405   

    def not_authorized(self, template=None):
        self.template = template
        self._response.status_code = 401   

    def bad_request(self, template=None):
        self.template = template
        self._response.status_code = 400   

    def return_json(self, json):
        self.template = None
        self._response.data = json_dumps(json)
        self._response.content_length = len(self._response.data)
        self._response.content_type="text/json"

