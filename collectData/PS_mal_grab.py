'''
Program to take in the current list from phishing database and add any successful phishing attempts to the list

 - Want the program to hold the dates of previous scans so it knows where to start and stop this would be the current top date and the current bottom date
   of when the program was last run for continuity sake. 

 - Need to download the latest csv file from: https://phishstats.info/phish_score.csv through wget 

 - Make sure to delete the old csv file before downloading the new one


'''

# Import the needed libraries
import os 
import csv
import whois
from time import sleep
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import signal
from requests_html import HTMLSession

def handler(signum, frame):
    raise Exception("Request timed out")

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


#Check if the csv file exists, if it does, delete it
#if os.path.isfile('phish_score.csv'):
#    os.remove('phish_score.csv')

#Download the csv file from phishstats.info with the most up to date data.
#os.system("wget https://phishstats.info/phish_score.csv")
#os.system("wget https://phishstats.info/phish_score.csv")

#Open the csv file and read it into a list
with open("phish_score.csv", "r") as f:
    csv_list = f.readlines()

#print number of rows in the list
print(len(csv_list))

#get the previous date of scanned url from text file
with open("lastDate.txt", "r") as f:
    previous_date = f.read()

count = 0

first_run = True
new_date = ""

#print out the urls in the list
for row in csv_list[9:]:

    #print("Row: " + str(row))

    #separate the row into a list
    rows = row.split(",")
    print("Length of rows: " + str(len(rows)))

    #get the url from the list
    date = rows[0]
    url = rows[2]

    if first_run:
        new_date = date
        new_date = new_date.replace('"', '')
        first_run = False

    #remove the quotes from the url
    date = date.replace('"', '')
    print(date)

    #Check if the date is the same as the previous date, if so, break out of the loop
    if date == previous_date:
        break
    count += 1

    #clean the url
    url = url.replace('"', '')
    print(url)

    old_url = url

    #fix the url format
    url = fix_url_format(url)

    signal.signal(signal.SIGALRM, handler)

    try:
        # Set an alarm for the timeout
        signal.alarm(10)

        # Make request to website.
        session = HTMLSession()
        session.max_redirects = 20
        response = session.get(url, headers={"User-Agent": "XY"}, allow_redirects=True, verify=False)

        # Cancel the alarm
        signal.alarm(0)

        # Check the status code
        if response.status_code == 200:
            # Request was successful (status code 200)
            print(f"Request was successful: {url}")

            # Check if dataHold.csv does not exist
            if not os.path.isfile('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/v3_data/grabMal/dataHold.csv'):
                # Add the headers to the CSV file
                with open('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/v3_data/grabMal/dataHold.csv', 'a') as f:
                    f.write("id,url,type,redirects,createDate,expireDate,updateDate,registrar\n")

            # Initialize the id variable
            id = 0

            # Get the last id from the CSV file if it exists
            if os.path.isfile('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/v3_data/grabMal/dataHold.csv'):
                with open('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/v3_data/grabMal/dataHold.csv', 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:
                        last_line = lines[-1]
                        last_id = int(last_line.split(",")[0])
                        id = last_id + 1

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
            with open(f"/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/v3_data/grabMal/html/{id}.txt", "w") as f:
                f.write(html)

            # Save the data to the CSV file
            with open('/Users/jackcavar/Library/CloudStorage/OneDrive-AbertayUniversity/Dissertation/URL algorithm/v3_data/grabMal/dataHold.csv', 'a') as f:
                f.write(f"{id},{old_url},1,{num_redirects},{creation},{expiration},{updated},{registrar}\n")

        else:
            # Request failed (status code is not 200)
            print(f"Request failed: {url}")

    except Exception as e:
        # Request timed out
        print(f"Request timed out: {url}")
    

    
#write the new date to the text file
with open("lastDate.txt", "w") as f:
    f.write(new_date)
    f.close()

print("File count: " + str(count))







