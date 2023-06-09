# Work in progress: Diversity in The Pile

Current functionality: 
- Writes a CSV file of all authors, titles, and affiliated institutions of the Works in a source
- Maps the locations of institutions with which authors published in the journal are affiliated

**Note:** Cannot parse more than 10,000 Works at a time due to OpenAlex limits

*example to generate maps of publications in Gesta, a leading peer-reviewed journal in art history, starting in 1999:*
    
    python journalDiversity.py your-email@gmail.com gesta -m --start_year 1999

## Use Instructions

In terminal and from directory `the-pile-diversity`

### 0. For first time set-up, build the conda environment to access the necessary packages:
<!--- Make code --->
     conda env create -f journal-diversity.yml

### 1. Activate the environment:
<!--- Make code --->
    conda activate journal-diversity

### 2. Run the program:

#### use in terminal:
<!--- Make code --->
    cd src
    python journalDiversity.py email journal_name 
        [-h] [-v] [-c] [-a] [-m] [-r] [--start_year START_YEAR] [--end_year END_YEAR]
                           

#### positional arguments:
  `email`                   the reply-to email for OpenAlex API calls

  `journal_name`            name of journal or source to search for


#### options:

  `-h`, `--help`            show this help message and exit

  `-v`, `--verbose`         include to print progress messages

  `-c`, `--write_csv`       include to write csv of data

  `-m`, `--write_maps`      include to plot locations of affiliated institutions
  
  `-a`, `--write_abstracts`
                            include to write abstracts of all works to csv

  `--start_year START_YEAR` 
                            filter publications by this earliest year (inclusive)

  `--end_year END_YEAR`     filter publications by this latest year (inclusive)

  `-r`, `--restore_saved`   include to display saved/pickled data from last run


### Citations
The Pile:

    Gao, L., Biderman, S., Black, S., Golding, L., Hoppe, T., Foster, C., … Leahy, C. (2020). The Pile: An 800GB Dataset of Diverse Text for Language Modeling. ArXiv [Cs.CL]. Retrieved from http://arxiv.org/abs/2101.00027

OpenAlex:

    Priem, J., Piwowar, H., & Orr, R. (2022). OpenAlex: A fully-open index of scholarly works, authors, venues, institutions, and concepts. ArXiv. https://arxiv.org/abs/2205.01833

PyGMT:

    Wessel, P., Luis, J. F., Uieda, L., Scharroo, R., Wobbe, F., Smith, W. H. F., & Tian, D. (2019). The Generic Mapping Tools version 6. Geochemistry, Geophysics, Geosystems, 20, 5556– 5564. https://doi.org/10.1029/2019GC008515

## To-Do

- add sampling functionality as an option to not try to deal with all data from the huge sources
    - how large of a sample is considered valid/rigorous enough?
- make protocol for what fields to query to get locations if they don't have the coordinates?
    ie get institution ID, else get last known institution (have implemented in gesta-diversity)
- Genderize API to get gender stats from list of authors
- swap print statements for progress bar
- alternate data visualizations: histogram by country for locations? once have gender, gender vs. country plot somehow?

<!--- NOTES --->
<!---- issn_l = "0016-920X" --->
<!---- source_query = "https://api.openalex.org/sources/" + args.id --->