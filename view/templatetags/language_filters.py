from django import template

register = template.Library()

LANGUAGE_MAP = {
    'eng': '英语',
    'chi': '中文',
    'spa': '西班牙语',
    'fre': '法语',
    'ger': '德语',
    'jpn': '日语',
    'rus': '俄语',
    'kor': '韩语',
    'ita': '意大利语',
    'por': '葡萄牙语',
    'ara': '阿拉伯语',
    'hin': '印地语',
    'tha': '泰语',
    'dut': '荷兰语',
    'swe': '瑞典语',
    # 继续添加其他语言
}

@register.filter
def readable_language(code):
    return LANGUAGE_MAP.get(code, code)
