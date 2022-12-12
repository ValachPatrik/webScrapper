# webScrapper
scrapper of python documentation for statistical data

The programm scours trough the given website and does the folowing:
## Find and Download
Finds all the websites present within the given domain, so that the programm does not leave to outside sources.
The site adresses are then stored for future runs and to offload some of the strain on the servers of the website.
With this idea in mind the websites are also downloaded into a new folder created by the program and as long as it is present,
there is no longer the need to access the online website and therefore all the statistical scouring is then done locally.
## Analysis
### Linux only Availability
Finds all functions that area available only on Linux systems
    :param base_url: base url of the website
    :return: all function names that area available only on Linux systems
### Most visited webpage
Finds the page with most links to it
    :param url_all: all urls to search
    :return: number of anchors to this page and its URL
### Changes
Locates all counts of changes of functions and groups them by version
    :param base_url: base url of the website
    :return: all counts of changes of functions and groups them by version, sorted from the most changes DESC
### Most parameters
Finds the function that accepts more than 10 parameters
    :param base_url: base url of the website
    :return: number of parameters of this function and its name, sorted by the count DESC
