import csv
import re
import pickle
from sklearn.ensemble import VotingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score

# Load the CSV file
def load_data(csv_file):
    urls = []
    labels = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            urls.append(row['URL'])
            labels.append(row['Label'])
    return urls, labels

# Preprocess the URLs
def preprocess_urls(urls):
    # Remove non-alphanumeric characters
    processed_urls = [re.sub(r'[^a-zA-Z0-9]', '', url) for url in urls]
    return processed_urls

# Extract features from URLs using a vectorizer
def extract_features(urls, vectorizer):
    features = vectorizer.transform(urls)
    return features

# Train the ensemble of classifiers
def train_classifiers(features, labels):
    classifier1 = DecisionTreeClassifier()
    classifier2 = RandomForestClassifier(n_estimators=100, random_state=42)
    classifier3 = KNeighborsClassifier(n_neighbors=5)
    
    ensemble = VotingClassifier(
        estimators=[('dt', classifier1), ('rf', classifier2), ('knn', classifier3)],
        voting='hard'
    )
    
    ensemble.fit(features, labels)
    return ensemble

# Predict labels for new URLs
def predict_labels(classifier, new_urls, vectorizer):
    processed_urls = preprocess_urls(new_urls)
    new_features = extract_features(processed_urls, vectorizer)
    predicted_labels = classifier.predict(new_features)
    return predicted_labels

# Main code
def main():
    # Load data from CSV file
    training_csv_file = 'malware.csv'
    urls, labels = load_data(training_csv_file)
    
    # Preprocess URLs
    processed_urls = preprocess_urls(urls)
    
    # Initialize and fit the CountVectorizer
    vectorizer = CountVectorizer()
    features = vectorizer.fit_transform(processed_urls)
    
    # Train the ensemble of classifiers
    classifier = train_classifiers(features, labels)
    
    # Save the vectorizer and classifier
    with open('vectorizer.pkl', 'wb') as file:
        pickle.dump(vectorizer, file)
    with open('classifier.pkl', 'wb') as file:
        pickle.dump(classifier, file)
    
    # Load the vectorizer and classifier during prediction
    with open('vectorizer.pkl', 'rb') as file:
        vectorizer = pickle.load(file)
    with open('classifier.pkl', 'rb') as file:
        classifier = pickle.load(file)
    
    # Get the path of the testing CSV file from user input
    test_urls, test_labels = load_data('malware_test2.csv')
    
    # Predict labels for the test URLs
    predicted_labels = predict_labels(classifier, test_urls, vectorizer)
    
    # Calculate and print the accuracy of the model
    accuracy = accuracy_score(test_labels, predicted_labels)
    print(f"Accuracy: {accuracy*100:.2f}%")

if __name__ == '__main__':
    main()
