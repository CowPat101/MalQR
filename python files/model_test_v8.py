#Test model performance on test data

#Import libraries
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import pandas as pd
import os
import random
from PIL import Image
from tensorflow import keras
import xgboost as xgb
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
from urllib.parse import urlparse
import validators
from urllib.parse import urlparse, urlunparse,unquote
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import tldextract
from bs4 import Comment
from requests_html import HTMLSession
import onnx
import signal
import whois
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def handler(signum, frame):
    raise Exception("Request timed out")


#URL, TF-IDF and html extraction functions

#Function to check for .com subdomain
def has_com_subdomain(url):
    parsed_url = urlparse(url)
    subdomains = parsed_url.netloc.split('.')
    print("Subdomains: ", subdomains, "\n")
    return 'com' in subdomains

# Function to clean and preprocess text
def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.lower()  # Convert to lowercase
    return text

# Function to extract textual content features from the webpage and html content
def extract_text_features(html_content, url, redirects, creation_date, expiration_date, updated_date, registrar):

#URL extraction

    print("Conducting URL extraction...\n")
    # Define the fixed length for the padded sequences
    fixed_length = 200

    # Convert each URL to a sequence of integers using ASCII encoding
    sequences = []
    
    sequence = [ord(c) for c in old_url]
    sequences.append(sequence)

    # Pad each sequence with zeros to the fixed length
    padded_sequences = []
    for sequence in sequences:
        if len(sequence) < fixed_length:
            padding = [0] * (fixed_length - len(sequence))
            padded_sequence = sequence + padding
        else:
            padded_sequence = sequence[:fixed_length]
        padded_sequences.append(padded_sequence)

    # Convert the padded sequences to a numpy array
    padded_sequences = np.array(padded_sequences)

    # Initialize HTML feature rates
    rates = {"F3": 0,
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
    match = re.search(ip_pattern, old_url)

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
    path_get = urlparse(old_url).path
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

    if extension:
        rates["F51"] = 1

    #Get the special character quantity from the url

    print("Getting the special character quantity from the url...\n")

    #get the quantity of '-' in the url
    dash = old_url.count('-')
    print(dash)
    rates["F25"] = dash

    #get the quantity of '.' in the url
    dot = old_url.count('.')
    print(dot)
    rates["F26"] = dot

    #get the quantity of '/' in the url
    slash = old_url.count('/')
    print(slash)
    rates["F27"] = slash

    #get the quantity of '@' in the url
    at = old_url.count('@')
    print(at)
    rates["F28"] = at

    #get the quantity of '?' in the url
    question = old_url.count('?')
    print(question)
    rates["F29"] = question

    #get the quantity of '=' in the url
    equal = old_url.count('=')
    print(equal)
    rates["F30"] = equal

    #get the quantity of '_' in the url
    underscore = old_url.count('_')
    print(underscore)
    rates["F31"] = underscore

    #get the quantity of '&' in the url
    ampersand = old_url.count('&')
    print(ampersand)
    rates["F32"] = ampersand

    #get the quantity of '~' in the url
    tilde = old_url.count('~')
    print(tilde)
    rates["F33"] = tilde

    #get the quantity of '%' in the url
    percent = old_url.count('%')
    print(percent)
    rates["F44"] = percent

    #get the quantity of ':' in the url
    colon = old_url.count(':')
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
        rates["F3"] = len(script_tags) / total_tags
        rates["F4"] = len(css_tags) / total_tags
        rates["F5"] = len(img_tags) / total_tags
        rates["F6"] = len(anchor_tags) / total_tags

    #Calculate empty hyperlink files, update anchor to only look for 'a' no 'href'

    print("Conducting empty hyperlink extraction...\n")      

    anchor_tags = soup.find_all('a')
    total_hyperlinks = len(anchor_tags)

    if total_hyperlinks > 0:
        anchor_without_href = len([a for a in anchor_tags if not a.has_attr('href')])
        null_hyperlinks = len([a for a in anchor_tags if 'href' in a.attrs and (a['href'] == "#" or a['href'] == "#content" or a['href'] == "javascript:void(0);")])
        
        rates["F7"] = anchor_without_href / total_hyperlinks
        rates["F8"] = null_hyperlinks / total_hyperlinks

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
        rates["F10"] = len(internal_hyperlinks) / total_hyperlinks
        rates["F11"] = len(external_hyperlinks) / total_hyperlinks
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
    baser_url = old_url

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

    if total_hyperlinks > 0:
        rates["F13"] = invalid_hyperlinks / total_hyperlinks

        print("Rate 13: ", str(rates["F13"]), "\n")

    
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

    #print out all new added features
    print("F39: ", rates["F39"], "\n")
    print("F40: ", rates["F40"], "\n")
    print("F41: ", rates["F41"], "\n")
    print("F42: ", rates["F42"], "\n")
    print("F43: ", rates["F43"], "\n")
    print("F44: ", rates["F44"], "\n")
    print("F45: ", rates["F45"], "\n")
    print("F46: ", rates["F46"], "\n")
    print("F47: ", rates["F47"], "\n")
    print("F48: ", rates["F48"], "\n")
    print("F49: ", rates["F49"], "\n")
    print("F50: ", rates["F50"], "\n")
    print("F51: ", rates["F51"], "\n")
    print("F52: ", rates["F52"], "\n")
    print("F53: ", rates["F53"], "\n")
    print("F54: ", rates["F54"], "\n")
    print("F55: ", rates["F55"], "\n")
    print("F56: ", rates["F56"], "\n")

    #Conduct TF-IDF extraction

    print("Conducting TF-IDF extraction...\n")

    # Return default feature vector if plaintext is empty or contains only stop words
    if not plaintext or all(word in stopwords.words('english') for word in plaintext.split()):


        print("padded sequences content: ", str(padded_sequences[0]), "\n")

        print("padded sequences size: ", len(padded_sequences[0]), "\n")
        print("rates size: ", len(list(rates.values())), "\n")

        # Initialize the default feature vector as a NumPy array of zeros with shape (5000,)
        feature_vector = np.zeros(5000)

        # Check if `padded_sequences[0]` is a NumPy array before accessing its shape
        if isinstance(padded_sequences[0], np.ndarray) and len(padded_sequences[0].shape) > 0:
            feature_vector = np.concatenate((padded_sequences[0],list(rates.values()),feature_vector))

        return feature_vector  # Return a NumPy array with the concatenated values

    # Tokenization and text cleaning
    tokens = word_tokenize(plaintext)
    cleaned_tokens = [clean_text(token) for token in tokens if token.isalpha()]

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in cleaned_tokens if token not in stop_words]

    # Stemming
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in filtered_tokens]

    # Join tokens back to text
    cleaned_text = ' '.join(stemmed_tokens)

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)  
    try:
        tfidf_matrix = vectorizer.fit_transform([cleaned_text])
        feature_vector = tfidf_matrix.toarray()[0]

        # Pad the feature vector to the desired size (25,000)
        if len(feature_vector) < 5000:
            feature_vector = np.pad(feature_vector, (0, 5000 - len(feature_vector)), 'constant')
        elif len(feature_vector) > 5000:
            feature_vector = feature_vector[:5000]

    except ValueError:
        # Handle the case where TF-IDF cannot be computed
        feature_vector = np.zeros(5000)

    print("Conducting concatenation...\n")

    #Combine the feature vector and the HTML feature rates
    try:
        feature_vector = np.concatenate((padded_sequences[0],list(rates.values()), np.atleast_1d(feature_vector)))
        if len(feature_vector) != 5254:
            raise ValueError("Invalid feature vector length")
    except ValueError:
        feature_vector = np.zeros(5254)

    if len(feature_vector) != 5254:
        raise ValueError("Invalid feature vector length")

    return feature_vector

