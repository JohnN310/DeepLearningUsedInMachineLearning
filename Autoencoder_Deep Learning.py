import re
import numpy as np
import pandas as pd
import tldextract
import hashlib
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import EarlyStopping

# Load the dataset
urls_data = pd.read_csv('malicious_phish.csv')
urls_data["url_type"] = LabelEncoder().fit_transform(urls_data["Label"])

# Preprocessing
def preprocess_data(data):
    data['url_len'] = data['URL'].apply(lambda x: len(str(x)))
    data['root_domain'] = data['URL'].apply(lambda x: extract_root_domain(str(x)))
    data = data[data['root_domain'] != '0']
    data['root_domain'] = data['root_domain'].apply(hash_encode)
    return data

def extract_root_domain(url):
    extracted = tldextract.extract(url)
    root_domain = extracted.domain
    return root_domain

def hash_encode(category):
    hash_object = hashlib.md5(category.encode())
    return int(hash_object.hexdigest(), 16) % (10 ** 8)
# Function to extract the primary domain from URLs
def extract_pri_domain(url):
    try:
        res = get_tld(url, as_object=True, fix_protocol=True)
        pri_domain = res.parsed_url.netloc
    except:
        pri_domain = None
    return pri_domain

# Add 'pri_domain' column to the dataset
urls_data['pri_domain'] = urls_data['URL'].apply(lambda x: extract_pri_domain(x))
urls_data = preprocess_data(urls_data)
data = urls_data.drop(columns=['URL','Label','pri_domain'])
x = data.drop(columns=['url_type'])
y = data['url_type']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.5, random_state=42)

# Autoencoder Model
model = Sequential()
model.add(Dense(32, input_shape=(x_train.shape[1],), activation='relu'))
model.add(Dense(16, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(x_train.shape[1], activation='linear'))
model.compile(optimizer='adam', loss='mean_squared_error')

# Training
early_stopping = EarlyStopping(monitor='val_loss', patience=3)
model.fit(x_train, x_train, epochs=10, batch_size=32, validation_split=0.2, callbacks=[early_stopping])

# Reconstruction error calculation
x_train_pred = model.predict(x_train)
train_mse = np.mean(np.power(x_train_pred - x_train, 2), axis=1)
threshold = np.mean(train_mse) + np.std(train_mse)

# Testing
x_test_pred = model.predict(x_test)
test_mse = np.mean(np.power(x_test_pred - x_test, 2), axis=1)
y_pred = (test_mse > threshold).astype(int)

# Evaluation
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred, output_dict=True)
f1_score = report['macro avg']['f1-score']
precision = report['macro avg']['precision']
recall = report['macro avg']['recall']

print('Test Accuracy: {:.2f}%'.format(accuracy * 100))
print('F1-Score: {:.2f}'.format(f1_score))
print('Precision: {:.2f}'.format(precision))
print('Recall: {:.2f}'.format(recall))
print('\nClassification Report:')
print(classification_report(y_test, y_pred))
print('\nConfusion Matrix:')
cf_matrix = confusion_matrix(y_test, y_pred)
print(cf_matrix)