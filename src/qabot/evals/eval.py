# run with : `uv run -m src.qabot.evals.eval`
# debug with `uv run -m pdb src.qabot.evals.eval`
import httpx
import pandas as pd
from pathlib import Path
import ast

from src.qabot.helpers.config import Config
from src.qabot.ingest.loader import DocumentLoader
from src.qabot.helpers.logger import get_custom_logger
from src.qabot.helpers.project_config import load_project_config
from src.qabot.helpers.logger import get_custom_logger



logger = get_custom_logger('eval_script')


def merge_all_documents(config):
    output_file = config['all_documents_dump']
    document_loader = DocumentLoader(config = config)
    files_paths = document_loader.find_files()
    logger.debug(f'Found data files paths with document_loader.find_files() : {files_paths}')
    all_document  = document_loader.load_files(files = files_paths)
    logger.info('Ingested documents by their paths into RAM')
    all_documents_dump = []
    for doc in all_document:
        print(doc.model_dump_json)
        all_documents_dump.append(doc.model_dump_json)
        
    output_file.write_text(str(all_documents_dump))
    logger.debug(f'Documents saved to: {output_file}')
   
def evaluate(config, project_config):
    logger.info('evaluate() function starting execution')
    logger.debug(f'evaluate() function execution Path.cwd() :{Path.cwd()}')
    logger.info('Oppening questions samples with golden path with pandas...')
    questions = pd.read_csv(config['questions'], sep=';')
    questions['golden_path'] = questions['golden_path'].apply(ast.literal_eval)
    logger.debug(f'Questions from questions.csv: {questions}')
    precision_at_k = 0
    recall_at_k = 0
    test_frame_len = questions.shape[0]
    retrieving_depth = project_config['retriever']['k']
    ASK_ENDPOINT = project_config['web']['frontend']['backend_host'] + '/ask'
    for n,row in questions.iterrows():
        question = row['question']
        golden_path = row['golden_path']
        response = httpx.post(
            ASK_ENDPOINT,
            json = {
            'question':question,
            'history_summary':"",
            'session_id': "25eddaa8-c177-49ac-8297-464422c872db",
            'last_turns':[]
            },
            timeout=project_config['evals']['request_timeout']
        )
        #breakpoint()
        sources = [source['path'] for source in response.json()['sources']]

        
        logger.debug(f'\n\n\n SOURCES FROM RESPONSE: \n\n\n{type(sources)}' )
        logger.debug(f'\n\n\n all_sources_paths: \n\n\n {sources}')
        logger.debug(f'\n\n\nGOLDEN PATH: {golden_path}')
        logger.debug(f'\n\n\n')
        logger.debug(f'Server status on sent request: {response}')
        logger.debug(f'Response on test questions : {response.json()}')

        precision, recall = precision_recall_at_k(sources, golden_path)
        precision_at_k +=precision
        recall_at_k+=recall
        logger.debug(f"For {n} question:\n")
        logger.debug(f"Current question Precision@{retrieving_depth} = {precision:.2f}")
        logger.debug(f"Current question Recall@{retrieving_depth} = {recall:.2f}")
    precision_at_k = precision_at_k / test_frame_len
    recall_at_k = recall_at_k / test_frame_len
    logger.info(f'Overal Precision@{retrieving_depth} : {precision_at_k}')
    logger.info(f'Overal Recall@{retrieving_depth} : {recall_at_k} ')

        
def precision_recall_at_k(all_sources_paths, golden_path):
    retrieved = all_sources_paths
    relevant = golden_path

    retrieved_set = set(retrieved)
    relevant_set = set(relevant)
    #breakpoint()
    intersection = retrieved_set.intersection(relevant_set)
    true_positives = len(intersection)

    precision = true_positives / len(retrieved) if retrieved else 0
    recall = true_positives / len(relevant) if relevant else 0

    return precision, recall

    
if __name__ == '__main__':
   #merge_all_documents()
   config = Config()
   project_config = load_project_config()
   evaluate(config = config, project_config= project_config)