def fix_url_format(url):
    # Parse the URL
    parsed_url = urlparse(url)
    
    
    # Check if the scheme is missing, and add "https://" if so
    if not parsed_url.scheme:
        print(f"URL scheme is missing: {url}")
        url = "https://" + url
        print("HTTPS url: " + str(url) + "\n")

    #check if the parsed scheme is http, if so, change it to https
    if parsed_url.scheme == "http":
        print(f"URL scheme is http: {url}")
        url = "https://" + url[7:]
        print("HTTPS url: " + str(url) + "\n")

    #Update the parsed URL
    parsed_url = urlparse(url)

    # Extract the scheme of the URL
    scheme = parsed_url.scheme
    print("scheme: " + str(scheme) + "\n")
    
    # Check if the hostname (netloc) is missing, and add "www" as a subdomain if so
    if not parsed_url.netloc:
        print(f"URL hostname is missing: {url}")
        path_parts = parsed_url.path.split('/', 1)
        print("Path parts: " + str(path_parts) + "\n")
        hostname = path_parts[0]
        print("Hostname: " + str(hostname) + "\n")
        path = path_parts[1] if len(path_parts) > 1 else ""
        print("Path: " + str(path) + "\n")
        fixed_netloc = f"www.{hostname}" if hostname else ""
        print("Fixed netloc: " + str(fixed_netloc) + "\n")

        print("Parsed url scheme: " + str(scheme) + "\n")
        
        # Reconstruct the URL with the fixed netloc and original scheme
        url = urlunparse((scheme, fixed_netloc, path, *parsed_url[3:]))
    
    return url

