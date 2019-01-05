import hmac
import json
import os
import uuid
from base64 import encodebytes
from datetime import datetime
from hashlib import sha1
from urllib.error import HTTPError
from urllib.parse import urlencode, quote_plus
from urllib.request import urlopen


def log(*args, **kwargs):
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ":", *args, *kwargs)


def get_ip_address():
    url = 'http://members.3322.org/dyndns/getip'
    try:
        res = urlopen(url)
        body = res.read().decode().strip()
        return body
    except RuntimeError as e:
        log("获取公网ip失败:", e.args)
        return None


def get_domain_record():
    params = {
        "Action": "DescribeSubDomainRecords",
        "SubDomain": os.getenv("DOMAIN"),
    }
    signed_params = get_signed_params("GET", params)
    url = "http://alidns.aliyuncs.com/?" + urlencode(signed_params)
    try:
        res = json.loads(urlopen(url).read().decode())
        if res["TotalCount"] == 0:
            return None
        return res["DomainRecords"]["Record"][0]
    except RuntimeError as e:
        log("获取域名解析失败:", e)


def update_domain_record(record):
    params = {
        "Action": "UpdateDomainRecord",
        "RecordId": record["RecordId"],
        "RR": record["RR"],
        "Type": record["Type"],
        "Value": record["Value"]
    }
    signed_params = get_signed_params("GET", params)
    url = "http://alidns.aliyuncs.com/?" + urlencode(signed_params)
    try:
        urlopen(url)
        log("更新域名解析成功!")
    except HTTPError as e:
        log("更新域名解析失败:", e)


def add_domain_record(record):
    params = {
        "Action": "AddDomainRecord",
        "DomainName": record["DomainName"],
        "RR": record["RR"],
        "Type": record["Type"],
        "Value": record["Value"]
    }
    signed_params = get_signed_params("GET", params)
    url = "http://alidns.aliyuncs.com/?" + urlencode(signed_params)
    try:
        urlopen(url)
        log("添加域名解析成功!")
    except HTTPError as e:
        log("添加域名解析失败:", e)


def get_common_params():
    """
    获取公共参数
    参考文档：https://help.aliyun.com/document_detail/29745.html?spm=5176.doc29776.6.588.sYhLJ0
    """
    return {
        'Format': 'JSON',
        'Version': '2015-01-09',
        'AccessKeyId': os.getenv('ACCESS_KEY'),
        'SignatureMethod': 'HMAC-SHA1',
        'Timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'SignatureVersion': '1.0',
        'SignatureNonce': uuid.uuid4()
    }


def get_signed_params(http_method, params):
    """
    参考文档：https://help.aliyun.com/document_detail/29747.html?spm=5176.doc29745.2.1.V2tmbU
    """
    # 1、合并参数，不包括Signature
    params.update(get_common_params())
    # 2、按照参数的字典顺序排序
    sorted_params = sorted(params.items())
    # 3、encode 参数
    query_params = urlencode(sorted_params)
    # 4、构造需要签名的字符串
    str_to_sign = "&".join([http_method, quote_plus("/"), quote_plus(query_params)])
    # 5、计算签名
    h = hmac.new((os.getenv('ACCESS_SECRET') + '&').encode('ASCII'), str_to_sign.encode('ASCII'), sha1)
    signature = encodebytes(h.digest()).strip()
    # 6、将签名加入参数中
    params['Signature'] = signature
    return params


def main():
    # 获取当前公网ip地址
    address = get_ip_address()
    # 获取当前解析配置
    record = get_domain_record()
    if record is not None:
        if record["Value"] != address:
            record["Value"] = address
            log("更新域名解析IP地址为:", address)
            update_domain_record(record)
        else:
            log("当前IP地址有效:", address)
    else:
        domains = os.getenv("DOMAIN").split(".")
        record = {
            "DomainName": ".".join(domains[1:]),
            "RR": domains[0],
            "Type": "A",
            "Value": address
        }
        log("添加域名解析IP地址:", address)
        add_domain_record(record)


if __name__ == '__main__':
    main()
