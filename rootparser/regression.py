from sklearn import datasets, svm, metrics
import numpy as np

def sklearn_sample():
    #These objects are like dictionaries; .data holds data and .target holds classification metadata
    digits = datasets.load_digits()

    print digits.data   #flattened lst of pixel arrays for 0-9
                        # shaped (n_samples, n_features)
    print digits.target #array with the class label for col(data)

    #list of [ (image_1, label_1), (image_2, label_2) ...]
    data_and_labels = list(zip(digits.images, digits.target))

    #if necessary, flatten the arrays
    n_samples = len(digits.images)
    data = digits.images.reshape((n_samples, -1))

    classifier = svm.SVC(gamma=.001)

    #train the fit:
    N_fit = n_samples /2
    classifier.fit(data[:N_fit], digits.target[:N_fit])

    #make predictions on what happens in the remaining samples:
    expected = digits.target[N_fit:]
    predicted = classifier.predict(data[N_fit:])

def train_and_predict(data, target, N_fit=None):
    #Given an array of event parameter arrays and bool labels for whether
    #the kineNeutron was a successful predictor, train and test a
    #classifier for events


    #Verify that the classification
    if len(data_array) != len(target_array):
        raise ValueError("data and classifier arrays do not match in dim")

    #N_fit is how many samples we fit on; the remaining we use for testing
    N_samples = len(data_array)
    if N_fit == None:
        N_fit = N_samples / 2

    #TODO:
    #birth and train the classifier
    classifier = svm.SVC(gamma=.001)
    classifier.fit(data[:N_fit], target[:N_fit])

    expected = target[N_fit:]
    predicted = classifier.predict(data[N_fit:])

    #TODO: How do we check the results of our classification?

def main():
    structured = np.array([
                    (1, 2., np.arange(4)),
                    (2, 5., np.arange(4)),
                    (3, 1., np.array([2,3,4,5]))
                    ],
    dtype=[('evt', 'int8'), ('E', 'float32'), ('P', '4float32')])

    x = structured
    print x.view((float, len(x.dtype.names)))
    arr2 = structured.reshape(len(structured), -1)

    print "original: \n", structured
    print "reshaped to len %i \n" % len(structured), arr2

if __name__ == "__main__":
    main()
