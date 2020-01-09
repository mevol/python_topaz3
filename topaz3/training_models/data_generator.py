import numpy as np
import keras
import mrcfile

class DataGenerator(keras.utils.Sequence):
    'Generates data for Keras'
    def __init__(self, list_IDs, labels, batch_size=32, dim=(32,32,32),
                 n_classes=2, n_channels=1, shuffle=True):
#    def __init__(self, data, batch_size=32, dim=(32,32,32),
#                 n_classes=2, n_channels=1, shuffle=True):

        'Initialization'
        self.dim = dim
        self.batch_size = batch_size
        #self.data = data
        #print(self.data.keys())
        
        self.labels = labels
#        print(333, self.labels.keys())
        self.list_IDs = list_IDs
#        print(444, self.list_IDs.keys())
        self.n_channels = n_channels
        self.n_classes = n_classes
        self.shuffle = shuffle
        self.on_epoch_end()

    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(len(self.list_IDs.keys()) / self.batch_size))
#        return int(np.floor(len(self.data["Files"]) / self.batch_size))

    def __getitem__(self, index):
        'Generate one batch of data'
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
#        print(888, indexes)

        # Find list of IDs
        list_IDs_temp = [self.list_IDs[k] for k in indexes]
        list_labels_temp = [self.labels[k] for k in indexes]
#        list_IDs_temp = [self.data["Files"]()[k] for k in indexes]
        
#        print(666, list_IDs_temp)
#        print(222, list_labels_temp)

        # Generate data
        X, y = self.__data_generation(list_IDs_temp, list_labels_temp)

        return X, y

    def on_epoch_end(self):
        'Updates indexes after each epoch'
        self.indexes = np.arange(len(self.list_IDs))
        #self.indexes = np.arange(len(self.data["Files"]))

        if self.shuffle == True:
            np.random.shuffle(self.indexes)

    def __data_generation(self, list_IDs_temp, list_labels_temp):
        'Generates data containing batch_size samples' # X : (n_samples, *dim, n_channels)
        # Initialization
        X = np.empty([self.batch_size, *self.dim])
        y = np.empty([self.batch_size], dtype=int)

        # Generate data
        for i, ID in enumerate(list_IDs_temp):
            print(777, ID)
#            print(111, i)
            with mrcfile.open(ID) as mrc:
                volume = mrc.data
                print(volume.shape)   
        
            # Store sample
            X[i,] = volume

        for i, ID in enumerate(list_labels_temp):
            # Store class
            #Y[i,] = keras.utils.to_categorical(img_Y, num_classes=self.n_classes)
#            print(999, ID)
#            print(000, i)

            y[i] = ID
            
            
            print("class label", y[i])
        X = X.reshape(self.batch_size, *self.dim, self.n_channels)
        print(X.shape)
        
        return X, keras.utils.to_categorical(y, num_classes=self.n_classes)


