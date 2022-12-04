import json


def convert_issue_to_faq(issue_file: str, faq_file: str):
    with open(issue_file, 'r', encoding='utf-8') as f:
        issue = json.load(f)
    
    faqs = []
    for key, value in issue.items():
        faqs.append({
            "number": key,
            "title": value['title'],
            "url": value['url']
        })
    
    with open(faq_file, 'w', encoding='utf-8') as f:
        json.dump(faqs, f, ensure_ascii=False)


if __name__ == "__main__":
    convert_issue_to_faq(
        "/Users/wujingjing05/projects/self/py-osschat/.wechaty/SyncGithubIssuePlugin/setting.json",
        "/Users/wujingjing05/projects/self/py-osschat/data/faq.json"
    )