#Imports
from urllib.parse import urlparse, urlunparse,unquote
from requests_html import HTMLSession
import requests
import urllib
import re
import numpy as np
import tldextract
from bs4 import BeautifulSoup
from bs4.element import Comment
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import validators
from sklearn.feature_extraction.text import TfidfVectorizer
from os.path import dirname, join
import pickle
import sys
import ssl
import nltk
import whois
import os


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


def get_old_url(url):
    #if url contains http:// or https://, remove it
    if url.startswith("http://") or url.startswith("https://"):

        if url.startswith("http://"):
            holdURL = url[6:]
            if holdURL.startswith("/"):
                return holdURL
            else:
                return "/" + holdURL
        else:
            holdURL = url[7:]
            if holdURL.startswith("/"):
                return holdURL
            else:
                return "/" + holdURL
    else:
        if url.startswith("/"):
            return url
        else:
            return "/" + url


#Function to take in a url and return a fixed url if the URL wouldn't function
def fix_url_format(url):
    # Parse the URL
    parsed_url = urlparse(url)

    #missing scheme flag
    missing_scheme = 0

    #remove any / from the start of the url ----- test code idea
    while url.startswith("/"):
        url = url[1:]
        print("Removed / from the start of the url: " + str(url) + "\n")

    # Check if the scheme is missing, and add "https://" if so
    if not parsed_url.scheme:
        print(f"URL scheme is missing: {url}")
        url = "https://" + url
        print("HTTPS url: " + str(url) + "\n")

        #flag the missing scheme
        missing_scheme = 1

    else:
        print("URL scheme is not missing: " + str(url) + "\n")

        #check if the scheme is anything other than http or https
        if parsed_url.scheme != "http" and parsed_url.scheme != "https":
            #flag the missing scheme
            missing_scheme = 1
            print("Missing scheme flagged after not missing\n")

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
    #sys.stdout.write("scheme: {}\n".format(scheme).encode())

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
    return url,missing_scheme


# Function to clean and preprocess text
def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\d+', '', text)  # Remove numbers
    text = text.lower()  # Convert to lowercase
    return text

#Function to make a request call to a url and return the html content from the url (F39, F47 - 50)
def get_html_content(url,missing_scheme):

    registrar = 0
    creation_date = 0
    expiration_date = 0
    updated_date = 0
    redirect_count = 0



    try:
        #Make request to website.
        session = HTMLSession()
        session.max_redirects = 20


        response = session.get(url, timeout=10, headers={"User-Agent": "XY"}, allow_redirects=True, verify=False)
        redirect_count = len(response.history)
        print("Redirect count: " + str(redirect_count) + "\n")

    except requests.exceptions.Timeout:
            # The request timed out
            print("Request timed out")

            requestFailed = True
            html_content = ""
            return html_content,1,redirect_count, creation_date, expiration_date, updated_date, registrar

    except Exception as e:
        # Handle other exceptions that may occur during the request
        print(f"An exception occurred: {str(e)}")
        html_content = ""

        requestFailed = True

        if missing_scheme == 1:
            return html_content,2,redirect_count, creation_date, expiration_date, updated_date, registrar
        else:
            return html_content,1,redirect_count, creation_date, expiration_date, updated_date, registrar

    # Check the status code
    if response.status_code == 200:
        # Request was successful (status code 200)
        html_content = response.html.html
        print("HTML content: " + str(html_content) + "\n")
        print("HTML content length: " + str(len(html_content)) + "\n")

        try:

            # Get the whois info
            domain_info = whois.whois(url)

            try:
                #Get the creation, expiration, and updated dates
                creation_date = domain_info.creation_date

                #Filter to year only
                if isinstance(creation_date, list):
                    creation_date = creation_date[0]

                #Check if the creation date is none or not
                if creation_date.year != None:
                    creation_date = creation_date.year
            except:
                creation_date = 0


            try:

                expiration_date = domain_info.expiration_date

                if isinstance(expiration_date, list):
                    expiration_date = expiration_date[0]

                #Check if the expiration date is none or not
                if expiration_date.year != None:
                    expiration_date = expiration_date.year

            except:
                expiration_date = 0

            try:

                updated_date = domain_info.updated_date

                if isinstance(updated_date, list):
                    updated_date = updated_date[0]

                #Check if the updated date is none or not
                if updated_date.year != None:
                    updated_date = updated_date.year

            except:
                updated_date = 0

            try:

                #Check if the registrar is none or not
                if domain_info.registrar != None:
                    registrar = 1
            except:
                registrar = 0
        except:
            creation_date = 0
            expiration_date = 0
            updated_date = 0
            registrar = 0


        print("Creation date: " + str(creation_date) + "\n")
        print("Expiration date: " + str(expiration_date) + "\n")
        print("Updated date: " + str(updated_date) + "\n")

        rates["F47"] = creation_date
        rates["F48"] = expiration_date
        rates["F49"] = updated_date
        rates["F50"] = registrar


        if missing_scheme == 1:
            #return html_content,2,redirect_count, creation_date, expiration_date, updated_date, registrar
            return html_content,0,redirect_count, creation_date, expiration_date, updated_date, registrar
        return html_content,0,redirect_count, creation_date, expiration_date, updated_date, registrar
    else:
        # There was an error in the request
        print(f"Request error: Status code {response.status_code}")

        requestFailed = True

        html_content = ""

        #Number returned is in reference to the message which will be displayed to the user alongside the
        #type of response from the request. If also missing the scheme, it will be considered text (2) else a failed url (1).
        if missing_scheme == 1:
            return html_content,2,redirect_count, creation_date, expiration_date, updated_date, registrar
        else:
            return html_content,1,redirect_count, creation_date, expiration_date, updated_date, registrar





