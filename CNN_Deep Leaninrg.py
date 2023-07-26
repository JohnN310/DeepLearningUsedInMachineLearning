import re
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import plotly.graph_objects as go
from colorama import Fore
from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, ExtraTreesClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import GaussianNB
from tld import get_tld, is_tld
from tld.exceptions import TldDomainNotFound, TldBadUrl, TldIOError
import whois
from datetime import datetime
from plotly.subplots import make_subplots
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
import nltk
import tldextract
import hashlib
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis, QuadraticDiscriminantAnalysis
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, AdaBoostClassifier, ExtraTreesClassifier, BaggingClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.neural_network import MLPClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.linear_model import RidgeClassifier, Perceptron, SGDClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers

urls_data = pd.read_csv('malware_detection(100000 urls).csv')
urls_data.head()
urls_data["url_type"] = urls_data["Label"].replace({
    'benign':0,
    'defacement':1,
    'phishing':2,
    'malware':3
})
# display the csv file's content
def get_url_length(url):
    return len(url)

count = urls_data['Label'].value_counts()

# Define a color scale for the bars
colors = [
    '#288BA8', '#7468B0', '#FF33FF', '#FFFF99', '#00B3E6',
    '#E83845', '#3366E6', '#999966', '#E389B9', '#B34D4D'
]
fig = go.Figure(data=[go.Bar(x=count.index, y=count, marker=dict(color=colors))])

# Update layout
fig.update_layout(
    xaxis_title='Types',
    yaxis_title='Count',
    title='Count of Different Types of URLs',
    plot_bgcolor='rgba(0, 0, 0, 0)',  # Set plot background color to transparent
    paper_bgcolor='rgba(0, 0, 0, 0)',  # Set paper background color to transparent
    font=dict(color='white')  # Set font color to white
)

# Update x-axis tick font color
fig.update_xaxes(tickfont=dict(color='white'))

# Update y-axis tick font color
fig.update_yaxes(tickfont=dict(color='white'))

fig.show()


urls_data['url_len'] = urls_data['URL'].apply(lambda x: get_url_length(str(x)))

def extract_pri_domain(url):
    try:
        res = get_tld(url, as_object=True, fix_protocol=True)
        pri_domain = res.parsed_url.netloc
    except:
        pri_domain = None
    return pri_domain

urls_data['pri_domain'] = urls_data['URL'].apply(lambda x: extract_pri_domain(x))

def count_letters(url):
    num_letters = sum(char.isalpha() for char in url)
    return num_letters

def count_digits(url):
    num_digits = sum(char.isdigit() for char in url)
    return num_digits

def count_special_chars(url):
    special_chars = "!@#$%^&*()_+-=[]{};:,.<>/?`~|"
    num_special_chars = sum(char in special_chars for char in url)
    return num_special_chars

urls_data['letters_count'] = urls_data['URL'].apply(lambda x: count_letters(x))
urls_data['digits_count'] = urls_data['URL'].apply(lambda x: count_digits(x))
urls_data['special_chars_count'] = urls_data['URL'].apply(lambda x: count_special_chars(x))

def has_shortening_service(url):
    pattern = re.compile(r'bit\.ly|goo\.gl|shorte\.st|go2l\.ink|x\.co|ow\.ly|t\.co|tinyurl|tr\.im|is\.gd|cli\.gs|'
                         r'yfrog\.com|migre\.me|ff\.im|tiny\.cc|url4\.eu|twit\.ac|su\.pr|twurl\.nl|snipurl\.com|'
                         r'short\.to|BudURL\.com|ping\.fm|post\.ly|Just\.as|bkite\.com|snipr\.com|fic\.kr|loopt\.us|'
                         r'doiop\.com|short\.ie|kl\.am|wp\.me|rubyurl\.com|om\.ly|to\.ly|bit\.do|t\.co|lnkd\.in|'
                         r'db\.tt|qr\.ae|adf\.ly|goo\.gl|bitly\.com|cur\.lv|tinyurl\.com|ow\.ly|bit\.ly|ity\.im|'
                         r'q\.gs|is\.gd|po\.st|bc\.vc|twitthis\.com|u\.to|j\.mp|buzurl\.com|cutt\.us|u\.bb|yourls\.org|'
                         r'x\.co|prettylinkpro\.com|scrnch\.me|filoops\.info|vzturl\.com|qr\.net|1url\.com|tweez\.me|v\.gd|'
                         r'tr\.im|link\.zip\.net')
    match = pattern.search(url)
    return int(bool(match))

