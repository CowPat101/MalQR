#Jack Cavar
#Program to extract features from the dataset for a feature vector to be created


#Import the libraries
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import pandas as pd
import csv
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
import os
from time import sleep
import numpy as np
import requests
import urllib.parse
from urllib.parse import urlparse, unquote
import validators
import tldextract
from bs4 import Comment


#URL, TF-IDF and html extraction functions

#Function to check for .com subdomain
def has_com_subdomain(url):
    parsed_url = urlparse(url)
    subdomains = parsed_url.netloc.split('.')
    return 'com' in subdomains

# Function to clean and preprocess text
def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.lower()  # Convert to lowercase
    return text

# Function to extract textual content features from the webpage and html content
def extract_text_features(html_content, url, redirects, creation_date, expiration_date, updated_date, registrar,count,type):


    # Initialize HTML feature rates
    rates = {
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

    #URL extraction

    print("Conducting URL extraction...\n")
    
    #Get the length of the URL
    rates["F1"] = len(url)
    
    #Process the redirects and whois information

    print("Processing the redirects and whois information...\n")

    rates["F39"] = redirects
    rates["F47"] = creation_date
    rates["F48"] = expiration_date
    rates["F49"] = updated_date
    rates["F50"] = registrar

    #Calculate .com subdomain

    print("checking for .com subdomain...\n")

    check_com = has_com_subdomain(url)

    if check_com == True:
        rates["F16"] = 1
    else:
        rates["F16"] = 0

    #Check for IP address within the URL

    print("checking for IP address in URL...\n")

    ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    match = re.search(ip_pattern, url)

    if bool(match) == True:
        rates["F17"] = 1
    else:
        rates["F17"] = 0
    
    #Check for common TLD

    print("checking for common TLD...\n")

    ext = tldextract.extract(url)

    print(ext.suffix)

    # read list of TLD's from TLDs.txt
    with open('TLDs.txt', 'r') as file:
        tlds = file.readlines()
    tlds = [tld.strip() for tld in tlds]

    print("TLD is " + ext.suffix.upper())

    # check if suffix is in list of known TLDs
    suffix_parts = ext.suffix.split('.')

    print(suffix_parts)

    #use the last part of the suffix
    suffix = suffix_parts[-1]

    print(suffix)

    if suffix.upper() in tlds:
        rates["F18"] = 1
    else:
        rates["F18"] = 0

    #Get the text length and digit amount of the domain, subdomain and path of the url

    print("Getting the text length of the domain, subdomain and path of the url...\n")

    #get the domain name
    domain = ext.domain
    print(domain)
    rates["F19"] = len(domain)

    #get the number of digits in the domain name
    digits = sum(c.isdigit() for c in domain)
    print(digits)
    rates["F22"] = digits

    #Get the subdomain
    subdomain = ext.subdomain
    print(subdomain)
    rates["F20"] = len(subdomain)

    #get the number of digits in the subdomain
    digits_sub = sum(c.isdigit() for c in subdomain)
    print(digits_sub)
    rates["F23"] = digits_sub

    #get the path
    path_get = urlparse(url).path
    print(path_get)
    rates["F21"] = len(path_get)

    #get the number of digits in the path
    digits_path = sum(c.isdigit() for c in path_get)
    print(digits_path)
    rates["F24"] = digits_path

    #Get the port number from the url
    print("Getting the port number from the url...\n")

    parsed_url = urlparse(url)
    port = parsed_url.port

    if port != None:
        rates["F43"] = 1

    #Check if the URL is relative or absolute
    print("Checking if the URL is relative or absolute...\n")
    if bool(parsed_url.netloc) and bool(parsed_url.scheme):
        rates["F46"] = 1

    #Check if the URL is obfuscated
    print("Checking if the URL is obfuscated...\n")
    if unquote(url) != url:
        rates["F56"] = 1

    #Check if the URL contains a file extension
    print("Checking if the URL contains a file extension...\n")
    extension = os.path.splitext(path_get)

    if extension[1]:
        rates["F51"] = 1

    #Get the special character quantity from the url

    print("Getting the special character quantity from the url...\n")

    #get the quantity of '-' in the url
    dash = url.count('-')
    print(dash)
    rates["F25"] = dash

    #get the quantity of '.' in the url
    dot = url.count('.')
    print(dot)
    rates["F26"] = dot

    #get the quantity of '/' in the url
    slash = url.count('/')
    print(slash)
    rates["F27"] = slash

    #get the quantity of '@' in the url
    at = url.count('@')
    print(at)
    rates["F28"] = at

    #get the quantity of '?' in the url
    question = url.count('?')
    print(question)
    rates["F29"] = question

    #get the quantity of '=' in the url
    equal = url.count('=')
    print(equal)
    rates["F30"] = equal

    #get the quantity of '_' in the url
    underscore = url.count('_')
    print(underscore)
    rates["F31"] = underscore

    #get the quantity of '&' in the url
    ampersand = url.count('&')
    print(ampersand)
    rates["F32"] = ampersand

    #get the quantity of '~' in the url
    tilde = url.count('~')
    print(tilde)
    rates["F33"] = tilde

    #get the quantity of '%' in the url
    percent = url.count('%')
    print(percent)
    rates["F44"] = percent

    #get the quantity of ':' in the url
    colon = url.count(':')
    print(colon)
    rates["F45"] = colon


    soup = BeautifulSoup(html_content, 'html.parser')
    plaintext = soup.get_text()

    # Extract all links from the HTML content to be used for multiple feature
    script_tags = soup.find_all('script', src=True)
    css_tags = soup.find_all('link', rel='stylesheet', href=True)
    img_tags = soup.find_all('img', src=True)
    anchor_tags = soup.find_all('a', href=True)
    link_tags = soup.find_all('link', href=True)

    #Calculate script, css, image and anchor tags

    print("Conducting script,css and achor extraction...\n")

    total_tags = len(script_tags) + len(css_tags) + len(img_tags) + len(anchor_tags)
    if total_tags > 0:
        rates["F3"] = len(script_tags) 
        rates["F4"] = len(css_tags) 
        rates["F5"] = len(img_tags) 
        rates["F6"] = len(anchor_tags) 

    #Calculate empty hyperlink files, update anchor to only look for 'a' no 'href'

    print("Conducting empty hyperlink extraction...\n")      

    anchor_tags = soup.find_all('a')
    total_hyperlinks = len(anchor_tags)

    if total_hyperlinks > 0:
        anchor_without_href = len([a for a in anchor_tags if not a.has_attr('href')])
        null_hyperlinks = len([a for a in anchor_tags if 'href' in a.attrs and (a['href'] == "#" or a['href'] == "#content" or a['href'] == "javascript:void(0);")])
        
        rates["F7"] = anchor_without_href 
        rates["F8"] = null_hyperlinks 

    #Get all of the hyperlinks from the HTML content
    print("Conducting total hyperlink extraction...\n")

    total_hyperlinks = len(anchor_tags) + len(link_tags) + len(script_tags) + len(img_tags)
    rates["F9"] = total_hyperlinks


    print("Conducting internal and external hyperlink extraction...\n")

    #Calculate number of external and internal hyperlinks
    internal_hyperlinks = []
    external_hyperlinks = []

    # Extract internal and external hyperlinks from relevant attributes
    for tag in soup.find_all(['img', 'script', 'frame', 'form', 'a', 'link']):
        if 'src' in tag.attrs:
            href = tag['src']
            if href.startswith('http') or href.startswith('www'):
                external_hyperlinks.append(href)
            else:
                internal_hyperlinks.append(href)

    total_hyperlinks = len(internal_hyperlinks) + len(external_hyperlinks)
    
    if total_hyperlinks > 0:
        rates["F10"] = len(internal_hyperlinks) 
        rates["F11"] = len(external_hyperlinks) 
        rates["F12"] = len(external_hyperlinks) / len(internal_hyperlinks) if len(internal_hyperlinks) > 0 else 0

    #Calculate hyperlink errors

    print("Conducting hyperlink error extraction...\n")

    all_hyperlinks = []

    # Extract hyperlinks from relevant attributes
    for tag in soup.find_all(['img', 'script', 'frame', 'form', 'a', 'link']):
        if 'src' in tag.attrs:
            all_hyperlinks.append(tag['src'])
        elif 'href' in tag.attrs:
            all_hyperlinks.append(tag['href'])


    total_hyperlinks = len(all_hyperlinks)
    invalid_hyperlinks = 0

    # Parse the full URL to get the base URL
    print("Actual url: ", url, "\n")
    baser_url = url

    # Check if the URL starts with a scheme (e.g., "http://" or "https://")
    if not baser_url.startswith("http://") and not baser_url.startswith("https://"):
        # Assuming HTTPS by default
        base_url = "https://" + baser_url
    else:
        base_url = baser_url

    print("Base url: ", base_url, "\n")

    # Check the validity of hyperlinks
    for hyperlink in all_hyperlinks:
        try:
            parsed_url = urlparse(hyperlink)
        except:
            continue

        print("Checking URL path\n")
        #Check if the URL is a relative path
        if not parsed_url.scheme:
            # URL is a relative path, change it to an absolute path
            hyperlink = urllib.parse.urljoin(base_url, hyperlink)
        else:
            #check whether the url contains javascript:void(0)
            if "javascript:void(0)" in hyperlink:
                continue
            else:
                #check that the url starts with http or https
                if not hyperlink.startswith("http://") and not hyperlink.startswith("https://"):
                    #add the http:// to the start of the url
                    hyperlink = "https://" + hyperlink
            # URL is an absolute path
            #print(f"{hyperlink} is not a relative URL.")

        print("Checking if the URL is valid...\n")

        #Check if the URL is valid
        if validators.url(hyperlink):
            # URL is valid
            continue
        else:
            # URL is invalid
            invalid_hyperlinks += 1

    rates["F13"] = invalid_hyperlinks 

    
    #Calculate form features

    print("Conducting form feature extraction...\n")

    total_forms = len(soup.find_all('form'))
    suspicious_forms = 0

    # Extract form action URLs and check if they are suspicious
    for form in soup.find_all('form'):
        action_url = form.get('action', '').strip()
        if not action_url:
            # Action URL is empty
            suspicious_forms += 1
        elif not re.match(r'^https?://', action_url) and not action_url.startswith('/'):
            # Action URL is not a valid URL and not a relative path
            suspicious_forms += 1

    if total_forms > 0:
        rates["F14"] = suspicious_forms / total_forms
        rates["F15"] = suspicious_forms


    #Get the amount of characters in the body of the HTML content

    print("Conducting body length extraction...\n")

    if soup.body is not None:
        body_length = len(soup.body.get_text())
        print("Body length: ", body_length, "\n")

        rates["F34"] = body_length
    else:
        print("HTML content does not have a body tag.")

    #Get the count of the number of HTML paired and single tags inside the body.

    print("Conducting HTML tag extraction...\n")

    # Get all the paired and single HTML tags inside the body
    if soup.body is not None:
        tags = soup.body.find_all()
    else:
        tags = []

    # Count the number of paired and single HTML tags
    paired_tags_count = 0
    single_tags_count = 0

    for tag in tags:
        if tag.string is None:
            paired_tags_count += 1
        else:
            single_tags_count += 1

    rates["F35"] = paired_tags_count
    rates["F36"] = single_tags_count

    #Check if html content contains © symbol

    print("Checking for © symbol...\n")

    if "©" in plaintext:
        rates["F37"] = 1
    else:
        rates["F37"] = 0

    # Look for domain name in HTML content, excluding comments

    print("Checking for domain name in HTML content, excluding comments...\n")

    # Remove comments from the HTML content
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]

    # Count how many times the domain name appears in the HTML content
    domain_count = soup.get_text().count(domain)
    rates["F38"] = domain_count


    #Check for iFrame tag in HTML content
    
    print("Conducting iFrame tag extraction...\n")

    iframe_tags = soup.find_all('iframe')
    if len(iframe_tags) > 0:
        rates["F40"] = 1

    #Check for mailto tag in HTML content
        
    print("Conducting mailto tag extraction...\n")

    mailto_tags = soup.find_all('mailto')
    if len(mailto_tags) > 0:
        rates["F41"] = 1

    #Filter to only get the javascript content from the HTML content
    
    print("Conducting javascript content extraction...\n")

    script_tags = soup.find_all('script')
    script_content = []
    for script in script_tags:
        script_content.append(script.get_text())
    
    #Check for window.open function in javascript content
    
    print("Conducting window.open function extraction...\n")

    for script in script_content:
        if "window.open" in script:
            rates["F42"] = 1
            break

    #Check for javascript native functions being used
    
    print("Conducting javascript native function extraction...\n")

    #check for escape(), eval(), unescape(), exec() and search() functions in javascript content

    for script in script_content:
        if "escape" in script or "eval" in script or "unescape" in script or "exec" in script or "search" in script:
            rates["F52"] = 1
            break

    #Check for javascript DOM sturcture elements being used

    print("Conducting javascript DOM structure element extraction...\n")

    #check for appendChild(), createElement(), createTextNode(), insertBefore(), removeChild(), replaceChild() and write() functions in javascript content

    for script in script_content:
        if "appendChild" in script or "createElement" in script or "createTextNode" in script or "insertBefore" in script or "removeChild" in script or "replaceChild" in script or "write" in script:
            rates["F53"] = 1
            break

    #Check for javascript obfuscation functions being used

    print("Conducting javascript obfuscation function extraction...\n")

    #check for functions ActiveXObject(), CreateObject(), CreateTextFile, FileSystemObject

    for script in script_content:
        if "ActiveXObject" in script or "CreateObject" in script or "CreateTextFile" in script or "FileSystemObject" in script:
            rates["F54"] = 1
            break
    
    #Get the length of the javascript content
    
    print("Conducting javascript content length extraction...\n")

    for script in script_content:
        rates["F55"] = rates["F55"] + len(script)

    #Note: The features of TF-IDF are not collected as they are deemed uneccessary for the app content to display hence F2 is skipped.
    
    
    #Open the CSV file to write the features to.
        
    with open('featureMetrics.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([count,type,rates["F1"],rates["F3"],rates["F4"],rates["F5"],rates["F6"],rates["F7"],rates["F8"],rates["F9"],rates["F10"],rates["F11"],rates["F12"],rates["F13"],rates["F14"],rates["F15"],rates["F16"],rates["F17"],rates["F18"],rates["F19"],rates["F20"],rates["F21"],rates["F22"],rates["F23"],rates["F24"],rates["F25"],rates["F26"],rates["F27"],rates["F28"],rates["F29"],rates["F30"],rates["F31"],rates["F32"],rates["F33"],rates["F34"],rates["F35"],rates["F36"],rates["F37"],rates["F38"],rates["F39"],rates["F40"],rates["F41"],rates["F42"],rates["F43"],rates["F44"],rates["F45"],rates["F46"],rates["F47"],rates["F48"],rates["F49"],rates["F50"],rates["F51"],rates["F52"],rates["F53"],rates["F54"],rates["F55"],rates["F56"]])
        
    


#Main function to extract the features from the dataset

def extract_features_and_split(df, training_output_file, validation_output_file, validation_split=0.2):
    # Path to the folder containing HTML txt files
    html_folder = '/Users/jackcavar/Documents/University work/Dissertation/creationTest/html'

    # Calculate the number of samples and the split point
    num_samples = len(df)
    num_validation = int(validation_split * num_samples)

    print("Number of samples: ", num_samples)
    print("Number of validation samples: ", num_validation)

    # Shuffle the data randomly 
    df = df.sample(frac=1).reset_index(drop=True)

    # Initialize counters
    validation_count = 0
    training_count = 0
    i=0

    # Initialize empty lists for features and labels
    training_features = []
    training_labels = []
    validation_features = []
    validation_labels = []

    #check if featureMetrics.csv exists, if so delete it
    if os.path.exists('featureMetrics.csv'):
        os.remove('featureMetrics.csv')

    #Check if featureMetrics.csv exists, if not create it
    if not os.path.exists('featureMetrics.csv'):
        with open('featureMetrics.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID","Type","F1","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12","F13","F14","F15","F16","F17","F18","F19","F20","F21","F22","F23","F24","F25","F26","F27", "F28","F29","F30","F31","F32","F33","F34","F35","F36","F37","F38","F39","F40","F41","F42","F43","F44","F45","F46","F47","F48","F49","F50","F51","F52","F53","F54","F55","F56"])

    for id, label in zip(df['id'], df['type']):
        print("ID: ", id, "\n")
        html_file_path = os.path.join(html_folder, f"{id}.txt")
        if os.path.exists(html_file_path):
            with open(html_file_path, mode='r', encoding='utf-8') as file:
                html_content = file.read()

                #Display the number of samples processed
                print(f"Processing URL {i+1}/{num_samples} with id of {df['id'][i]}", end="\r")

                #Extract the and whois infromation from the csv file
                redirects = df['redirects'][i]
                creation_date = df['createDate'][i]
                expiration_date = df['expireDate'][i]
                updated_date = df['updateDate'][i]
                registrar = df['registrar'][i]
                
                extract_text_features(html_content, df['url'][i],redirects,creation_date,expiration_date,updated_date,registrar,i,df['type'][i])

                i+=1


        else:
            print("File does not exist")


#URL extraction

#Open the CSV file
df = pd.read_excel('/Users/jackcavar/Documents/University work/Dissertation/creationTest/dataComb.xlsx')

import nltk

#Create a ssl certificate to download the nltk packages
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('stopwords')
nltk.corpus.stopwords.words('english')

# Specify the output files for training and validation data
training_output_file = 'training_featuresv7.npz'
validation_output_file = 'validation_featuresv7.npz'

# Set the validation split ratio to 80:20.
validation_split = 0.2

# Call the function to extract features, split the data, and save it
extract_features_and_split(df, training_output_file, validation_output_file, validation_split)


