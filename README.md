# MalQR

Jack Cavar - 2000314 - Machine learning Malicious QR code scanner

This is an extremely cut content version of code used to create the entire machine learning process behind the malicious QR code scanning project V1 for my dissertation at Abertay University. As such the files will show the overall code used to execute the project but cannot run successfully on device.

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

Folder "featureCounts" contains:

	- averageFeatures.py - gets the averages for each features in the dataset

	- averageMetrics.csv - the output of "averageFeatures.py"

	- getFeatureCounts.py - gets the number of features from each of the dataset individually

	- featureMetrics.csv - the output of "getFeatureCounts.py"

	
Folder "collectData" contains:

	- benign_grab.py - processes benign websites contained in Alexa top 1 million

	- PS_mal_grab.py - processes malicious websites contained from the PhishStats database
 

Folder "collectData/grabMal" contains:

	- malGrab.py - python scrapy spider for processing malicious websites contained in the PhishTank database.

	- Additional python scrapy files for runtime.

training and validation features and models have been removed from this repository to allow for newcomers to attempt on their own.

Folder "malqrdetect-Android" contains all main code files relating to the QR code scanning Android application created. 

The "malqrdetect-Android" folder contains the main following files: 

	- "Scan.kt" and "BarCodeAnalyse.kt" - Responsible for the logic behind discovering a QR code and displaying the scanning page

	- "EmbedAnalyse.kt" - Responsible for the logic in collecting the features from the embedded code, initialising the machine learning model to make a prediction and displaying all feature elements of the application.

	- "chaqFeatureExtract.py" - Responsible for containing all the python code pertaining to request and feature extraction. Called within "EmbedAnalyse.kt".

	- Additional files for python runtime.
