from datetime import datetime
import json


def is_numeric(value):
    try:
        float(value)
    except ValueError:
        return False
    return True


def is_card_number_valid(card_number):
    card_number = card_number.replace(' ', '')
    if len(card_number) == 16:
        try:
            int(card_number)
        except ValueError:
            return False
    else:
        return False
    return True


def print_log(*log_text):
    for log in log_text:
        print(f'{datetime.now()} {log}')


def save_config(config):
    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)


def get_config():
    with open("config.json", "r") as config_file:
        return json.load(config_file)


def set_payeer_usd_to_uah_course(course):
    config = get_config()
    config["payeer_usd_to_uah"] = course
    save_config(config)


def set_advcash_usd_to_uah_course(course):
    config = get_config()
    config["advcash_usd_to_uah"] = course
    save_config(config)


def set_payeer_account(payeer_account):
    config = get_config()
    config["payeer_account"] = payeer_account
    save_config(config)


def set_advcash_account(advcash_account):
    config = get_config()
    config["advcash_account"] = advcash_account
    save_config(config)
