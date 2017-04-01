from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key, value in json_data.items():
            setattr(self, key, value)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        method = getattr(api_client, 'get_{}'.format(cls.RESOURCE_NAME))
        json_data = method(resource_id)
        return cls(json_data)
        '''
        #get_people(self, people_id=None, **params):
        if cls.RESOURCE_NAME == 'people':
            return People(api_client.get_people(resource_id))
        elif cls.RESOURCE_NAME ==  'films':
            return Films(api_client.get_films(resource_id))
        '''
            


    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        '''
        if cls.RESOURCE_NAME == 'people':
            #return PeopleQuerySet(api_client.get_people())
            return PeopleQuerySet.collection
        elif cls.RESOURCE_NAME ==  'films':
            #return FilmsQuerySet(api_client.get_films())
            return FilmsQuerySet.collection
        '''
        qs = "{}QuerySet".format(cls.RESOURCE_NAME.title())
        return eval(qs)()
        

class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)
        

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.page = 0
        self.item = 0
        self.collection = []
        self.counter=None
        
    def __iter__(self):
        return self.__class__()
        
    
    def _request_next_page(self):
        self.page += 1
        
        method = getattr(api_client, 'get_{}'.format(self.RESOURCE_NAME))
        json_data = method(**{'page': self.page})
        
        Model = eval(self.RESOURCE_NAME.title())
        for data in json_data['results']:
            self.collection.append(Model(data))        
        self.counter=json_data['count']
    
    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        #return each dictionary on a page
        #10 items per page - after 10 items, go to next page
        #if there are no more items, stop iteration
        
        while True:
            if self.item + 1 > len(self.collection):
                try:
                    self._request_next_page()
                except SWAPIClientError:
                    raise StopIteration()
            element = self.collection[self.item]
            self.item += 1
            return element
            
    next = __next__            
        
        
    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        if not self.counter:
             self._request_next_page()
        return self.counter


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
