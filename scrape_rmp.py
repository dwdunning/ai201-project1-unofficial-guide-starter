"""
Rate My Professors scraper via the site's internal GraphQL API.

Endpoint:  https://www.ratemyprofessors.com/graphql
Auth:      none required (the site serves unauthenticated queries)
ID scheme: GraphQL global IDs are base64("Teacher-{legacyId}")

Usage:
    python scrape_rmp.py
    python scrape_rmp.py --output-dir data/rmp
"""

import argparse
import base64
import json
import time
from pathlib import Path

import requests

GRAPHQL_URL = "https://www.ratemyprofessors.com/graphql"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ),
    "Content-Type": "application/json",
    "Referer": "https://www.ratemyprofessors.com/",
}

# Professors to scrape: (name, legacy_id from the URL)
PROFESSORS = [
    ("Mark Gondree",     2222240),
    ("Lynn Stauffer",    62597),
    ("Ali Kooshesh",     62598),
    ("Suzanne Rivoire",  1213020),
    ("Gurman Gill",      2083075),
    ("B. Ravikumar",     62601),
    ("Tia Watts",        62602),
    ("Glenn Carter",     25142),
    ("Shubbhi Taneja",   2484473),
    ("Anamary Leal",     2409598),
]

TEACHER_INFO_QUERY = """
query TeacherInfoQuery($id: ID!) {
  node(id: $id) {
    __typename
    ... on Teacher {
      id
      legacyId
      firstName
      lastName
      department
      school {
        id
        legacyId
        name
        city
        state
        country
      }
      numRatings
      avgRating
      avgDifficulty
      wouldTakeAgainPercent
      mandatoryAttendance {
        yes
        no
        neither
        total
      }
      ratingsDistribution {
        r1
        r2
        r3
        r4
        r5
        total
      }
    }
  }
}
"""

RATINGS_LIST_QUERY = """
query RatingsListQuery($count: Int!, $id: ID!, $courseFilter: String, $cursor: String) {
  node(id: $id) {
    __typename
    ... on Teacher {
      ratings(first: $count, after: $cursor, courseFilter: $courseFilter) {
        edges {
          cursor
          node {
            id
            legacyId
            comment
            date
            class
            difficultyRating
            helpfulRating
            isForOnlineClass
            isForCredit
            grade
            thumbsUpTotal
            thumbsDownTotal
            wouldTakeAgain
            ratingTags
            attendanceMandatory
            textbookUse
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}
"""


def encode_id(legacy_id: int) -> str:
    return base64.b64encode(f"Teacher-{legacy_id}".encode()).decode()


def gql(query: str, variables: dict, session: requests.Session) -> dict:
    resp = session.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def fetch_teacher_info(gql_id: str, session: requests.Session) -> dict:
    data = gql(TEACHER_INFO_QUERY, {"id": gql_id}, session)
    node = data.get("node")
    if not node or node.get("__typename") != "Teacher":
        raise ValueError(f"No Teacher node found for id={gql_id}")
    return node


def fetch_all_ratings(
    gql_id: str,
    session: requests.Session,
    page_size: int = 20,
    course_filter: str | None = None,
    delay: float = 0.5,
) -> list[dict]:
    ratings = []
    cursor = None

    while True:
        variables = {
            "count": page_size,
            "id": gql_id,
            "courseFilter": course_filter,
            "cursor": cursor,
        }
        data = gql(RATINGS_LIST_QUERY, variables, session)
        node = data.get("node", {})
        ratings_conn = node.get("ratings", {})
        edges = ratings_conn.get("edges", [])
        page_info = ratings_conn.get("pageInfo", {})

        for edge in edges:
            ratings.append(edge["node"])

        if not page_info.get("hasNextPage"):
            break

        cursor = page_info["endCursor"]
        time.sleep(delay)

    return ratings


def scrape_professor(name: str, legacy_id: int, session: requests.Session) -> dict:
    gql_id = encode_id(legacy_id)
    print(f"  Fetching info for {name} (legacyId={legacy_id}) ...")
    info = fetch_teacher_info(gql_id, session)

    num_ratings = info.get("numRatings", 0)
    print(f"  Fetching {num_ratings} ratings ...")
    ratings = fetch_all_ratings(gql_id, session)
    print(f"  Retrieved {len(ratings)} ratings.")

    return {
        "professor": info,
        "ratings": ratings,
    }


def main():
    parser = argparse.ArgumentParser(description="Scrape RateMyProfessors via GraphQL")
    parser.add_argument(
        "--output-dir",
        default="documents/rmp",
        help="Directory to write JSON files into (default: documents/rmp)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.75,
        help="Seconds to wait between paginated requests (default: 0.75)",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()

    for name, legacy_id in PROFESSORS:
        print(f"\n=== {name} ===")
        try:
            result = scrape_professor(name, legacy_id, session)
            safe_name = name.lower().replace(" ", "_").replace(".", "")
            out_path = out_dir / f"{safe_name}_{legacy_id}.json"
            out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
            print(f"  Saved -> {out_path}")
        except Exception as exc:
            print(f"  ERROR: {exc}")

        time.sleep(args.delay)

    print("\nDone.")


if __name__ == "__main__":
    main()
