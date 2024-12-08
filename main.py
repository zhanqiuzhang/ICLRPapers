import argparse
import os

import pandas as pd
from loguru import logger

from utils.fetcher import OpenReviewFetcher
from utils.file_util import read_jsonl, read_yaml, save_jsonl
from utils.processor import OpenReviewProcessor
from utils.translate import get_translation

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--config", type=str, default="config.yaml")
    args = argparser.parse_args()

    logger.info(f"Loading config from {args.config}")
    config = read_yaml(args.config)
    # 1. download papers
    year = config["year"]
    save_dir = config["save_dir"]
    logger.info(f"Downloading papers and reviews for {year} to {save_dir}")
    fetcher = OpenReviewFetcher("ICLR", year, batch_limit=1000, limit=-1)
    papers = fetcher.fetch_papers()
    logger.info(f"Downloaded {len(papers)} papers")
    save_jsonl(papers, os.path.join(save_dir, f"raw_paperlist_{year}.jsonl"))

    papers = list(read_jsonl(os.path.join(save_dir, f"raw_paperlist_{year}.jsonl")))
    processor = OpenReviewProcessor()
    df = processor.process_papers(papers)
    df.to_csv(os.path.join(save_dir, f"processed_paperlist_{year}.csv"), index=False)

    # 2. download reviews
    papers = pd.read_csv(os.path.join(save_dir, f"processed_paperlist_{year}.csv"))
    reviews = fetcher.fetch_reviews(papers["id"].tolist(), config.get("gateway", None))
    save_jsonl(reviews, os.path.join(save_dir, f"raw_paper_reviews_{year}.jsonl"))

    # 3. process reviews
    logger.info("Processing reviews...")
    reviews = []
    for review in read_jsonl(os.path.join(save_dir, f"raw_paper_reviews_{year}.jsonl")):
        rsp = processor.process_review(review)
        if rsp:
            reviews.append(rsp)

    df = pd.DataFrame(reviews)
    df.sort_values(by=["avg_rating", "std_dev"], ascending=[False, True], inplace=True)
    df.to_csv(os.path.join(save_dir, f"processed_paper_reviews_{year}.csv"), index=False)

    # 4. translation
    get_translation(
        os.path.join(save_dir, f"processed_paper_reviews_{year}.csv"),
        os.path.join(save_dir, f"paper_reviews_with_translation_{year}.csv"),
        config["llm"],
    )
