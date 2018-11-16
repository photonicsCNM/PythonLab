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
                for arg in keywords:
                    is_there=[]
                    for key in result.keys():
                        if arg in result[key]:
                            is_there.append(True)
                if len(is_there)==len(keywords):
                        filtered_query.append(result)  
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
            if getter_func:
                with self.np.load(npz, mmap_mode='r') as item:
                    return getter_func(item[key])
            elif index:
                
                with self.np.load(npz, mmap_mode='r') as item:
                    return item[key][index]
            else:
                with self.np.load(npz, mmap_mode='r') as item:
                    return item[key]
            
        query = sorted(result, key=getKey)
        self.result = query