# Read the csv test data file
df = pd.read_csv('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/Images algorithm/urls/urldata.csv')

# Extract the urls from the B column
urls = df['url'].tolist()
results = df['result'].tolist()

#combine the urls and results into a list of tuples
urls = list(zip(urls, results))

# Shuffle the list of urls, keeping the urls and results together
random.shuffle(urls)

#Check if the predictions.csv file exists, if so, delete it
if os.path.exists('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/predictions.csv'):
    os.remove('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/predictions.csv')

#Add the column headers, benign, malicious, actual to the csv file
with open('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/predictions.csv', 'a') as f:
    f.write("Benign,Malicious,Actual,Response,Result,URL\n")



import lightgbm as lgb

# Load the LightGBM machine learning model
loaded_model = lgb.Booster(model_file='/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/v8/lightgbm_modelv8v15.model')

# View the parameters used to train the model
params = loaded_model.params
print("Params: " + str(params))

#For every url in the list, create a QR code, make a prediction, print the result and delete the image
true_positives = 0
false_positives = 0
true_negatives = 0
false_negatives = 0

y_true = []
y_pred = []

for urli in urls[:1000]:

    url = urli[0]

    #url = "www.bbc.com"
    #url = "https://www.google.com/"
    #url = "https://ed4.inovarun.com.br/pkt/app/login.php"
    #url = "https://bluepostfuc.top/de/"

    requestFailed = False

    print("URL: " + str(url) + "\n")

    old_url = url


    #if url contains http:// or https://, remove it
    '''
    if url.startswith("http://") or url.startswith("https://"):


        if url.startswith("http://"):
            old_url = url[6:]
        else:
            old_url = url[7:]
    '''
    
    if url.startswith("http://") or url.startswith("https://"):

        if url.startswith("http://"):
            old_url = url[6:]
            if old_url.startswith("/"):
                old_url = old_url
            else:
                old_url = "/" + old_url
        else:
            old_url = url[7:]
            if old_url.startswith("/"):
                old_url = old_url
            else:
                old_url = "/" + old_url
    else:
        if url.startswith("/"):
            old_url = url
        else:
            old_url = "/" + url
            
        print("Removed http:// or https:// from url\n")


    print("Old URL: " + str(old_url) + "\n")   

    # Fix the URL format
    url = fix_url_format(url)

    #old_url = url

    print("Fixed URL: " + str(url) + "\n")

    signal.signal(signal.SIGALRM, handler)

    try:
        # Set an alarm for the timeout
        signal.alarm(15)

        # Make request to website.
        session = HTMLSession()
        session.max_redirects = 20
        response = session.get(url, headers={"User-Agent": "XY"}, allow_redirects=True, verify=False)
        redirect_count = len(response.history)
        print("Redirect count: " + str(redirect_count) + "\n")
        sleep(10)

        # Cancel the alarm
        signal.alarm(0)

        # Check the status code
        if response.status_code == 200:
            # Request was successful (status code 200)
            html_content = response.html.html
            #print("HTML content: " + str(html_content) + "\n")
            print ("HTML content length: " + str(len(html_content)) + "\n")

            # Get the number of redirects
            redirects = len(response.history)

            # Get the whois info
            domain_info = whois.whois(url)

            #Get the creation, expiration, and updated dates
            creation_date = domain_info.creation_date
            expiration_date = domain_info.expiration_date
            updated_date = domain_info.updated_date

            #Filter to year only
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            if isinstance(expiration_date, list):
                expiration_date = expiration_date[0]
            if isinstance(updated_date, list):
                updated_date = updated_date[0]

            #Check if the registrar is none or not
            if domain_info.registrar != None:   
                registrar = 1
            else:
                registrar = 0
            
            #Check if the creation date is none or not
            if creation_date.year != None:
                creation_date = creation_date.year
            else:
                creation_date = 0
            
            #Check if the expiration date is none or not
            if expiration_date.year != None:
                expiration_date = expiration_date.year
            else:
                expiration_date = 0
            
            #Check if the updated date is none or not
            if updated_date.year != None:
                updated_date = updated_date.year
            else:
                updated_date = 0

        else:
            # There was an error in the request
            print(f"Request error: Status code {response.status_code}")

            requestFailed = True

            html_content = ""

            redirects = 0
            creation_date = 0
            expiration_date = 0
            updated_date = 0
            registrar = 0


            #continue  # Skip this URL and proceed to the next one

    except Exception as e:
        # Handle exceptions that may occur during the request
        print(f"An exception occurred: {str(e)}")

        requestFailed = True
        html_content = ""
        redirects = 0
        creation_date = 0
        expiration_date = 0
        updated_date = 0
        registrar = 0
        #continue  # Skip this URL and proceed to the next one

    #Extract the feature vector from the url
    feature_vector = extract_text_features(html_content,old_url,redirects,creation_date,expiration_date,updated_date,registrar)

    print("feature vector length: ", len(feature_vector), "\n")

    #Make feature vector a numpy array
    feature_array = np.array(feature_vector, dtype=np.float64)[np.newaxis, :]

    #print the feature array shape
    print("feature array shape: ", feature_array.shape, "\n")

    #print the feature array
    print("feature array: ", feature_array, "\n")

    #Transform feature vector into a Dmatrix object
    #dmatrix = xgb.DMatrix(feature_array)

    # Make a prediction using the model
    #prediction = loaded_model.predict(dmatrix)
    prediction = loaded_model.predict(feature_array)

    # Convert feature_array to float32
    feature_array = np.array(feature_array, dtype=np.float32)


    #Print out the prediction and what the actual result should be
    print("Prediction: ", prediction)
    print("Result: ", urli[1])

    y_true.append(urli[1])

    '''
    y_pred.append(1 if prediction >= 0.5 else 0)

    # Calculate the metrics using sklearn
    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)

    # Output the metrics
    print('Accuracy:', accuracy)
    print('Precision:', precision)
    print('Recall:', recall)
    print('F1 score:', f1)

    '''
    y_pred.append(prediction.round()) 

    requestDisplay = ""
    if requestFailed == True:
        requestDisplay = "Failed"
    else:
        requestDisplay = "Success"

    if(requestFailed == False):


        #append a file with the url, prediction and result, if the result is 0, place the prediction in the benign column, if the result is 1, place the prediction in the malicious column
        with open('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/predictions.csv', 'a', encoding='utf-8') as f:
            if urli[1] <= 0.99:
                if prediction <= 0.99:
                    f.write(str(prediction) + ",," + str(urli[1]) + "," + str(requestDisplay) + "," + str("Correct") + "," + str(url) + "\n")
                else:
                    f.write(str(prediction) + ",," + str(urli[1]) + "," + str(requestDisplay) + "," + str("Wrong") + "," + str(url) + "\n")
            else:
                if prediction >= 0.99:
                    f.write("," + str(prediction) + "," + str(urli[1]) + "," + str(requestDisplay) + "," + str("Correct") + "," + str(url) + "\n")
                else:
                    f.write("," + str(prediction) + "," + str(urli[1]) + "," + str(requestDisplay) + "," + str("Wrong") + "," + str(url) + "\n")
                
        # Update the true/false positive/negative counts
        if prediction >= 0.99 and urli[1] == 1:
            true_positives += 1
        elif prediction >= 0.99 and urli[1] == 0:
            false_positives += 1
        elif prediction < 0.99 and urli[1] == 0:
            true_negatives += 1
        elif prediction < 0.99 and urli[1] == 1:
            false_negatives += 1

        # Print the predicted class
        if prediction >= 0.99:
            print('The image is malicious.')
        else:
            print('The image is benign.')
    

# Calculate the metrics

epsilon = 1e-7  
accuracy = (true_positives + true_negatives) / (true_positives + true_negatives + false_positives + false_negatives + epsilon)
precision = true_positives / (true_positives + false_positives + epsilon)
recall = true_positives / (true_positives + false_negatives + epsilon)
f1_score = 2 * (precision * recall) / (precision + recall + epsilon)



# Output the metrics
print('Accuracy:', accuracy)
print('Precision:', precision)
print('Recall:', recall)
print('F1 score:', f1_score)


print("Feature array size: ", feature_array.size)


# Calculate the confusion matrix
cm = confusion_matrix(y_true, y_pred)

# Print the confusion matrix
print('Confusion matrix:')
print(cm)