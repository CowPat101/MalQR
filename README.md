# MalQR

Jack Cavar - 2000314 - Malicious QR code scanner

Files may not run correctly without their correct pathing and necessary files. All files should be added here but some might be missing ooops!

To understand the full context behind the QR code website safety process, view the site here: https://www.jackqr.net/

NOTE: Any "V3" in files refers to the 3rd iteration of feature extraction gathering process. "V7" and "V8" both reference the final feature build algorithms for creating and testing the models which were used within the dissertation.

Raw dataset - Custom dataset used to train each machine learning model. Contains the individual html files and csv file which links a URL to a html file. Too big to be included locally. Can be downloaded here: https://www.kaggle.com/datasets/jackcavar/malicious-and-benign-website-dataset/data

Folder "python files" contains:

	- extractFeatures.py - feature extraction for creating the training and validation files from the dataset

	- model_testv7.py - testing the model accuracy against unseen data for a single model on the first training method

	- model_testv7v3.py - testing the model accuracy against unseen data for each model algorithm on the first training method

	- model_testv8.py - testing the model accuracy against unseen data for a single model on the second training method

	- model_testv8v3.py - testing the model accuracy against unseen data for each model algorithm on the second training method

	- light_convert.py - to convert the model to the correct format for android app usage

	- train_method_one contains a folder for each of the strongest model off of their hyperparameters trained in the format of Rates, URL, TF-IDF. This contains LightGBM, Decision Tree, K-Nearest-Neighbours, Naive Bayes, Random Forest and XGBoost. Each folder contains:

		- SingleTrain<Name of algorithm>.py - to train the model type with different hyperparameters

		- accuracies.txt - Accuracy, Precision, Recall and F1-Score for the model
		
		- confusionMatrix.png(txt) - confusion matrix for the model in both a text and visual format
	
		- bestParams.txt - The hyperparameters used to make the best performing model of its class
		
		- copy of the machine learning model with the highest scores.

		Additionally, LightGBM contains a feature_importances.csv file for collecting the best features from the model made (which was found to be LightGBM) as well as the ROC curve output.

	- train_method_two contains the same as "train_method_one" but with models trained in the format of URL, Rates, TF-IDF

	- Both train_method_<x> folders contain the externalTraining folder. This is data collected from model_testv(7/8)v3.py which shows how each model managed against 1000 random URLs. Within the folder is:

		- <model name>.txt - contains the scores from the model alongside the confusion matrix values

		- <model name> predictions.csv - shows each individual URL and what the model predicted the URL as.
		
		A visual confusion matrix would've been given, but the program corrupted their view so it was decided to remove from the submission numeric data should be enough however.


	Folder "featureCounts" contains:

		- averageFeatures.py - gets the averages for each features in the dataset

		- averageMetrics.csv - the output of "averageFeatures.py"

		- getFeatureCounts.py - gets the number of features from each of the dataset individually

		- featureMetrics.csv - the output of "getFeatureCounts.py"

	
	Folder "collectData" contains:

		- benign_grab.py - processes benign websites contained in Alexa top 1 million

		- PS_mal_grab.py - processes malicious websites contained from the PhishStats database

		Folder "grabMal" contains:

			- malGrab.py - python scrapy spider for processing malicious websites contained in the PhishTank database.

			- Additional python scrapy files for runtime.


training_featuresv(7/8).npz - processed training data for use in training a machine learning model. Loaded in most python programs included.

validation_featuresv(7/8).npz - processed validation data for use in validating a newly trained machine learning model. Loaded in most python programs included.

modelv9_float16.tflite - model created using the process from "light_convert.py" and then onnx2tf

Folder "Android" contains all files relating to the QR code scanning Android application created. Go to: "Android > app > src > main" to access all main files. Additionally, open the project up in Android studio for an easier viewing experience. 

	The "Android" folder contains the main following files: 

		- "Scan.kt" and "BarCodeAnalyse.kt" - Responsible for the logic behind discovering a QR code and displaying the scanning page

		- "EmbedAnalyse.kt" - Responsible for the logic in collecting the features from the embedded code, initialising the machine learning model to make a prediction and displaying all feature elements of the application.

		- "chaqFeatureExtract.py" - Responsible for containing all the python code pertaining to request and feature extraction. Called within "EmbedAnalyse.kt".

		- Additional files for python runtime.
