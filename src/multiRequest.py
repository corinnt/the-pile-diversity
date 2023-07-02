import pandas as pd 
from tqdm import tqdm
import argparse
import itertools
from concurrent.futures import ThreadPoolExecutor, wait

import util

def iterate_ids(all_IDs):
    """ 
        :param all_IDs: list of all OpenAlex Institution IDs
    """
    print('Iterating through Institution IDs...')        

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
