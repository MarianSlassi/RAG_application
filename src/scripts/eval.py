# run with : `uv run -m src.qabot.evals.eval`
# debug with `uv run -m pdb src.qabot.evals.eval`
import os
import httpx
import pandas as pd
from pathlib import Path
import ast

from src.qabot.helpers.config import Config
from src.qabot.ingest.loader import DocumentLoader
from src.qabot.helpers.logger import get_custom_logger
from src.qabot.helpers.project_config import load_project_config
from src.qabot.helpers.logger import get_custom_logger
from src.qabot.llm.prompts import LLM_JUDGE_SYSTEM, LLM_JUDGE_USER
from src.qabot.llm.gateway import LLM

from src.qabot.search import Retriever
from src.qabot.indexer import Indexer

from dotenv import load_dotenv
from openai import OpenAI

logger = get_custom_logger('eval_script')

class llm_evaluator():
    def __init__(self, project_config):
        self.project_config = project_config or load_project_config()
        indexer = Indexer()
        index, chunks, model = indexer.load_index()
        self.retriever = Retriever(index=index, chunks=chunks, model=model)
        self.llm = LLM()

    def empirical_answer_evaluation(self, question, answer):
        retrieved = self.retriever.retrieve(query=question, k = self.project_config['retriever']['k'])
        prompt_sources = [{"text": chunk.text, "path": chunk.meta.path} for chunk, i in retrieved]
        system_prompt = LLM_JUDGE_SYSTEM
        user_prompt  = LLM_JUDGE_USER.format(question = question, answer = answer, context = prompt_sources)
        evaluation = self.llm.generate(user_prompt=user_prompt, system_prompt=system_prompt, structured= True)

        
        faithfulness = float(evaluation['faithfulness'])
        relevance = float(evaluation['relevance'])
        completeness = float(evaluation['completeness'])
        consisness = float(evaluation['conciseness'])
        overall_score = float(evaluation['overall_score'])
        comments = evaluation['comments']

        logger.debug(f"Current evaluation {evaluation}")
        logger.debug(f'\ntype(evaluation){type(evaluation)}')

        return faithfulness, relevance, completeness, consisness, overall_score, comments
        



    # сразу импелменитровать на структур аутпут
    # ретривить контекст


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
   
def evaluate(config, project_config, questions_num:int = 50):
    """
    Args:
        questions_num: specify number of questions which to call from file, default = 50. Uses slice inside, last value not included. 
    """
    logger.info(f'Starting evaluate() function for questions_num: {questions_num}')
    logger.info('evaluate() function starting execution')
    logger.debug(f'evaluate() function execution Path.cwd() :{Path.cwd()}')
    logger.info('Oppening questions samples with golden path with pandas...')
    questions = pd.read_csv(config['questions'], sep=';')
    #questions = questions[:questions_num]
    questions['golden_path'] = questions['golden_path'].apply(ast.literal_eval)
    logger.debug(f'Questions from questions.csv: {questions}')
    llm_eval = llm_evaluator(project_config = project_config)
    precision_at_1, recall_at_1, precision_at_3, recall_at_3, precision_at_5, recall_at_5 = (0,) *6
    faithfulness_total, relevance_total, completeness_total, consisness_total, overall_score_total, comments_total = (0,) * 6
    mrr_total = 0
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

        answer = response.json()['answer']
        
        logger.debug(f'\n\n\n SOURCES FROM RESPONSE: \n\n\n{(sources)}' )
        logger.debug(f'\n\n\nGOLDEN PATH: {golden_path}')
        logger.debug(f'\n\n\n')
        logger.debug(f'Server status on sent request: {response}')
        logger.debug(f'Response on test questions : {response.json()}')


        precision_1, recall_1 = precision_recall_at_k(sources, golden_path, 1)
        precision_at_1 +=precision_1
        recall_at_1 +=recall_1

        precision_3, recall_3 = precision_recall_at_k(sources, golden_path, 3)
        precision_at_3 += precision_3
        recall_at_3 += recall_3

        precision_5, recall_5 = precision_recall_at_k(sources, golden_path, 5)
        precision_at_5 += precision_5
        recall_at_5 += recall_5

        faithfulness, relevance, completeness, consisness, overall_score, comments = llm_eval.empirical_answer_evaluation(question = question, answer= answer)
        faithfulness_total += faithfulness
        relevance_total += relevance
        completeness_total += completeness
        consisness_total +=consisness
        overall_score_total += overall_score

        rr = reciprocal_rank(sources, golden_path)
        mrr_total += rr


        
        logger.debug(f"For {n} question:\n")
        
        logger.debug(f"Current question Precision@1 = {precision_1:.2f}")
        logger.debug(f"Current question Recall@1 = {recall_1:.2f}")
        logger.debug(f"Current question Precision@3 = {precision_3:.2f}")
        logger.debug(f"Current question Recall@3 = {recall_3:.2f}")
        logger.debug(f"Current question Precision@5 = {precision_5:.2f}")
        logger.debug(f"Current question Recall@5 = {recall_5:.2f}")

        logger.debug(f"Current question faithfulness: {faithfulness}")
        logger.debug(f"Current question relevance: {relevance}")
        logger.debug(f"Current question completeness: {completeness}")
        logger.debug(f"Current question consisness: {consisness}")
        logger.debug(f"Current question overall_score: {overall_score}")


    precision_at_1 /= test_frame_len
    recall_at_1 /= test_frame_len
    precision_at_3 /= test_frame_len
    recall_at_3 /= test_frame_len
    precision_at_5 /= test_frame_len
    recall_at_5 /= test_frame_len

    faithfulness_total /= test_frame_len
    relevance_total /= test_frame_len
    completeness_total /= test_frame_len
    consisness_total /= test_frame_len
    overall_score_total /= test_frame_len



    mrr_total /= test_frame_len
    logger.info(f'Overal Precision@1 : {precision_at_1}')
    logger.info(f'Overal Recall@1 : {recall_at_1} ')
    logger.info(f'Overal Precision@3 : {precision_at_3}')
    logger.info(f'Overal Recall@3 : {recall_at_3} ')
    logger.info(f'Overal Precision@5 : {precision_at_5}')
    logger.info(f'Overal Recall@5 : {recall_at_5} ')

    logger.info(f"faithfulness_total : {faithfulness_total}")
    logger.info(f"relevance_total : {relevance_total}")
    logger.info(f"completeness_total : {completeness_total}")
    logger.info(f"consisness_total : {consisness_total}")
    logger.info(f"overall_score_total : {overall_score_total}")


        
def precision_recall_at_k(retrieved, golden_path, k):
    # if len(retrieved) < k:
    #     raise ValueError(f"Number of retrieved sources has to be grater than 'k' for @k evaluation, current len(retrieved)={len(retrieved)}, k={k}")`
    retrieved = retrieved[:k]
    relevant = golden_path

    retrieved_set = set(retrieved)
    relevant_set = set(relevant)
    #breakpoint()
    intersection = retrieved_set.intersection(relevant_set)
    true_positives = len(intersection)

    precision = true_positives / len(retrieved) if retrieved else 0
    recall = true_positives / len(relevant) if relevant else 0

    return precision, recall

def reciprocal_rank(retrieved, relevant):
    for idx, doc in enumerate(retrieved, start=1):
        if doc in relevant:
            return 1 / idx
    return 0



    
if __name__ == '__main__':
   #merge_all_documents()
   config = Config()
   project_config = load_project_config()
   evaluate(config = config, project_config= project_config) # For script testing add parametr ,questions_num = 10 (for example)

