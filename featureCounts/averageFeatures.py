#Program to take in the features from the featureMetrics file and create an average of the features fro each class for both malicious and benign
#import the necessary libraries
import pandas as pd
import os
import sys

benign = 0
malicious = 0


 # Initialize HTML feature rates for both malicious and benign
malRates = {
        "F1": 0,
        "F3": 0,
            "F4": 0,
            "F5": 0,
            "F6": 0,
            "F7": 0,
            "F8": 0,
            "F9": 0,
            "F10": 0,
            "F11": 0,
            "F12": 0,
            "F13": 0,
            "F14": 0,
            "F15": 0,
            "F16": 0,
            "F17": 0,
            "F18": 0,
            "F19": 0,
            "F20": 0,
            "F21": 0,
            "F22": 0,
            "F23": 0,
            "F24": 0,
            "F25": 0,
            "F26": 0,
            "F27": 0,
            "F28": 0,
            "F29": 0,
            "F30": 0,
            "F31": 0,
            "F32": 0,
            "F33": 0,
            "F34": 0,
            "F35": 0,
            "F36": 0,
            "F37": 0,
            "F38": 0,
            "F39": 0,
            "F40": 0,

            "F41": 0,
            "F42": 0,
            "F43": 0,
            "F44": 0,
            "F45": 0,
            "F46": 0,
            "F47": 0,
            "F48": 0,
            "F49": 0,
            "F50": 0,
            "F51": 0,
            "F52": 0,
            "F53": 0,
            "F54": 0,
            "F55": 0,
            "F56": 0}

benRates = {
        "F1": 0,
        "F3": 0,
            "F4": 0,
            "F5": 0,
            "F6": 0,
            "F7": 0,
            "F8": 0,
            "F9": 0,
            "F10": 0,
            "F11": 0,
            "F12": 0,
            "F13": 0,
            "F14": 0,
            "F15": 0,
            "F16": 0,
            "F17": 0,
            "F18": 0,
            "F19": 0,
            "F20": 0,
            "F21": 0,
            "F22": 0,
            "F23": 0,
            "F24": 0,
            "F25": 0,
            "F26": 0,
            "F27": 0,
            "F28": 0,
            "F29": 0,
            "F30": 0,
            "F31": 0,
            "F32": 0,
            "F33": 0,
            "F34": 0,
            "F35": 0,
            "F36": 0,
            "F37": 0,
            "F38": 0,
            "F39": 0,
            "F40": 0,
            "F41": 0,
            "F42": 0,
            "F43": 0,
            "F44": 0,
            "F45": 0,
            "F46": 0,
            "F47": 0,
            "F48": 0,
            "F49": 0,
            "F50": 0,
            "F51": 0,
            "F52": 0,
            "F53": 0,
            "F54": 0,
            "F55": 0,
            "F56": 0}

#Open the featureMetrics.csv and read the data

with open('featureMetrics.csv') as f:
    data = pd.read_csv(f)

    #print the column with the name type
    print(data['Type'])

    #Loop through the data and count the number of malicious and benign
    for index, row in data.iterrows():
        if row['Type'] == 1:
            malicious += 1

            #loop through every row['F value']
            for key in malRates:
                #print("Key: ", key)
                if key == "F1" or key == "F3" or key == "F4" or key == "F5" or key == "F6" or key == "F7" or key == "F8" or key == "F9" or key == "F10" or key == "F11" or key == "F12" or key == "F13" or key == "F14" or key == "F15" or key == "F19" or key == "F20" or key == "F21" or key == "F22" or key == "F23" or key == "F24" or key == "F25" or key == "F26" or key == "F27" or key == "F28" or key == "F29" or key == "F30" or key == "F31" or key == "F32" or key == "F33" or key == "F34" or key == "F35" or key == "F36" or key == "F38" or key == "F39" or key == "F44" or key == "F45" or key == "F47" or key == "F48" or key == "F49" or key == "F50" or key == "F55":
                    print("Malicious int: ", key)

                    #add the value of the key to the dictionary
                    malRates[key] += row[key]

                else:
                    #16,17,37,40,41,42,43,46,51,52,53,54,56 are the values on bool mode
                    print("Malicious Bool: ", key)

                    #check if the value on the column for the key is 1
                    if row[key] == 1:
                        malRates[key]+= 1
                    
                 
        else:
            
            for key in benRates:
                #print("Key: ", key)
                if key == "F1" or key == "F3" or key == "F4" or key == "F5" or key == "F6" or key == "F7" or key == "F8" or key == "F9" or key == "F10" or key == "F11" or key == "F12" or key == "F13" or key == "F14" or key == "F15" or key == "F19" or key == "F20" or key == "F21" or key == "F22" or key == "F23" or key == "F24" or key == "F25" or key == "F26" or key == "F27" or key == "F28" or key == "F29" or key == "F30" or key == "F31" or key == "F32" or key == "F33" or key == "F34" or key == "F35" or key == "F36" or key == "F38" or key == "F39" or key == "F44" or key == "F45" or key == "F47" or key == "F48" or key == "F49" or key == "F50" or key == "F55":
                    print("Benign int: ", key)

                    #add the value of the key to the dictionary
                    benRates[key] += row[key]

                else:
                    #16,17,37,40,41,42,43,46,51,52,53,54,56 are the values on bool mode
                    print("Benign Bool: ", key)

                    #check if the value on the column for the key is 1
                    if row[key] == 1:
                        benRates[key]+= 1

            benign += 1


print("Malicious: ", malicious)
print("Benign: ", benign)

import csv

#check if featureMetrics.csv exists, if so delete it
if os.path.exists('averageMetrics.csv'):
    os.remove('averageMetrics.csv')

#Check if averageMetrics.csv exists, if not create it
if not os.path.exists('averageMetrics.csv'):
    with open('averageMetrics.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Type","F1","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19","F20","F21","F22","F23","F24","F25","F26","F27", "F28","F29","F30","F31","F32","F33","F34","F35","F36","F37","F38","F39","F40","F41","F42","F43","F44","F45","F46","F47","F48","F49","F50","F51","F52","F53","F54","F55","F56"])



#print out the malicious dictionary
for key in malRates:
    #get the average for each key and print it out
    malRates[key] = malRates[key] / malicious

#print out the benign dictionary
for key in benRates:
    #get the average for each key and print it out
    benRates[key] = benRates[key] / benign

# Open the averageMetrics.csv file in append mode
with open('averageMetrics.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    # Write the rates to the file
    writer.writerow(["Malicious"] + [malRates[key]  for key in malRates])
    writer.writerow(["Benign"] + [benRates[key]  for key in benRates])