#Functions for gathering the URL features

#Get the URL sequence (1)
def url_sequence(old_url):

    print("Conducting URL extraction...\n")

    print("old_url: ", old_url, "\n")

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

    return padded_sequences

#Get the domain feature quantities (16 - 18)
def domain_features(old_url,url):

    #Calculate .com subdomain
    print("checking for .com subdomain...\n")

    parsed_url = urlparse(url)
    subdomains = parsed_url.netloc.split('.')

    if 'com' in subdomains:
        rates["F16"] = 1
        check_com = 1
    else:
        rates["F16"] = 0
        check_com = 0


    #Check for IP address within the URL

    print("checking for IP address in URL...\n")
    ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    match = re.search(ip_pattern, old_url)

    if bool(match) == True:
        rates["F17"] = 1
        contains_ip = 1
    else:
        rates["F17"] = 0
        contains_ip = 0


    #Check for common TLD

    print("checking for common TLD...\n")

    ext = tldextract.extract(url)

    print(ext.suffix)

    filename_TLD = join(dirname(__file__), 'TLDs.txt')

    # read list of TLD's from TLDs.txt
    with open(filename_TLD, 'r', encoding='utf-8') as file:
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
        contains_tld = 1
    else:
        rates["F18"] = 0
        contains_tld = 0

    return check_com, contains_ip, contains_tld

#Get the domain text length and digit amount (19 - 33)
def domain_digit_features(old_url,url):

    print("Getting the text length of the domain, subdomain and path of the url...\n")

    ext = tldextract.extract(url)

    #get the domain name (19)
    domain = ext.domain
    domain_length = len(domain)
    rates["F19"] = domain_length

    #get the number of digits in the domain name (22)
    digits = sum(c.isdigit() for c in domain)
    domain_digits = digits
    rates["F22"] = digits

    #Get the subdomain (20)
    subdomain = ext.subdomain
    subdomain_length = len(subdomain)
    rates["F20"] = subdomain_length

    #get the number of digits in the subdomain (23)
    digits_sub = sum(c.isdigit() for c in subdomain)
    subdomain_digits = digits_sub
    rates["F23"] = digits_sub

    #get the path (21)
    path_get = urlparse(old_url).path
    path_length = len(path_get)
    rates["F21"] = path_length

    #get the number of digits in the path (24)
    digits_path = sum(c.isdigit() for c in path_get)
    path_digits = digits_path
    rates["F24"] = digits_path

    #Get the port number from the url
    print("Getting the port number from the url...\n")
    portHold = 0
    parsed_url = urlparse(url)
    port = parsed_url.port
    if port != None:
        rates["F43"] = 1
        portHold = 1


    #Check if the URL is relative or absolute
    print("Checking if the URL is relative or absolute...\n")
    URLHold = 0
    if bool(parsed_url.netloc) and bool(parsed_url.scheme):
        rates["F46"] = 1
        URLHold = 1

    
    #Check if the URL is obfuscated
    print("Checking if the URL is obfuscated...\n")
    urlObf = 0
    if unquote(url) != url:
        rates["F56"] = 1
        urlObf = 1


    #Check if the URL contains a file extension
    print("Checking if the URL contains a file extension...\n")
    urlExt = 0
    extension = os.path.splitext(path_get)

    if extension[1]:
        rates["F51"] = 1    
        urlExt = 1

    #Get the special character quantity from the url

    print("Getting the special character quantity from the url...\n")

    #get the quantity of '-' in the url (25)
    dash = old_url.count('-')
    dash_quantity = dash
    rates["F25"] = dash

    #get the quantity of '.' in the url (26)
    dot = old_url.count('.')
    dot_quantity = dot
    rates["F26"] = dot

    #get the quantity of '/' in the url (27)
    slash = old_url.count('/')
    slash_quantity = slash
    rates["F27"] = slash

    #get the quantity of '@' in the url (28)
    at = old_url.count('@')
    at_quantity = at
    rates["F28"] = at

    #get the quantity of '?' in the url (29)
    question = old_url.count('?')
    question_quantity = question
    rates["F29"] = question

    #get the quantity of '=' in the url (30)
    equal = old_url.count('=')
    equal_quantity = equal
    rates["F30"] = equal

    #get the quantity of '_' in the url (31)
    underscore = old_url.count('_')
    underscore_quantity = underscore
    rates["F31"] = underscore

    #get the quantity of '&' in the url (32)
    ampersand = old_url.count('&')
    ampersand_quantity = ampersand
    rates["F32"] = ampersand

    #get the quantity of '~' in the url (33)
    tilde = old_url.count('~')
    tilde_quantity = tilde
    rates["F33"] = tilde

    #get the quantity of '%' in the url
    percent = old_url.count('%')
    print(percent)
    rates["F44"] = percent

    #get the quantity of ':' in the url
    colon = old_url.count(':')
    print(colon)
    rates["F45"] = colon

    return domain_length, subdomain_length, path_length, domain_digits, subdomain_digits, path_digits, dash_quantity, dot_quantity, slash_quantity, at_quantity, question_quantity, equal_quantity, underscore_quantity, ampersand_quantity, tilde_quantity,portHold,percent,colon, URLHold, urlExt, urlObf


