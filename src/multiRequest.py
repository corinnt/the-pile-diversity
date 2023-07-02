import requests
import pandas as pd 
from tqdm import tqdm
import argparse
import itertools
from concurrent.futures import ThreadPoolExecutor, wait

import util

def main(args): 
    df = pd.read_csv("data/gene_ids_and_symbols.csv")
    print('Original dataframe: ')
    print(df.head())
    biotypes = iterate_ids(df['GENEID'])
    try:
        df['BIOTYPES'] = biotypes
        print("Writing csv...")
        df.to_csv('data/with_gene_functions.csv', mode='w', index = False, header=True)
    except:
        new_df = pd.DataFrame(biotypes)
        new_df.to_csv('data/backup.csv', mode='w', index = False, header=True)
        
def iterate_ids(all_IDs):
    """ 
        :param all_IDs: list of all IDs
    """
    print('Iterating through genes...')        

    BATCH_SIZE = 50
    MAX_WORKERS = 15 # only 10?

    all_responses = []
    id_batches = [all_IDs[i:i + BATCH_SIZE] for i in range(0, len(all_IDs), BATCH_SIZE)]
    #TOGGLE FOR TEST
    #id_batches = id_batches[:100]
    id_batch_pools = [id_batches[i:i + MAX_WORKERS] for i in range(0, len(id_batches), MAX_WORKERS)]

    for pool in tqdm(id_batch_pools):
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            batch_futures = [executor.submit(process_batch, id_batch, i) for i, id_batch in enumerate(pool)]
            wait(batch_futures)
            results = [task.result() for task in batch_futures]
            results.sort(key=lambda x: x[1]) #thread safety
            results = [result[0] for result in results]
            
            final_pooled_results = list(itertools.chain.from_iterable(results))
            all_responses = all_responses + final_pooled_results
    return all_responses

def process_batch(id_batch, index, data):
    """
        :param id_batch: list of 50 OpenAlex ids
        :param index: int for where the batch goes in the thread pool
    """
    pipe_separated_dois = "|".join(id_batch)
    url = "https://api.openalex.org/institutions?filter=doi:" + {pipe_separated_dois}+ "&per-page=50&mailto=" + data.config.email
    r = util.api_request(url)
    institutions = r.json()["results"]

    return institutions, index
    # TODO: fix batch handling - need to reorder list?

    
def parseArgs():
    parser = argparse.ArgumentParser(description='Model to convert chip signal images to sequences of called bases')
    #parser.add_argument('path', help='Path to top level directory of images')
    #parser.add_argument('-c', '--clear', action='store_true', help='Include to clear saved folder')
    parser.add_argument('-t', '--test', action='store', help='Follow by a gene ID to retrieve biotype for')
    parser.add_argument('-v', '--verbose', action='store_true', help='Include to store quality control and intermediate images')
    args = parser.parse_args()
    #if args.verbose:
    #    util.VERBOSE = True
    return args

if __name__ == '__main__':
    args = parseArgs()
    main(args)