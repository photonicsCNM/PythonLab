class MyDB():
    
    np = __import__('numpy')
    os = __import__('os')
    base64 = __import__('base64')
    hashlib = __import__('hashlib')
    unicodedata = __import__('unicodedata')
    widgets = __import__('ipywidgets')
    interactive = widgets.interactive
    HBox = widgets.HBox
    
    def __init__(self, base_dir = '.'):
        self.base_dir = base_dir
        self.data = {}
        self.update()
        self.tags = []
        self.selected_tags = []
        self.selected_experiment = []
        #self.list_tags()
        self.spectrometers = self.np.load('.detectors.npz', mmap_mode='r')        
            
    def update(self):
        for root, directories, filenames in self.os.walk(self.base_dir):
            if '.debris' in root:
                pass
            else:
                for filename in filenames: 
                    if filename[-3:]=='npz' and filename not in self.data.keys() and filename != '.detectors.npz':
                        self.data[self.base64.b64encode(self.hashlib.md5(str.encode(filename)).digest()).decode("utf-8") ]=  self.os.path.join(root,filename)
                    else:
                        pass
                    
                    
    def normalize_caseless(self, text):
        if type(text) in [str]:
            return self.unicodedata.normalize("NFKD", text.casefold())

        elif type(text)==list:
            return [self.unicodedata.normalize("NFKD", textitem.casefold()) for textitem in text]
        else:
            raise TypeError('Wrong input type for conversion. Only string or list are allowed.')

      
            
    def list_experiments(self):        
        for id_ in self.data.keys():
            with self.np.load(self.data[id_], mmap_mode='r') as dataset:
                if 'tags' in dataset.keys():
                    self.tags.append(dataset['tags'][0])
                else:
                    pass
        self.tags = set(self.tags)
        self.tags = sorted(list(self.tags))        
                
        def select(tag):
            self.selected_experiment = (tag)
            self.readouts = MyQuery(self, self.selected_experiment)
            #selected.children[0].options = self.selected_experiment[::-1]
                
        options=self.tags+['']
        selector = self.widgets.Dropdown(
            options=options,
            value= options[-1],
#             rows=7,
            description='choose tag:',
            disabled=False
        )
        return self.interactive(select, tag=selector)
    
    
        
    def list_tags(self):
        
        for id_ in self.data.keys():
            with self.np.load(self.data[id_], mmap_mode='r') as dataset:
                if 'tags' in dataset.keys():
                    for tag in dataset['tags']:
                        self.tags.append(tag)
                else:
                    pass
        self.tags = set(self.tags)
        self.tags = sorted(list(self.tags))        
        
        selected = self.interact_tags()
        
        def select(tag):            
            if tag in self.selected_tags:
                pass
            else:
                self.selected_tags.append(tag)
                selected.children[0].options = self.selected_tags[::-1]
                
        options=self.tags+['']
        selector = self.widgets.Dropdown(
            options=options,
            value= options[-1],
#             rows=10,
            description='add tags for Query:',
            disabled=False
        )
        return self.widgets.HBox([self.interactive(select, tag=selector), selected], description=('left', 'right'))
  

    def interact_tags(self):
        
        def uncheck_tag(tag): 
            if tag =='':
                pass
            else:
                self.selected_tags.remove(tag) 
                selected.children[0].options=self.selected_tags[::-1]
        
        options = self.selected_tags+['']
        selector = self.widgets.Dropdown(
            options=options,
            value= options[-1],
#             rows=5,
            description='remove tags from Query:',
            disabled=False
        ) 
        selected = self.interactive(uncheck_tag, tag = selector)
        return selected

class MyQuery():
    
    np = __import__('numpy')
    
    def __init__(self, database, *keywords, key='tags'):
        self.database = database
        selected = self.database.selected_tags
        if '' in selected:
            selected.remove('')
        self.keywords = keywords +tuple(selected)
        self.key = key
        self.result = self.query(*self.keywords, key=self.key)
        self.t0 = None
        
    def query(self, *keywords, key='tags'):
        query = []
        for id_ in self.database.data.keys():
            with self.np.load(self.database.data[id_], mmap_mode='r') as dataset:
                if key in dataset.keys():
                    is_there = []
                    for arg in keywords: 
                        if self.np.ndim(dataset[key])==0:
                            if arg in dataset[key]:
                                is_there.append(True)
                        else:
                            for tag in dataset[key]:
                                if arg in tag:
                                    is_there.append(True)
                    if len(is_there)==len(keywords):
                        query.append(self.database.data[id_])  
        if len(query)==1:
            query = query[0]

        return query
    
    def print_tags(self):
        if self.result==[]:
            print('No matches found.')
        else:
            for npz in self.result:
                with self.np.load(npz, mmap_mode='r') as item:
                    print(item['tags'])

    def print_keys(self):
        if self.result==[]:
            print('No matches found.')
        else:
            for npz in self.result:
                with self.np.load(npz, mmap_mode='r') as item:
                    print(item.keys())

    def select(self, *keywords):
        filtered_query = []
        for npz in self.result:
            with self.np.load(npz, mmap_mode='r') as result:
                is_there=[]
                for arg in keywords:
                    for key in result.keys():
                        if arg in result[key]:
                            is_there.append(True)
                if len(is_there)==len(keywords):
                        filtered_query.append(npz)  
        if len(filtered_query)==1:
            filtered_query = filtered_query[0]
        return filtered_query
    
    
    def sort(self, key, index = None, result = None, getter_func=None):
        if not result:
            result=self.result
            
        test = []
        for npz in result:
            with self.np.load(npz, mmap_mode='r') as item:
                try:            
                    item[key]
                    test.append(npz)
                except KeyError:
                    pass
        result = test  
        
        def getKey(npz):
            if getter_func and not index:
                with self.np.load(npz, mmap_mode='r') as item:
                    return getter_func(item[key])
            elif index and not getter_func:                
                with self.np.load(npz, mmap_mode='r') as item:
                    return item[key][index]
            elif index and getter_func:
                with self.np.load(npz, mmap_mode='r') as item:
                    return getter_func(item[key][index])
            else:
                with self.np.load(npz, mmap_mode='r') as item:
                    return item[key]
            
        query = sorted(result, key=getKey)
        self.result = query