urls_data['shortened'] = urls_data['URL'].apply(lambda x: has_shortening_service(x))

def abnormal_url(url):
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    if hostname:
        hostname = str(hostname)
        match = re.search(hostname, url)
        if match:
            return 1
    return 0

urls_data['abnormal_url'] = urls_data['URL'].apply(lambda x: abnormal_url(x))

def secure_http(url):
    scheme = urlparse(url).scheme
    if scheme == 'https':
        return 1
    else:
        return 0

urls_data['secure_http'] = urls_data['URL'].apply(lambda x: secure_http(x))

def have_ip_address(url):
    pattern = r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.' \
              r'([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\/)|' \
              r'(([01]?\d\d?|2[0-4]\d|25[0-5])\.([01]?\d\d?|2[0-4]\d|25[0-5])\.' \
              r'([01]?\d\d?|2[0-4]\d|25[0-5])\.' \
              r'([01]?\d\d?|2[0-4]\d|25[0-5])\/)|' \
              r'((0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\.(0x[0-9a-fA-F]{1,2})\/)' \
              r'(?:[a-fA-F0-9]{1,4}:){7}[a-fA-F0-9]{1,4}|' \
              r'([0-9]+(?:\.[0-9]+){3}:[0-9]+)|' \
              r'((?:(?:\d|[01]?\d\d|2[0-4]\d|25[0-5])\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d|\d)(?:\/\d{1,2})?)'

    match = re.search(pattern, url)
    if match:
        return 1
    else:
        return 0

urls_data['have_ip'] = urls_data['URL'].apply(lambda x: have_ip_address(x))

fig = make_subplots(rows=1, cols=1)

fig.add_trace(go.Histogram(x=urls_data['url_len'], nbinsx=100))

fig.update_layout(
    title='Distribution of URL Lengths',
    xaxis_title='URL Length',
    yaxis_title='Count',
    font=dict(color='gray')
)

fig.show()

def extract_root_domain(url):
    extracted = tldextract.extract(url)
    root_domain = extracted.domain
    return root_domain

urls_data['root_domain'] = urls_data['pri_domain'].apply(lambda x: extract_root_domain(str(x)))
data = urls_data.drop(columns=['URL','Label','pri_domain'])

print(data['root_domain'].value_counts())

data['root_domain'].value_counts()
data = data[data['root_domain'] != '0']
def hash_encode(category):
    hash_object = hashlib.md5(category.encode())
    return int(hash_object.hexdigest(), 16) % (10 ** 8)
data['root_domain'] = data['root_domain'].apply(hash_encode)

#Evaluate the model's performance
x = urls_data['URL']
y = urls_data['url_type']
x_train,x_test,y_train,y_test = train_test_split(x,y,test_size=0.1, random_state=42)

# Tokenize the URLs
tokenizer = tf.keras.preprocessing.text.Tokenizer()
tokenizer.fit_on_texts(x_train)

x_train = tokenizer.texts_to_sequences(x_train)
x_test = tokenizer.texts_to_sequences(x_test)

vocab_size = len(tokenizer.word_index) + 1
max_length = max(len(url) for url in x_train)

x_train = tf.keras.preprocessing.sequence.pad_sequences(x_train, maxlen=max_length, padding='post')
x_test = tf.keras.preprocessing.sequence.pad_sequences(x_test, maxlen=max_length, padding='post')

# Build the CNN model
model = tf.keras.Sequential()
model.add(layers.Embedding(vocab_size, 100, input_length=max_length))
model.add(layers.Conv1D(64, 3, activation='relu'))
model.add(layers.GlobalMaxPooling1D())
model.add(layers.Dense(10, activation='relu'))
model.add(layers.Dense(4, activation='softmax'))

model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the CNN model
model.fit(x_train, y_train, epochs=10, batch_size=32, validation_data=(x_test, y_test))

# Evaluate the CNN model
y_pred_probs = model.predict(x_test)
y_pred = np.argmax(y_pred_probs, axis=1)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
confusion_mat = confusion_matrix(y_test, y_pred)

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