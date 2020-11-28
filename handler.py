import json
import os
import requests
from typing import Dict


BASE_URL = 'https://api.clashroyale.com/v1'
ACCESS_KEY = os.environ['CR_ACCESS_KEY']


def init_headers() -> Dict[str, str]:
    """
    初期化されたヘッダー情報の辞書を返す

    Returns
    -------
    dict
        header情報
    """
    return {
        'content-type': 'application/json; charset=utf-8',
        'cache-control': 'max-age=60',
        'authorization': f'Bearer {ACCESS_KEY}',
    }


def get_member(clan_tag: str) -> Dict[str, str]:
    """
    クラロワAPIからclan_tagのメンバー情報をGETする

    Parameters
    ----------
    clan_tag : str
        クランタグ (ex. #228UCY92)

    Returns
    -------
    dict
        APIのレスポンス
    """
    url = BASE_URL + f'/clans/{clan_tag}/members'
    headers = init_headers()

    res = requests.get(url, headers=headers)

    return res.json()


def lambda_function(event, context) -> Dict[str, str]:
    """
    実行用の関数

    Parameters
    ----------
    event : list
        入力パラメータ
    context : list
        よくわからん

    Returns
    -------
    data : dict
        結果
    """
    data = get_member('#228UCY92')

    return data
