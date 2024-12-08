import concurrent
import json
import re

import pandas as pd
from loguru import logger
from openai import OpenAI
from tqdm import tqdm

global client
global MODEL
global SYSTEM_PROMPT

PROMPT = """你是一个专业的学术论文阅读助手，请你根据给定的论文题目和摘要，给出题目和摘要的中文翻译，并用3~5个关键词概括该论文。
你需要以json格式输出：```json\n{{"中文题目": "xxx", "中文摘要": "xxx:, "关键词": ["xxx", "xxx", "xxx",...]}}\n```
题目和摘要的中文翻译中不要添加任何换行，如果题目和摘要中需要添加引号，那么需要使用中文引号“”。

给定的论文题目是：{title}
给定的摘要是：{abstract}"""


def parse_json_string(json_string):
    try:
        pattern_json = r"```json\n(.*?)\n```"
        matched = re.search(pattern_json, json_string, re.DOTALL)

        if matched:
            string = matched.group(1).strip()
            # 将除了 \n 以外的 \ 转换为 \\
            pattern_slash = r"\\(?!n)"
            result_slash = re.sub(pattern_slash, r"\\\\", string)

            # 去掉 latex 公式中可能存在的 \
            return json.loads(result_slash.replace('\\"', ""))
    except Exception as e:
        logger.error('"' + result_slash + '"')
        logger.error(f"Error parsing json string: {e}")
        return None


def run_llm(paper_row):
    global client
    global MODEL
    global SYSTEM_PROMPT

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": PROMPT.format(
                        title=paper_row["title"],
                        abstract=paper_row["abstract"],
                    ),
                },
            ],
        )

        summary = completion.choices[0].message.content
        return parse_json_string(summary)
    except Exception as e:
        logger.error(f"Error generating summary: {e}")


def get_translation(review_path, save_path, llm_config):
    logger.info(f"Running LLM with config: {llm_config}")
    global client
    global SYSTEM_PROMPT
    global MODEL
    SYSTEM_PROMPT = llm_config["system_prompt"]
    client = OpenAI(base_url=llm_config["base_url"], api_key=llm_config["api_key"])
    MODEL = llm_config["model"]

    papers = pd.read_csv(review_path)

    all_rows = []
    results = []
    for i, paper_row in papers.iterrows():
        all_rows.append(paper_row)
    logger.info(f"Running LLM on {len(all_rows)} papers")

    with concurrent.futures.ThreadPoolExecutor(max_workers=llm_config["num_workers"]) as executor:
        futures = [executor.submit(run_llm, paper_row) for paper_row in all_rows]
        results = [future.result() for future in tqdm(futures)]

    title_zh = []
    abs_zh = []
    keywords = []
    for json_str in results:
        if json_str:
            title_zh.append('"' + json_str["中文题目"] + '"')
            abs_zh.append('"' + json_str["中文摘要"] + '"')
            keywords.append(json_str["关键词"])
        else:
            title_zh.append("")
            abs_zh.append("")
            keywords.append([])
    papers["title_zh"] = title_zh
    papers["abs_zh"] = abs_zh
    papers["keywords"] = keywords

    logger.info(f"Saving translated papers to {save_path}")
    papers.to_csv(save_path, index=False)
