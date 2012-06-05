
import warnings

from sqlalchemy.schema import MetaData
from sqlalchemy.orm import mapper, sessionmaker, clear_mappers
from sqlalchemy.orm.session import object_session 
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import SAWarning

def reflect(engine, models, schema=None):
    
    metadata = MetaData()
    metadata.bind = engine 
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=SAWarning)
        metadata.reflect(schema=schema)

    if schema is not None:
        tables = dict( (table_name.replace(str(schema)+".", ""), table)
                      for table_name, table in metadata.tables.iteritems() )
    else:
        tables = metadata.tables
    
    clear_mappers()
    
    mappers = {}
    for table_name, table in tables.iteritems():
        modelname = "".join([word.capitalize() for word in table_name.split("_")])
        
        try: 
            model = getattr(models, modelname)
        except AttributeError:
            #raise NameError, "Model %s not found in %s" % (modelname, str(models))
            pass
        else:
            mappers[modelname] = mapper(model, table)
            
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=True)
    
    return mappers, tables, Session


def column(attr):
    """Returns reflected column"""
    return attr.parententity.mapped_table._columns[attr.key]

def column_type(attr):
    """Returns reflected type"""
    return column(attr).type

def enum_values(attr):
    """Returns list of values in enum field"""
    return column(attr).type.enums

def length(attr):
    """Returns length of field"""
    return column(attr).type.length


class BaseModel(object):
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def session(self):
        return object_session(self)

    def drop(self):
        self.session.delete(self)

    @classmethod
    def load(cls, session, **kwargs):
        q = session.query(cls)
        for key, val in kwargs.items():
            field = getattr(cls, key)
            q = q.filter(field==val)
        try:
            return q.one()
        except MultipleResultsFound, exc:
            raise MultipleResultsFound, str(exc)+" on model "+repr(cls)
        except NoResultFound, exc:
            raise NoResultFound, str(exc)+" on model "+repr(cls)
            
    @classmethod
    def load_multiple(cls, session, **kwargs):
        q = session.query(cls)
        for key in kwargs:
            val = kwargs[key]
            field = getattr(cls, key)
            q = q.filter(field==val)
            return q.all()
