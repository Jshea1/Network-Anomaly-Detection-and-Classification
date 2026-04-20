# Network-Anomaly-Detection-and-Classification

This project aims to build a network anomaly detection and classification system using the UNSW-NB 15 dataset (https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15). The main idea is to analyze network traffic data to determine if the activity is normal or malicious. This dataset has labeled examples of different types of attacks and normal behavior, which makes it useful for applying pattern recognition methods.

A notable aspect of this dataset is its lower “Usability Score,” which Kaggle uses to rate a dataset’s functionality. The data includes multiple instances of missing records, features, and similar issues. While this would normally rule out a dataset, it will be a good demonstration of our ability to clean and otherwise deal with missing & noisy data. 

Our plan is to use Python libraries to preprocess the data, choose the most important features, and fill in missing elements. Then, we will apply a simple machine learning algorithm such as K-Nearest Neighbors or a Decision Tree to classify the traffic. To evaluate our system, we will use performance metrics such as accuracy, precision, and recall.

Overall, this project aims to show how pattern recognition can be applied to a real-world cybersecurity problem by building a simple and effective model for detecting network anomalies.
