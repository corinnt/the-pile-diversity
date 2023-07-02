import requests
from util import increment, decode_inverted, info, api_request

def parse_work(work, data):
    """
        :param work: single Work object from OpenAlex
        :param data: partially full Data object
    """
    title = work['display_name']
    if not title: title = 'NA'
    data.titles.append(title)

    year = str(work['publication_year'])
    if not year: year = 'NA'
    data.years.append(year)

    if data.config.write_abstracts:
        inverted_index = work['abstract_inverted_index']
        if inverted_index:
            decode_inverted(inverted_index, data)
        else:
            data.abstracts.append('NA')

    authorship_list = work['authorships']
    if authorship_list:
        parse_authorship(authorship_list, data)
    else:
        data.authors.append('NA')


def parse_authorship(authorships, data):
    """
        :param authorships: list of authorship objects from the OpenAlex API
        :param data: partially full Data object
    """
    author_string = ""
    for authorship in authorships:
        author_string += authorship['author']['display_name'] + "; "
        for institution in authorship['institutions']:
            id = institution['id']
            #if id: parse_geodata(id, data)
            if id: data.institution_ids.append(id)
    data.authors.append(author_string)

def parse_geodata(institution, data):
    """
        :param institution: - Institution object to check for geodata
        :param data: - partially full Data object
        :returns bool: - True if successfully added coordinates 
    """
    if not institution: return False, 'NA'

    display_name = institution['display_name']
    if 'latitude' in institution['geo']:
        lat = institution['geo']['latitude']
        long = institution['geo']['longitude']
        data.latitudes.append(lat)
        data.longitudes.append(long)
    else:
        info("Geo information unavailable for " + display_name)
        return False, display_name
   

def alternate_geodata(id, data):
    """
        :param authorship: string id of Author to check for most recent institution's geodata
        :param data: partially full Data object    
        :return bool: returns True if successfully found institution/location info to Data
    """
    if not id: return False
    url =  "https://api.openalex.org/authors/" + id
    author = util.api_request(url)
    if not author: return False, 'NA'

    if author['last_known_institution']:
        institution_id = author['last_known_institution']['id']
        mapped, name = parse_geodata(institution_id, data)
        info("adding last known institution " + name)
        return mapped, "last known: " + name
    else:
        info("Last known institution unavailable.")
        return False, 'NA'