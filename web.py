
from sys import modules

from simplejson import dumps as json_dumps

from werkzeug.wrappers import Request, Response
from werkzeug.utils import redirect as http_redirect
from werkzeug.exceptions import HTTPException


def render(tpl_env, template, view):
    """Renders a view into a template given a template environment `tpl_env """
    return tpl_env.get_template(template).render(**view)


class BaseController(object):
    """Extendable base controller"""
    
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
        """Executes before the action"""
        pass
    
    def exit(self):
        """Executes after the action"""
        pass

    @property
    def response(self):
        """Returns the response, if given a template,
        renders a view and puts it as data of the response"""
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


def get_application(FrontControllerClass, appspace):
    """Retuns WSGI application given a front controller class 
    and application namespace"""
    
    def application(environ, start_response):
        request=Request(environ)
        fc=FrontControllerClass(request, appspace)
        return fc.response(environ, start_response)
        
    return application
    

class BaseFrontController(object):
    """Basic front controller, `dispatch` should be extended"""

    def __init__(self, request, appspace):
        self._request=request
        self.appspace=appspace
        self._is_finished=False
        
    def dispatch(self):
        raise NotImplementedError

    def _default_dispatch(self, controllers_path):
        """Returns controller class, action name and args given match on the rules"""
        try:
            endpoint, args = self.urls.match()
        except HTTPException, exc:
            endpoint, args = 'index|notfound', {}
        
        controller_name, action_name = endpoint.split('|')
        
        __import__(controllers_path+controller_name)
        controller_module = modules[controllers_path+controller_name]
        controller_class = controller_module.Controller

        return controller_class, action_name, args

        
    @property
    def response(self):
        if not self._is_finished:
            self.dispatch()
            self._is_finished=True
        return self._response
    
    @property
    def request(self):
        return self._request

        