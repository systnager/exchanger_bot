from datetime import datetime
from database import update_item


def is_numeric(value):
    try:
        float(value)
    except ValueError:
        return False
    return True


def is_card_number_valid(card_number):
    if len(card_number) == 16:
        try:
            int(card_number)
        except ValueError:
            return False
    return True


def print_log(log_text):
    print(f'{datetime.now()} {log_text}')


def set_payeer_usd_to_uah_course(course):
    if is_numeric(course):
        update_item('settings', ['payeer_usd_to_uah'], [course], ['id'], [1])
    else:
        raise ValueError('Course must to be numeric')


def set_payeer_account(payeer_account):
    update_item('settings', ['payeer_account'], [payeer_account], ['id'], [1])
