import statistics

import pandas as pd
from loguru import logger


class OpenReviewProcessor:
    @staticmethod
    def process_papers(papers):
        df = pd.json_normalize(papers)
        filtered_df = df[
            [
                "id",
                "content.title.value",
                "content.abstract.value",
                "content.primary_area.value",
                "content.keywords.value",
                "content.TLDR.value",
            ]
        ]
        filtered_df.columns = ["id", "title", "abstract", "primary_area", "keywords", "tldr"]
        return filtered_df

    @staticmethod
    def process_review(review):
        paper_id = None
        title = ""
        paper_ratings = []
        abstract = None

        for note in review["notes"]:
            if "abstract" in note["content"]:
                title = note["content"]["title"]["value"]
                paper_id = note["id"]
                abstract = '"' + note["content"]["abstract"]["value"] + '"'
            elif "rating" in note["content"]:
                rating = int(note["content"]["rating"]["value"])
                paper_ratings.append(rating)

        if not abstract:
            logger.warning(f"No abstract found for paper {paper_id}")
            return None
        if paper_ratings:
            avg_rating = sum(paper_ratings) / len(paper_ratings)
            std_dev = statistics.stdev(paper_ratings) if len(paper_ratings) > 1 else 0
        else:
            avg_rating = None
            std_dev = None

        return {"id": paper_id, "title": title, "avg_rating": avg_rating, "std_dev": std_dev, "ratings": paper_ratings, "abstract": abstract}
