class Measurement():
    np = __import__('numpy')
    def __init__(self,id_, path, metadata=None):
        self.id_ = id_
        self.path = path
        if metadata:
            self.metadata = metadata
        else:
            with self.np.load(path, mmap_mode='r') as readout:
                self.metadata = {'IT':readout['IT'].item(),
                                 'N':readout['N'].item(),
                                 'detector':readout['detector'].item(),
                                 'experiment': readout['tags'][0].item(),
                                 'sensor': readout['tags'][1].item(),
                                 'timestamp': readout['tags'][2].item()}
                if len(readout['tags']) == 4:
                    self.metadata['concentration'] = readout['tags'][-1].item()
    def __repr__(self):
        return "<Measurement(%s, timestamp='%s')>"%(self.metadata['experiment'],
                                                   self.metadata['timestamp'])
    def get_data(self):
        with self.np.load(self.path, mmap_mode='r') as readout:
            return readout['intensities']

class MyDB():

    np = __import__('numpy')
    os = __import__('os')
    json = __import__('json')
    threading = __import__('threading')
    time = __import__('time')
    # base64 = __import__('base64')
    # hashlib = __import__('hashlib')
    unicodedata = __import__('unicodedata')
    # widgets = __import__('ipywidgets')
    # interactive = widgets.interactive
    # HBox = widgets.HBox

    def __init__(self, base_dir = '.'):
        self.base_dir = base_dir
        self.data = {}
        self.id_counter = 0
        self.new_files = None
        self.tags = []
        self.selected_tags = []
        self.selected_experiment = []
        #self.list_tags()
        self.spectrometers = self.np.load(base_dir+'/detectors.npz',
                                            mmap_mode='r')
        try:
            with open(self.os.path.join(self.base_dir,'.metadata.db'),'r') as file:
                data = self.json.load(file)
                for id_ in data:
                    self.data[id_] = Measurement(id_, data[id_]['path'],
                                                    data[id_]['metadata'])
                self.id_counter=int(max([id_ for id_ in data]))
        except FileNotFoundError:
            self.scan()
            self.save_metadata()
        self.UpdateClient = self.threading.Thread(target=self.update)
        self.UpdateClient.stop = False
        self.UpdateClient.start()

    def scan(self):
        added_paths = [m.path for m in self.data.values()]
        files_added = False
        for root, directories, filenames in self.os.walk(self.base_dir):
            if '.debris' in root:
                pass
            else:
                for filename in filenames:
                    path = self.os.path.join(root,filename)
                    if filename=='detectors.npz' or filename=='.detectors.npz':
                        pass
                    elif filename=='params.npz':
                        pass
                    elif filename[-3:]=='npz' and path not in added_paths:
                        id_ = str(self.id_counter + 1)
                        self.data[id_] = Measurement(id_, path)
                        self.id_counter += 1
                        files_added = True
                    else:
                        pass
        return files_added

    def save_metadata(self):
        with open(self.os.path.join(self.base_dir,'.metadata.db'),'w') as file:
            data = {}
            for measurement in self.data.values():
                data[measurement.id_] = {'path':measurement.path,
                                        'metadata':measurement.metadata}
            self.json.dump(data, file, indent=4)

    def update(self):
        while not getattr(self.UpdateClient, "stop", False):

            self.new_files = self.scan()
            if self.new_files:
                self.save_metadata()
            else:
                pass
            self.time.sleep(10)


    def normalize_caseless(self, text):
        if type(text) in [str]:
            return self.unicodedata.normalize("NFKD", text.casefold())
        elif type(text)==list:
            return [self.unicodedata.normalize("NFKD", textitem.casefold()) for textitem in text]
        else:
            try:
                text = str(text)
                return self.unicodedata.normalize("NFKD", text.casefold())
            except:
                msg = 'in conversion of ' + str(type(text)) + '\n'
                msg  = msg + 'Wrong input type for conversion.\n'
                msg = msg+ 'Only string or list are allowed.'
                raise TypeError(msg)

    def query(self, *keywords):
        query = []

        for id_ in self.data:
            is_there = []
            for arg in keywords:
                for entry in self.data[id_].metadata:
                    if self.normalize_caseless(arg) in self.normalize_caseless(
                            self.data[id_].metadata[entry]):
                        is_there.append(True)
            if len(is_there)==len(keywords):
                query.append(self.data[id_])
        if len(query)==1:
            return query[0]
        else:
            return query


    def sort(self, query, key, getter_func=None):
        def getKey(item):
            if getter_func:
                return getter_func(item.metadata[key])
            else:
                return item.metadata[key]

        query = sorted(query, key=getKey)
        return query


    def list_experiments(self, sensors = ['biofilm', 'ref'], interactive=False):

        self.tags = set([self.data[id_].metadata['experiment'] for id_ in self.data.keys()])
        self.tags = sorted(list(self.tags))

        if interactive:
            def select(tag):
                self.selected_experiment = (tag)
                self.readouts = {sensor: MyQuery(self, self.selected_experiment, sensor) for sensor in sensors}
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
        else:
            return self.tags


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
