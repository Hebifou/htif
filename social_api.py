import requests

def fetch_instagram_comments(post_id: str, api_key: str, limit=100):
    """
    Kommentare von Instagram über Graph API holen.
    api_key ist der Access Token des Kunden.
    """
    url = f"https://graph.facebook.com/v16.0/{post_id}/comments"
    params = {
        "access_token": api_key,
        "limit": limit,
        "fields": "id,text,timestamp,username"
    }
    comments = []
    while url and len(comments) < limit:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Instagram API Error: {response.status_code} - {response.text}")
        data = response.json()
        for comment in data.get("data", []):
            comments.append({
                "id": comment.get("id"),
                "text": comment.get("text"),
                "timestamp": comment.get("timestamp"),
                "username": comment.get("username", "")
            })
            if len(comments) >= limit:
                break
        url = data.get("paging", {}).get("next")
        params = {}  # Nur initial params beim ersten Request

    return comments[:limit]


def fetch_tiktok_comments(video_id: str, api_key: str, limit=100):
    """
    TikTok Business API Beispiel. api_key muss entsprechend angepasst werden.
    """
    url = f"https://business-api.tiktok.com/open_api/v1.2/comment/list/"
    headers = {
        "Access-Token": api_key,
        "Content-Type": "application/json"
    }
    params = {
        "video_id": video_id,
        "page_size": limit,
        "cursor": 0
    }
    comments = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"TikTok API Error: {response.status_code} - {response.text}")
        data = response.json()
        comment_list = data.get("data", {}).get("comments", [])
        for comment in comment_list:
            comments.append({
                "id": comment.get("cid"),
                "text": comment.get("text"),
                "timestamp": comment.get("create_time"),
                "username": comment.get("user", {}).get("nickname", "")
            })
        if len(comments) >= limit or not data.get("data", {}).get("has_more"):
            break
        params["cursor"] = data.get("data", {}).get("cursor", 0)
    return comments[:limit]
