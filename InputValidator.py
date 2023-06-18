from Bio import SeqIO, Entrez
import gzip
import shutil
from urllib.error import HTTPError


class InputValidator:
    """
    A class validate the inputs.

    ...

    Attributes
    ----------
    

    Methods
    -------
    implemented below
    """
    def __is_fasta(self, file_path):
        """the function verify if the file is Fasta (not only the name but also the content)
        
        Parameters
        ----------
        file_path: str
            the path to the file

        Returns
        -------
        is_fasta: bool
            True if fasta file, else False
        """
        with open(file_path, "r") as handle:
            fasta = SeqIO.parse(handle, "fasta")
            try:
                return any(fasta)
            except Exception as e:
                return False

    def __is_fastq(self, file_path):
        """the function verify if the file is Fastaq (not only the name but also the content)
        
        Parameters
        ----------
        file_path: str
            the path to the file

        Returns
        -------
        is_fastaq: bool
            True if fastaq file, else False
        """
        with open(file_path, "r") as handle:
            fastq = SeqIO.parse(handle, "fastq")

            try:
                return any(fastq)
            except Exception as e:
                return False

    def unzip_file(self, file_path):
        """this function unzip a gz file
        
        Parameters
        ----------
        file_path: str
            the path to the file

        Returns
        -------
        unzipped_file_path: str
            The path to the unzipped file
        """
        with gzip.open(file_path, 'rb') as f_in:
            unzipped_file_path = '.'.join(file_path.split('.')[:-1])
            with open(unzipped_file_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        return unzipped_file_path

    def validate_input_file(self, file2check):
        """this function validates the input file.
        It tests if the file is fasta or fastaq (if it's gz then it first unzip and then tests if fasta or fastaq)
        
        Parameters
        ----------
        file2check: str
            the path to the file

        Returns
        -------
        is_valid: bool
            True if the file is valid, else False
        """
        if file2check.endswith('.gz'): #unzip file
            file2check = self.unzip_file(file2check)
        
        if self.__is_fasta(file2check):
            return True
        elif self.__is_fastq(file2check):
            return True
        return False
        
    def valid_species(self, specie: str):
        #TODO complete
        """this function validates the if the specie name is valid
        
        Parameters
        ----------
        specie: str
            the specie name

        Returns
        -------
        True if valid, else False
        """
        try:
            handle = Entrez.efetch(db="nucleotide", id=specie, rettype="fasta", retmode="text")
        except HTTPError as e:
            print(e)
            return False
        return True
