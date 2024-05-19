import argparse
import sys
import os
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA  # Import PCA
from sklearn.pipeline import Pipeline
from joblib import dump, load

# Defines a function for training the model.
def run_train(public_dir, model_dir):
    # Ensures the model directory exists, creates it if it doesn't.
    os.makedirs(model_dir, exist_ok=True)

    # Constructs the path to the training data file.
    train_file = os.path.join(public_dir, 'train.npz')

    # Loads the training data from the .npz file.
    train_data = np.load(train_file)

    # Extracts the features from the training data.
    X_train = train_data['X_train'][:]

    # Extracts the labels from the training data.
    y_train = train_data['y_train'][:]

    # Initialize PCA with desired number of components
    pca = PCA(n_components=0.69)  # You can adjust the number of components

    # Fit PCA to the training data and transform it
    X_train_transformed = pca.fit_transform(X_train)

    # # Instantiates the KNN classifier model.
    # model = Pipeline(steps=[('scaler', None), ('decomposition', PCA(n_components=0.73)),
    #             ('another_decomposition', 'passthrough'),
    #             ('feature_selection', None),
    #             ('estimator',
    #              KNeighborsClassifier(metric='euclidean', n_neighbors=10,
    #                                   weights='distance'))])

    model = KNeighborsClassifier(metric='euclidean', n_neighbors=9, weights='distance')
    # Fits the model to the transformed training data.
    model.fit(X_train_transformed, y_train)

    # Defines the path for saving the trained model.
    model_path = os.path.join(model_dir, 'trained_model.joblib')

    # Saves the trained model to the specified path.
    dump((model, pca), model_path)  # Save both the model and PCA object

# Defines a function for making predictions.
def run_predict(model_dir, public_dir, output_path):
    # Specifies the path to the trained model.
    model_path = os.path.join(model_dir, 'trained_model.joblib')

    # Loads the trained model and PCA object from file.
    model, pca = load(model_path)

    # Constructs the path to the test data file.
    test_file = os.path.join(public_dir, 'test.npz')

    # Loads the test data from the .npz file.
    test_data = np.load(test_file)

    # Extracts the features from the test data.
    X_test = test_data['X_test']

    # Transform the test data using the learned PCA transformation
    X_test_transformed = pca.transform(X_test)

    # Predicts and saves results.
    pd.DataFrame({'y': model.predict(X_test_transformed)}).to_json(output_path, orient='records', lines=True)


# Defines the main function that parses commands and arguments.
def main():
    # Initializes a parser for command-line arguments.
    parser = argparse.ArgumentParser()

    # Creates subparsers for different commands.
    subparsers = parser.add_subparsers(dest='command')

    # Adds a subparser for the 'train' command.
    parser_train = subparsers.add_parser('train')

    # Adds an argument for the directory containing public data.
    parser_train.add_argument('--public_dir', type=str)

    # Adds an argument for the directory to save the model.
    parser_train.add_argument('--model_dir', type=str)

    # Adds a subparser for the 'predict' command.
    parser_predict = subparsers.add_parser('predict')

    # Adds an argument for the directory containing the model.
    parser_predict.add_argument('--model_dir', type=str)

    # Adds an argument for the directory containing public data.
    parser_predict.add_argument('--public_dir', type=str)

    # Adds an argument for the path to save prediction results.
    parser_predict.add_argument('--output_path', type=str)

    # Parses the command-line arguments.
    args = parser.parse_args()

    if args.command == 'train':
        # Checks if the 'train' command was given.
        # Calls the function to train the model.
        run_train(args.public_dir, args.model_dir)
    elif args.command == 'predict':
        # Checks if the 'predict' command was given.
        # Calls the function to make predictions.
        run_predict(args.model_dir, args.public_dir, args.output_path)
    else:
        # If no valid command was given, prints the help message.
        # Displays help message for the CLI.
        parser.print_help()

        # Exits the script with a status code indicating an error.
        sys.exit(1)


# Checks if the script is being run as the main program.
if __name__ == "__main__":
    # Calls the main function if the script is executed directly.
    main()
