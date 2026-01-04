import httpx
from bs4 import BeautifulSoup, Tag
import re
from markdownify import markdownify as md
import json

BASE_URL = "https://www.schulportal.sachsen.de/lplandb/index.php"
PLANS = {
    "deutsch": {"id": "908", "sc": "1tblk6cNNahu0dAWKRuO"},
    "mathe": {"id": "912", "sc": "Mpk0iAibe4ONjV3PndYR"},
    "englisch": {"id": "91", "sc": "O6Em8mw3wB7reJu01rO2"},
    "sachunterricht": {"id": "80", "sc": "2DYw4je6s74vCaxRHqx6"},
}


def _get_cover_page(soup: Tag) -> str:
    cover_page = soup.find(
        "div", class_="lplanpage", attrs={"data-ci": "Deckblatt"}
    ).text.strip()
    return re.sub(r"\s+", " ", cover_page)


def _get_impressum(soup: Tag) -> str:
    impressum = soup.find(
        "div", class_="lplanpage", attrs={"data-ci": "Impressum"}
    ).text.strip()
    return re.sub(r"\s+", " ", impressum)


def _get_content_ids(soup: Tag) -> list[str]:
    toc = soup.find("div", class_="inhaltsverzeichnis")
    toc = toc.find("div", class_="ivblock", recursive=False)

    items = toc.find_all("div", class_="ivitem", recursive=False)
    return [item.text.strip() for item in items]


def _remove_links(html_tag: Tag) -> str:
    for link in html_tag.find_all("a"):
        link.unwrap()
    return html_tag


def _get_toc(content: dict) -> dict[int, str]:
    toc = {}
    for key, value in content.items():
        if value["section"] not in toc:
            toc[value["section"]] = {key: value["title"]}
        else:
            toc[value["section"]][key] = value["title"]
    return toc


def _get_content(soup: Tag, content_ids: list[str]) -> dict[int, str]:
    content_dict = {}
    idx = 0

    for content_id in content_ids:
        content = soup.find("div", class_="lplanpage", attrs={"data-ci": content_id})
        sub_content = content.find("div", class_="childItems")

        for item in sub_content.find_all(recursive=False):
            category = item.attrs.get("data-ci")
            content_dict[idx] = {
                "title": category,
                "section": content_id,
                "content": [],
            }

            cleaned_html = _remove_links(item)
            content_dict[idx]["content"] = md(cleaned_html.prettify())
            idx += 1

    return content_dict


def parse_plan(subject: str) -> dict:
    ids = PLANS[subject]

    url = f"{BASE_URL}?lplanid={ids['id']}&lplansc={ids['sc']}"

    response = httpx.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    plan = soup.find("div", class_="lplancontent")

    content_ids = _get_content_ids(plan)
    content = _get_content(plan, content_ids)

    toc = _get_toc(content)
    return {
        "cover_page": _get_cover_page(plan),
        "impressum": _get_impressum(plan),
        "table_of_contents": toc,
        "content": content,
    }


def main():
    all_plans = {
        "deutsch": parse_plan("deutsch"),
        "mathe": parse_plan("mathe"),
        "englisch": parse_plan("englisch"),
        "sachunterricht": parse_plan("sachunterricht"),
    }

    with open("resources/data.json", "w") as f:
        json.dump(all_plans, f)


if __name__ == "__main__":
    main()
