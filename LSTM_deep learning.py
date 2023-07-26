import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score

# Load the dataset
df = pd.read_csv('malware_detection(100000 urls).csv')

# Preprocessing
le = LabelEncoder()
df['encoded_label'] = le.fit_transform(df['Label'])

# Tokenization and padding
tokenizer = Tokenizer()
tokenizer.fit_on_texts(df['URL'])
sequences = tokenizer.texts_to_sequences(df['URL'])
max_sequence_length = max([len(seq) for seq in sequences])
vocab_size = len(tokenizer.word_index) + 1
x = pad_sequences(sequences, maxlen=max_sequence_length)

# Train-test split
x_train, x_test, y_train, y_test = train_test_split(x, df['encoded_label'], test_size=0.2, random_state=42)

# Define the model
embedding_dim = 100
model = Sequential()
model.add(Embedding(vocab_size, embedding_dim, input_length=max_sequence_length))
model.add(LSTM(units=64))
model.add(Dense(len(le.classes_), activation='softmax'))

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(x_train, y_train, batch_size=32, epochs=10, validation_split=0.2)

# Evaluate the model
y_pred_prob = model.predict(x_test)
y_pred = np.argmax(y_pred_prob, axis=1)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
confusion_mat = confusion_matrix(y_test, y_pred)

# Print the results
print('Test Accuracy: {:.2f}%'.format(accuracy * 100))
print('Classification Report:')
print(report)
print('Confusion Matrix:')
print(confusion_mat)