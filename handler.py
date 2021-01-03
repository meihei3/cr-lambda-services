import json
import os
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, List

CR_BASE_URL = 'https://proxy.royaleapi.dev/v1'
LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"

CR_ACCESS_KEY = os.environ['CR_ACCESS_KEY']
LINE_NOTIFY_ACCESS_TOKEN = os.environ['LINE_NOTIFY_ACCESS_TOKEN']


def init_headers(api_key: str) -> Dict[str, str]:
    """
    初期化されたヘッダー情報の辞書を返す

    Args:
        api_key (str): API Key (Token)

    Returns
        dict: header情報
    """
    return {
        'authorization': f'Bearer {api_key}',
    }


def get_member(clan_tag: str) -> Dict[str, str]:
    """
    クラロワAPIからclan_tagのメンバー情報をGETする

    Args:
        clan_tag (str): クランタグ (ex. #228UCY92)

    Returns:
        dict: APIのレスポンス
    """
    clan_tag = clan_tag.replace('#', '%23')
    url = CR_BASE_URL + f'/clans/{clan_tag}/members'
    headers = init_headers(CR_ACCESS_KEY)

    res = requests.get(url, headers=headers)

    return res.json()


def last_seen_to_datetime(last_seen: str) -> datetime:
    """
    last_seenの記法からdatetime型に変換する

    Args:
        last_seen (str): クランメンバーの最終ログイン

    Returns:
        datetime: datetime型のlast_seen
    """
    return datetime.strptime(last_seen, '%Y%m%dT%H%M%S.000Z').astimezone(timezone.utc)


def filter_by_last_seen(items: List[dict], dead_line: datetime) -> List[dict]:
    """
    最終ログインがdead_lineのクラメンの情報を抽出する

    Args:
        items (List[dict])  : クランメンバーの情報のリスト
        dead_line (datetime): 最終ログインのデッドライン

    Returns:
        List[dict]: dead_lineを超えてしまったクラメンの情報のリスト
    """
    before_last_seen = lambda i: last_seen_to_datetime(i['lastSeen']) < dead_line

    return [item for item in items if before_last_seen(item)]


def generate_message(cr_items: List[dict]) -> str:
    """
    Line Notify送信用のメッセージを作成する

    Args:
        items (List[dict]): クランメンバーの情報のリスト

    Returns:
        str: 送信用のメッセージ
    """
    message = ''
    for member in cr_items:
        last_seen_diff = str(datetime.now(timezone.utc) - last_seen_to_datetime(member['lastSeen'])).split('.')[0]
        message += f'\n{member["name"]}: {last_seen_diff}'

    return message


def send_line(message: str):
    """
    Line Notifyに送信する

    Args:
        message (str): 送信用のメッセージ
    """
    headers = init_headers(LINE_NOTIFY_ACCESS_TOKEN)
    data = {'message': message}

    requests.post(LINE_NOTIFY_URL, data=data, headers=headers)


def lambda_function(event, context) -> Dict[str, str]:
    """
    実行用の関数

    Args:
        event (list)  : 入力パラメータ
        context (list): よくわからん

    Returns:
        dict: 結果
    """
    data = get_member('#228UCY92')
    dead_line = datetime.now(timezone.utc) - timedelta(days=5)
    filtered_data = filter_by_last_seen(data['items'], dead_line)

    if (filtered_data):
        message = generate_message(filtered_data)
        send_line(message)

    return f'ok: {len(filtered_data)}件取得しました'
