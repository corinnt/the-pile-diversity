import argparse
import requests
import pandas as pd

#from tqdm import tqdm

import parseDetails
from map import map_points
import util

class Data():
    def __init__(self, args):
        self.titles = []
        self.authors = [] #eventually should use for Genderize
        self.years = []
        self.abstracts = []

        self.latitudes = [] # currently just from any institution listed w/ the Work -> shift to author's most recent?
        self.longitudes = []

        self.config = args
        self.id = get_journal_id(args)

def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("email", help="the reply-to email for OpenAlex API calls")
    parser.add_argument("journal_name", type=str, help="name of journal or source to search for")
    parser.add_argument("-v", "--verbose", action="store_true", help="include to print progress messages")
    parser.add_argument("-c", "--write_csv", dest="csv", action="store_true", help="include to write csv of data") 
    parser.add_argument("-a", "--write_abstracts", action="store_true", help="include to write abstracts of all works to csv") 
    parser.add_argument("-m", "--write_maps", dest="maps", action="store_true", help="include to plot locations of affiliated institutions") 
    parser.add_argument("-r", "--restore_saved", action="store_true", help="include to restore saved data") 
    parser.add_argument("--start_year", dest="start_year", type=int, default=None, help="filter publication dates by this earliest year (inclusive)")
    parser.add_argument("--end_year", dest="end_year", type=int, default=None, help="filter publication dates by this latest year (inclusive)")
    args = parser.parse_args()
    if args.verbose: 
        util.VERBOSE = True
    return args

def main(args):
    if args.restore_saved:
        util.info("Restoring saved data from previous run.")
        data = util.unpickle_data('../output/pickled_data')
    else:
        data = Data(args)
        if not data.id:
            return 
        iterate_search(args, data)
        util.pickle_data(data)
    display_data(data)    

def get_journal_id(args):
    """ Returns the OpenAlex Work ID of the top result matching the input journal name
    :param args: parsed user argument object
    :returns str: ID of journal
    """
    url = "https://api.openalex.org/sources?search=" + args.journal_name + '&mailto=' + args.email
    results = {}
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        results = response.json()
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return ""
    except ValueError as e:
        print("Error decoding JSON:", e)
        return ""
    
    if len(results['results']) > 0:
        top_result = results['results'][0]

    if 'id' in top_result: 
        util.info("got id of " + top_result['display_name']) # POSSBUG: multiple journals of same name
        return top_result['id']
    else: 
        print("No results found.")
        return ""

def iterate_search(args, data):
    """ Iterates through all search results for Works by the given source and fitting other criteria
    :param source_id: string - OpenAlex ID of the source to analyze
    :param data: empty Data object
    """
    fields = 'display_name,authorships,concepts,publication_year,abstract_inverted_index'
    search_filters = 'locations.source.id:' + data.id
    if args.start_year:
        search_filters += ',publication_year:>' + str(args.start_year - 1)
    if args.end_year: 
        search_filters += ',publication_year:<' + str(args.end_year + 1)

    works_query_with_page = 'https://api.openalex.org/works?select=' + fields + '&filter=' + search_filters + '&page={}&mailto=' + args.email
    page = 1
    has_more_pages = True
    fewer_than_10k_results = True

    #for page in tqdm(range(int(data.num_works/25))):
    while has_more_pages and fewer_than_10k_results:
        # set page value and request page from OpenAlex
        url = works_query_with_page.format(page)
        page_with_results = requests.get(url).json()
            
        # loop through page of results
        results = page_with_results['results']
        for i, work in enumerate(results):
            title = work['display_name']
            if util.valid_title(title):
                parseDetails.parse_work(work, data)
            
        page += 1
        # end loop when either there are no more results on the requested page 
        # or the next request would exceed 10,000 results
        page_size = page_with_results['meta']['per_page']
        has_more_pages = len(results) == page_size
        fewer_than_10k_results = page_size * page <= 10000
        if (page % 5 == 0):
            util.info("on page " + str(page))

def display_data(data, data_name="data"):
    """ Given populated Data object, displays collected data 
        script args of -c or -m -> CSV of data or maps the institutions of the authors
        :param data: filled Data object 
        :param data_name: base name for output csv or png 
    """
    dict = {'author' : data.authors, 'title' : data.titles, 'year' : data.years}
    if data.config.write_abstracts: dict['abstract'] = data.abstracts
    df = pd.DataFrame(dict)
    util.info(df.head())
    
    if data.config.csv: 
        util.info("writing csv...")
        df.to_csv("../output/" + data_name +".csv")

    if data.config.maps:
        util.info("mapping points...")
        map_dict = {'latitude' : data.latitudes, 'longitude' : data.longitudes} 
        map_df = pd.DataFrame(map_dict)
        df = map_df.groupby(['longitude', 'latitude']).size().reset_index(name='counts')
        map_points(df, "world-" + data_name + "-points" )
        util.info("maps created!")

if __name__ == "__main__":
    args = parseArguments()
    main(args)
 