#Functions for gathering the HTML content features

#Get the HTML tag features (3 - 15)
def html_tag_features(html_content):

    #BeautifulSoup extraction
    soup = BeautifulSoup(html_content, 'html.parser')
    plaintext = soup.get_text()

    print("Conducting script,css and anchor extraction...\n")

    # Calculate script, css and anchor files
    script_tags = soup.find_all('script', src=True)
    css_tags = soup.find_all('link', rel='stylesheet', href=True)
    img_tags = soup.find_all('img', src=True)
    anchor_tags = soup.find_all('a', href=True)

    total_tags = len(script_tags) + len(css_tags) + len(img_tags) + len(anchor_tags)
    if total_tags > 0:
        script_tag_quantity = len(script_tags) / total_tags
        css_tag_quantity = len(css_tags) / total_tags
        img_tag_quantity = len(img_tags) / total_tags
        anchor_tag_quantity = len(anchor_tags) / total_tags
        rates["F3"] = script_tag_quantity
        rates["F4"] = css_tag_quantity
        rates["F5"] = img_tag_quantity
        rates["F6"] = anchor_tag_quantity
    else:
        script_tag_quantity = 0
        css_tag_quantity = 0
        img_tag_quantity = 0
        anchor_tag_quantity = 0

    print("Conducting empty hyperlink extraction...\n")

    #Calculate empty hyperlink files
    anchor_tags = soup.find_all('a')
    total_hyperlinks = len(anchor_tags)

    if total_hyperlinks > 0:
        anchor_without_href = len([a for a in anchor_tags if not a.has_attr('href')])
        null_hyperlinks = len([a for a in anchor_tags if 'href' in a.attrs and (a['href'] == "#" or a['href'] == "#content" or a['href'] == "javascript:void(0);")])

        anchor_NoHref_quantity = anchor_without_href / total_hyperlinks
        anchor_emp_quantity = null_hyperlinks / total_hyperlinks
        rates["F7"] = anchor_NoHref_quantity
        rates["F8"] = anchor_emp_quantity
    else:
        null_hyperlinks = 0
        anchor_without_href = 0
        anchor_NoHref_quantity = 0
        anchor_emp_quantity = 0

    print("Conducting total hyperlink extraction...\n")

    #Calculate total number of hyperlinks
    anchor_tags = soup.find_all('a')
    link_tags = soup.find_all('link', href=True)
    script_tags = soup.find_all('script', src=True)
    img_tags = soup.find_all('img', src=True)

    total_hyperlinks = len(anchor_tags) + len(link_tags) + len(script_tags) + len(img_tags)
    total_hyperlinks_quantity = total_hyperlinks
    rates["F9"] = total_hyperlinks

    return script_tag_quantity, css_tag_quantity, img_tag_quantity, anchor_tag_quantity, anchor_without_href, null_hyperlinks, total_hyperlinks_quantity

