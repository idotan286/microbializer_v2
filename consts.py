import os

LOCAL = False
CAN_SUBMIT_NEW_JOBS = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSERVER_LOCAL_OUTPUTS = os.path.join(BASE_DIR, 'local_run')

MICROBIALIZER_PIPELINE_LOCAL_PATH = r'C:\repos\microbializer'
MICROBIALIZER_PIPELINE_LOCAL_FLASK_PATH = os.path.join(MICROBIALIZER_PIPELINE_LOCAL_PATH, 'pipeline', 'flask')
MICROBIALIZER_LOCAL_GALLERY_PATH = os.path.join(MICROBIALIZER_PIPELINE_LOCAL_PATH, 'gallery')
MICROBIALIZER_LOCAL_USER_RESULTS = os.path.join(WEBSERVER_LOCAL_OUTPUTS, 'user_results')

ARG_DISPLAY_JOB_NAME = 'Job name'
ARG_DISPLAY_EMAIL = 'Email address'
ARG_DISPLAY_INPUTS_FASTA_TYPE = 'Input FASTA files type'
ARG_DISPLAY_FILTER_OUT_PLASMIDS = 'Filter out contigs / orfs of plasmids'
ARG_DISPLAY_IDENTITY_CUTOFF = 'Minimum sequence identity (protein-level) for homologs detection'
ARG_DISPLAY_COVERAGE_CUTOFF = 'Minimum sequence coverage (protein-level) for homologs detection'
ARG_DISPLAY_CORE_MINIMAL_PERCENTAGE = 'Minimum percent of strains required to consider an orthogroup as part of the core genome'
ARG_DISPLAY_OUTGROUP = 'Root the species tree according to this outgroup'
ARG_DISPLAY_BOOTSTRAP = 'Apply bootstrap over the species tree'
ARG_DISPLAY_ADD_ORPHAN_GENES_TO_OGS = 'Add orphan genes to orthogroups table'


ARG_NAME_IN_PIPELINE_TO_DISPLAY = {
    'job_name': ARG_DISPLAY_JOB_NAME,
    'email': ARG_DISPLAY_EMAIL,
    'inputs_fasta_type': ARG_DISPLAY_INPUTS_FASTA_TYPE,
    'filter_out_plasmids': ARG_DISPLAY_FILTER_OUT_PLASMIDS,
    'identity_cutoff': ARG_DISPLAY_IDENTITY_CUTOFF,
    'coverage_cutoff': ARG_DISPLAY_COVERAGE_CUTOFF,
    'core_minimal_percentage': ARG_DISPLAY_CORE_MINIMAL_PERCENTAGE,
    'outgroup': ARG_DISPLAY_OUTGROUP,
    'bootstrap': ARG_DISPLAY_BOOTSTRAP,
    'add_orphan_genes_to_ogs': ARG_DISPLAY_ADD_ORPHAN_GENES_TO_OGS,
}
