#Program to collect benign URLs from the Alexa top 1 million list and form the benign dataset

# Import the necessary libraries
import requests
import csv
from urllib.parse import urlparse, urlunparse
import signal
from requests_html import HTMLSession
import os
import whois
from time import sleep

def handler(signum, frame):
    raise Exception("Request timed out")

#Function to fix the URL format
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




start_row = 0

#Check if the holdLineBen.txt file exists
if os.path.isfile('holdLineBen.txt'):
    #Open the file and get the hold line value
    with open('holdLineBen.txt', 'r') as f:
        hold_line = f.read()
        start_row = int(hold_line) + 1

#Open the Alexa top 1 million list

with open('/Users/jackcavar/Documents/University work/Dissertation/v3Datasets/top-1m.csv', 'r') as csv_file:
    csv_reader = csv.reader(csv_file)
    for row in csv_reader:
        #Skip the first 20 rows
        if start_row > 0:
            start_row -= 1
            continue
        print("ID: " + str(row[0]) + "\n")
        print("URL: " + str(row[1]) + "\n")
        url = row[1]

        #Fix the URL format
        url = fix_url_format(url)
        print("Fixed url: " + str(url) + "\n")

        #make a request to the URL
        signal.signal(signal.SIGALRM, handler)

        try:
            # Set an alarm for the timeout
            signal.alarm(10)

            # Make request to website.
            session = HTMLSession()
            session.max_redirects = 20
            response = session.get(url, headers={"User-Agent": "XY"}, allow_redirects=True, verify=False)
            full_url = response.url

            print("Full url: " + str(full_url) + "\n")

            # Cancel the alarm
            signal.alarm(0)
            
            # Check the status code
            if response.status_code == 200:
                # Request was successful (status code 200)
                print(f"Request was successful: {url}")

                # Check if dataHold.csv does not exist
                if not os.path.isfile('dataHoldBen.csv'):
                    # Add the headers to the CSV file
                    with open('dataHoldBen.csv', 'a') as f:
                        f.write("id,url,type,redirects,createDate,expireDate,updateDate,registrar\n")

                # Initialize the id variable
                id = 135545

                hold_line = row[0]

                # Get the last id from the CSV file if it exists
                if os.path.isfile('dataHoldBen.csv'):
                    with open('dataHoldBen.csv', 'r') as f:
                        lines = f.readlines()
                        print("Lines: " + str(len(lines)) + "\n")
                        if len(lines) > 1:
                            last_line = lines[-1]
                            last_id = int(last_line.split(",")[0])
                            id = last_id + 1

                if id == 301211:
                    exit()

                # Get the number of redirects
                num_redirects = len(response.history)

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
                    creation = creation_date.year
                else:
                    creation = 0
                
                #Check if the expiration date is none or not
                if expiration_date.year != None:
                    expiration = expiration_date.year
                else:
                    expiration = 0
                
                #Check if the updated date is none or not
                if updated_date.year != None:
                    updated = updated_date.year
                else:
                    updated = 0

                #Get the html content of the page
                html = response.html.html

                #Save the html content to the file with the id as the name
                with open(f"html/{id}.txt", "w") as f:
                    f.write(html)

                # Save the data to the CSV file
                with open('dataHoldBen.csv', 'a') as f:
                    f.write(f"{id},{full_url},0,{num_redirects},{creation},{expiration},{updated},{registrar}\n")
                
                #save hold_line value to a file
                with open('holdLineBen.txt', 'w') as f:
                    f.write(str(hold_line))
                #close the file
                    f.close()
                sleep(1)

            else:
                # Request failed (status code is not 200)
                print(f"Request failed: {url}")
            

        except Exception as e:
            # Request timed out
            print(f"Request timed out: {url}")