#Get the hyperlink features (10 - 13)
def hyperlink_features(html_content,old_url):

    #BeautifulSoup extraction
    soup = BeautifulSoup(html_content, 'html.parser')
    plaintext = soup.get_text()

    print("Conducting internal and external hyperlink extraction...\n")

    #Calculate number of external and internal hyperlinks
    internal_hyperlinks = []
    external_hyperlinks = []

    internal_hyperlink_quantity = 0
    external_hyperlink_quantity = 0
    total_hyperlink_quantity = 0

    # Extract internal and external hyperlinks from relevant attributes
    for tag in soup.find_all(['img', 'script', 'frame', 'form', 'a', 'link']):
        if 'src' in tag.attrs:
            href = tag['src']
            if href.startswith('http') or href.startswith('www'):
                external_hyperlinks.append(href)
            else:
                internal_hyperlinks.append(href)

    total_hyperlinks = len(internal_hyperlinks) + len(external_hyperlinks)
    hold_total_hyperlinks = total_hyperlinks

    if total_hyperlinks > 0:
        internal_hyperlink_quantity = len(internal_hyperlinks) / total_hyperlinks
        external_hyperlink_quantity = len(external_hyperlinks) / total_hyperlinks
        total_hyperlink_quantity = len(external_hyperlinks) / len(internal_hyperlinks) if len(internal_hyperlinks) > 0 else 0
        rates["F10"] = internal_hyperlink_quantity
        rates["F11"] = external_hyperlink_quantity
        rates["F12"] = total_hyperlink_quantity

    else:
        internal_hyperlink_quantity = 0
        external_hyperlink_quantity = 0
        total_hyperlink_quantity = 0

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
    print("Actual url: ", old_url, "\n")
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
        parsed_url = urlparse(hyperlink)

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

        print("Checking if the URL is valid...\n")

        #Check if the URL is valid
        if validators.url(hyperlink):
            # URL is valid
            continue
        else:
            # URL is invalid
            invalid_hyperlinks += 1

    if total_hyperlinks > 0:
        invalid_hyperlink_quantity = invalid_hyperlinks / total_hyperlinks
        rates["F13"] = invalid_hyperlink_quantity
    else:
        invalid_hyperlink_quantity = 0


    return internal_hyperlink_quantity, external_hyperlink_quantity, total_hyperlink_quantity, invalid_hyperlinks



def form_features(html_content):

    #BeautifulSoup extraction
    soup = BeautifulSoup(html_content, 'html.parser')
    plaintext = soup.get_text()

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
        suspicious_form_quantity = suspicious_forms / total_forms
        suspicious_form_total = suspicious_forms
        rates["F14"] = suspicious_form_quantity
        rates["F15"] = suspicious_form_total
    else:
        suspicious_form_quantity = 0
        suspicious_form_total = 0

    return suspicious_form_quantity, suspicious_form_total

#Get the body features (34 - 38)
def body_features(html_content,url):

    ext = tldextract.extract(url)

    domain = ext.domain

    #BeautifulSoup extraction
    soup = BeautifulSoup(html_content, 'html.parser')
    plaintext = soup.get_text()

    #Get the amount of characters in the body of the HTML content

    print("Conducting body length extraction...\n")

    if soup.body is not None:
        body_length = len(soup.body.get_text())
        print("Body length: ", body_length, "\n")
        rates["F34"] = body_length

    else:
        print("HTML content does not have a body tag.")
        body_length = 0

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
        copyright_tag = 1
        rates["F37"] = 1
    else:
        copyright_tag = 0

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

    iframe = 0
    iframe_tags = soup.find_all('iframe')
    if len(iframe_tags) > 0:
        rates["F40"] = 1
        iframe = 1

    #Check for mailto tag in HTML content
        
    print("Conducting mailto tag extraction...\n")

    mailto = 0
    mailto_tags = soup.find_all('mailto')
    if len(mailto_tags) > 0:
        rates["F41"] = 1
        mailto = 1

    return body_length, paired_tags_count, single_tags_count, copyright_tag, domain_count, iframe, mailto


