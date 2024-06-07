import scrapy
from time import sleep
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import signal
from requests_html import HTMLSession
import os
import whois

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

class WebsitesmSpider(scrapy.Spider):
    name = "malGrab"
    allowed_domains = ["phishtank.org"]
    #start_urls = ["https://phishtank.org/phish_search.php?page=0&active=y&valid=u&Search=Search"] 
    start_urls = ["https://phishtank.org/phish_search.php?page=0&active=y&valid=y&Search=Search"]

    def parse(self, response):
        #get all the links to the phishing id pages
        for href in response.css('table.data td.value a::attr(href)'):
            #check if the link starts with phish to know that the id is being selected
            if href.extract().startswith('phish'):
                print(href.extract())
                #form the url to the phishing id page
                url = "https://phishtank.org/" + href.extract()
                print(url)
                yield response.follow(url, self.parse_phish)

        # After processing this page, increment the page number in the URL
        url_parts = list(urlparse(response.url))
        query = dict(parse_qs(url_parts[4]))
        page_number = int(query.get('page', ['0'])[0])  # get current page number, default to 0 if not present
        query['page'] = [str(page_number + 1)]  # increment page number
        url_parts[4] = urlencode(query, doseq=True)  # update the query part of the URL
        next_page_url = urlunparse(url_parts)

        #Check if the page number is a certain value, if so stop the spider
        if page_number == 25:
            raise scrapy.exceptions.CloseSpider('page_number exceeded')

        yield scrapy.Request(next_page_url, self.parse)
        pass
    
    def parse_phish(self, response):
        #get the url of the phishing page
        for i, href in enumerate(response.css('b')):
            if i == 1:

                #remove the <b> and </b> tags
                url = href.extract()[3:-4]
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
                        if not os.path.isfile('dataHold.csv'):
                            # Add the headers to the CSV file
                            with open('dataHold.csv', 'a') as f:
                                f.write("id,url,type,redirects,createDate,expireDate,updateDate,registrar\n")

                        # Initialize the id variable
                        id = 0

                        # Get the last id from the CSV file if it exists
                        if os.path.isfile('dataHold.csv'):
                            with open('dataHold.csv', 'r') as f:
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
                        with open(f"html/{id}.txt", "w") as f:
                            f.write(html)

                        # Save the data to the CSV file
                        with open('dataHold.csv', 'a') as f:
                            f.write(f"{id},{old_url},1,{num_redirects},{creation},{expiration},{updated},{registrar}\n")

                    else:
                        # Request failed (status code is not 200)
                        print(f"Request failed: {url}")

                except Exception as e:
                    # Request timed out
                    print(f"Request timed out: {url}")

                break
        sleep(1)


