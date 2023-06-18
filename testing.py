from DbUtils.CustomDbCreator import KrakenCustomDbCreator
from pathlib import Path
if __name__ == "__main__":
    # a = {"outputFilePath": "/groups/pupko/alburquerque/example.fasta"}
    a = {"outputFilePath": "/groups/pupko/alburquerque/results.txt",
         "remove_only_high_level_res": True}

    b=KrakenCustomDbCreator.create_custom_db(user_unique_id="Testing", path_to_fasta_file=Path("/groups/pupko/alburquerque/merged.fasta"),
                                             list_of_accession_numbers=["AY851612", "NC_000913", "MG762674"])

    print('a')

    # SearchEngine.kraken_search("/groups/pupko/alburquerque/example.fasta", {})
    # b = process_output(**a)
    # run_post_process(root_folder="/groups/pupko/alburquerque/", classification_threshold=0.3,
    #                  species_to_filter_on=["Salmonella (taxid 590)", "Enterobacteriaceae (taxid 543)", 2220, 12])
    print('a')