def get_javascript_features(html_content):
    #BeautifulSoup extraction
    soup = BeautifulSoup(html_content, 'html.parser')
    plaintext = soup.get_text()

    print("Conducting javascript content extraction...\n")

    script_tags = soup.find_all('script')
    script_content = []
    for script in script_tags:
        script_content.append(script.get_text())
    
    #Check for window.open function in javascript content
    
    print("Conducting window.open function extraction...\n")

    javaPop = 0
    for script in script_content:
        if "window.open" in script:
            rates["F42"] = 1
            javaPop = 1
            break

    #Check for javascript native functions being used
    
    print("Conducting javascript native function extraction...\n")

    #check for escape(), eval(), unescape(), exec() and search() functions in javascript content

    javaEscape = 0
    for script in script_content:
        if "escape" in script or "eval" in script or "unescape" in script or "exec" in script or "search" in script:
            rates["F52"] = 1
            javaEscape = 1
            break

    #Check for javascript DOM sturcture elements being used

    print("Conducting javascript DOM structure element extraction...\n")

    #check for appendChild(), createElement(), createTextNode(), insertBefore(), removeChild(), replaceChild() and write() functions in javascript content

    javaDom = 0
    for script in script_content:
        if "appendChild" in script or "createElement" in script or "createTextNode" in script or "insertBefore" in script or "removeChild" in script or "replaceChild" in script or "write" in script:
            rates["F53"] = 1
            javaDom = 1
            break

    #Check for javascript obfuscation functions being used

    print("Conducting javascript obfuscation function extraction...\n")

    #check for functions ActiveXObject(), CreateObject(), CreateTextFile, FileSystemObject
    javaObf = 0
    for script in script_content:
        if "ActiveXObject" in script or "CreateObject" in script or "CreateTextFile" in script or "FileSystemObject" in script:
            rates["F54"] = 1
            javaObf = 1
            break
    
    #Get the length of the javascript content
    
    print("Conducting javascript content length extraction...\n")

    script_length = 0

    for script in script_content:
        rates["F55"] = rates["F55"] + len(script)
        script_length = script_length + len(script)
    
    return javaPop, javaEscape, javaDom, javaObf, script_length

def createFeatureVector(padded_sequences,html_content):

    #BeautifulSoup extraction
    soup = BeautifulSoup(html_content, 'html.parser')
    plaintext = soup.get_text()

    print("Padded sequences special: ", str(padded_sequences), "\n")
    print("rates special: ", str(rates), "\n")

    print("Conducting TF-IDF extraction...\n")

    filename_stop = join(dirname(__file__), 'english.txt')

    #Install nltk english stopwords
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

    # Check if the plaintext is empty or contains only stopwords
    if not plaintext or all(word in stopwords.words('english') for word in plaintext.split()):

        print("padded sequences content: ", str(padded_sequences[0]), "\n")

        print("Rate values: ", str(rates.values()), "\n")

        print("padded sequences size: ", len(padded_sequences[0]), "\n")
        print("rates size: ", len(list(rates.values())), "\n")

        # Initialize the default feature vector as a NumPy array of zeros with shape (5000)
        feature_vector = np.zeros(5000)

        # Check if `padded_sequences[0]` is a NumPy array before accessing its shape
        if isinstance(padded_sequences[0], np.ndarray) and len(padded_sequences[0].shape) > 0:
            feature_vector = np.concatenate((list(rates.values()), padded_sequences[0], feature_vector))

        return feature_vector

    # Tokenization and text cleaning
    nltk.download('punkt')
    tokens = word_tokenize(plaintext)

    cleaned_tokens = [clean_text(token) for token in tokens if token.isalpha()]

    # Remove stopwords
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
        print("tfidf matrix: ", tfidf_matrix, "\n")
        feature_vector = tfidf_matrix.toarray()[0]
        print("feature vector: ", feature_vector, "\n")

        # Pad the feature vector to the desired size (5,000)
        if len(feature_vector) < 5000:
            feature_vector = np.pad(feature_vector, (0, 5000 - len(feature_vector)), 'constant')
        elif len(feature_vector) > 5000:
            feature_vector = feature_vector[:5000]

    except ValueError:
        # Handle the case where TF-IDF cannot be computed
        print("Value error hit\n")
        feature_vector = np.zeros(5000)


    #Print out the rates
    print("Rate values: ", str(rates.values()), "\n")

    print("Conducting concatenation...\n")

    #Combine the feature vector and the HTML feature rates
    try:
        feature_vector = np.concatenate((list(rates.values()),padded_sequences[0], np.atleast_1d(feature_vector)))
        if len(feature_vector) != 5254:
            raise ValueError("Invalid feature vector length")
    except ValueError:
        print("Value error hit\n")
        feature_vector = np.zeros(5254)

    if len(feature_vector) != 5254:
        raise ValueError("Invalid feature vector length")

    return feature_vector








