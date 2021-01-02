import re
from datetime import datetime, timedelta

from utils.database.models import Models
from utils.vk_utils import get_user_name

money_shorts = ['', 'тыс.', 'млн.', 'млрд.', 'трлн.']


def humanize_money(money, sep="'") -> str:
    before = str(int(money))
    money = str(float(money)).split('.')
    after = None
    if len(money) == 2 and money[1] != '0':
        before, after = money

    out, i = '', 0
    for d in before[::-1]:
        out += d
        i += 1
        if i % 3 == 0 and i < len(before):
            out += sep
    return out[::-1] if not after else f'{out[::-1]}.{after}'


def short_money(money, shorts=None) -> (str, bool):
    if shorts is None:
        shorts = money_shorts

    before = str(money)
    money = before.split('.')
    if len(money) == 2:
        before, _ = money

    if len(before) <= 3:
        return money, False

    separated_money = humanize_money(before).split(sep="'")
    if len(separated_money) > len(shorts):
        return '.'.join(money), False

    return f'{separated_money[0]} {shorts[len(separated_money) - 1]}', True


def humanize_and_short_money(money, valute='¥', sep="'", shorts=None) -> str:
    humanize = humanize_money(money, sep)
    short, shorted = short_money(money, shorts)

    if shorted:
        return f'{humanize}{valute} ({short})'
    else:
        return f'{humanize}{valute}'


def count_level(exp: int) -> [int, int]:
    level = 1
    while True:
        level_exp = (level ** 2) * ((level - 1) ** 2) * 2
        if exp < level_exp:
            return level_exp - exp, level - 1
        level += 1


def get_or_create_user(id, api) -> Models.user:
    if id <= 0:
        return None
    try:
        user = Models.user.get(user_id=id)
    except Models.user.DoesNotExist:
        user = Models.user.create(user_id=id, name=get_user_name(id, api),
                                  work_time=datetime.now() - timedelta(minutes=10),
                                  income_time=datetime.now() - timedelta(hours=1),
                                  auto=0, business=0, maid=0, miner=0, work=1)

    return user


def get_times_of_day(variants: (list, set, frozenset)):
    """ Returns string depending about time
    :param variants: a massive with times (Night, Morning, Day, Evening)
    :return: string depending about time
    """
    hours = datetime.now().hour
    if hours in range(0, 6):
        return variants[0]
    elif hours in range(6, 12):
        return variants[1]
    elif hours in range(12, 18):
        return variants[2]
    elif hours in range(18, 24):
        return variants[3]


def get_user_or_none(id):
    try:
        return Models.user.get(user_id=id)
    except Models.user.DoesNotExist:
        return None


def chunk_array(array, chunk_number) -> list:
    if len(array) <= chunk_number:
        return [array]
    out, tmp, index = [], [], 0
    for el in array:
        tmp.append(el)
        index += 1
        if index == chunk_number:
            out.append(tmp)
            tmp = []
            index = 0
    out.append(tmp)
    return out


def parse_attachments(attachments) -> tuple:
    out = []
    for attach in attachments:
        t = attach['type']
        if t == 'wall':
            out.append(f'{t}{attach[t]["from_id"]}_{attach[t]["id"]}')
        else:
            out.append(f'{t}{attach[t]["owner_id"]}_{attach[t]["id"]}')
    return tuple(out)


def parse_mention(mention: (str, None)) -> int:
    if not mention:
        return 0
    reg = r'\[id(\d+)\|.+\]'
    match = re.match(reg, mention)
    if not match:
        return 0
    return int(match.group(1))


def get_user_sex(user_id, api):
    query = api.users.get(user_ids=user_id, fields='sex')
    return query[0]['sex'] if len(query) > 0 else 2
