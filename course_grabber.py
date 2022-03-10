import re
import sqlite3


def main():
    html_file = 'courses.html'
    split_line = '<!-- https://docs.djangoproject.com/en/3.0/ref/templates/builtins/#autoescape -->'
    with open(html_file, 'r') as f:
        text = [line.strip() for line in f.read().split('\n') if len(line)]

    for idx, line in enumerate(text):
        if line == split_line:
            # Need to change match process to use included comments in courses.html
            hall_room_str = re.match('<td[^>]*>(.*?)</td>', text[idx+12]).group(1)
            hall = '' if hall_room_str == 'None' else hall_room_str.split(' - ')[0]
            room = -1 if hall_room_str == 'None' else hall_room_str.split(' - ')[0][3:]
            start_time = -1
            end_time = -1


if __name__ == '__main__':
    main()
