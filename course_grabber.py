import re
import sqlite3
from sqlite3 import Error


def create_connection(path: str) -> sqlite3.Connection:
    try:
        connection = sqlite3.connect(path)
        return connection
    except Error as e:
        print(f"The error '{e}' occurred.")


def execute_query(connection, query: str, vals: tuple = None):
    cursor = connection.cursor()
    try:
        if vals:
            cursor.execute(query, vals)
        else:
            cursor.execute(query)
        connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred.")


def main():
    # section for SQL definitions and setup
    SQL_PATH = 'sections.sqlite'
    CREATE_SECTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS sections (
    mon INTEGER NOT NULL,
    tue INTEGER NOT NULL,
    wed INTEGER NOT NULL,
    thu INTEGER NOT NULL,
    fri INTEGER NOT NULL,
    start_time INTEGER NOT NULL,
    end_time INTEGER NOT NULL,
    hall TEXT NOT NULL,
    room TEXT NOT NULL 
    );
    """
    CREATE_HALL_INDEX = "CREATE INDEX IF NOT EXISTS idx_hall ON hall (keyword)"
    INSERT_SECTION = """
    INSERT INTO sections (mon, tue, wed, thu, fri, start_time, end_time, hall, room) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    connection = create_connection(SQL_PATH)
    execute_query(connection, CREATE_SECTIONS_TABLE)
    execute_query(connection, CREATE_HALL_INDEX)

    html_file = 'courses.html'
    split_line = '<!-- https://docs.djangoproject.com/en/3.0/ref/templates/builtins/#autoescape -->'
    with open(html_file, 'r') as f:
        text = [line.strip() for line in f.read().split('\n') if len(line)]
    # grab all indices of lines matching split_line to define boundaries between courses
    indices = []
    for idx, line in enumerate(text):
        if line == split_line:
            indices.append(idx)

    max_ind = len(indices) - 1
    for outer_index, i in enumerate(indices):
        section = {'days': [], 'start': -1, 'end': -1, 'hall': '', 'room': ''}
        if outer_index == max_ind:
            break
        lines = text[i:indices[i+1]]
        for inner_index, line in enumerate(lines):
            if '<!-- schedule -->' in line:
                schedule_str = re.match('<td[^>]*>(.*?)</td>', lines[inner_index+1]).group(1)
                # days are stored in a list of five boolean integer values, one for each weekday.
                # MWF = [1, 0, 1, 0, 1], Th = [0, 0, 0, 1, 0], etc.
                if schedule_str != 'None':
                    days_str = schedule_str.split(' ')[0]
                    days = [0, 0, 0, 0, 0]
                    if 'M' in days_str:
                        days[0] = 1
                        days_str = days_str.replace('M', '')
                    if 'TH' in days_str:
                        days[3] = 1
                        days_str = days_str.replace('TH', '')
                    if 'T' in days_str:
                        days[1] = 1
                        days_str = days_str.replace('T', '')
                    if 'W' in days_str:
                        days[2] = 1
                        days_str = days_str.replace('W', '')
                    if 'F' in days_str:
                        days[4] = 1
                    section['days'] = days

                    # start and end time are stored in minutes after midnight.
                    # 1 == 12:01 am, 120 = 2:00 am, 990 = 4:30 pm, etc.
                    time_arr = ' '.join(schedule_str.split(' ')[1:]).split('-')
                    start_time_str = time_arr[0]
                    start_hr_min_str = start_time_str.split(' ')[0]
                    start_time = 720 if start_time_str.split(' ')[1] == 'PM' else 0
                    start_time += 60*int(start_hr_min_str.split(':')[0]) + int(start_hr_min_str.split(':')[1])
                    end_time_str = time_arr[1]
                    end_hr_min_str = end_time_str.split(' ')[0]
                    end_time = 720 if end_time_str[1] == 'PM' else 0
                    end_time += 60*int(end_hr_min_str.split(':')[0]) + int(end_hr_min_str.split(':')[1])
                    section['start'] = start_time
                    section['end'] = end_time
            elif '<!-- room -->' in line:
                hall_room_str = re.match('<td[^>]*>(.*?)</td>', lines[inner_index+1]).group(1)
                if hall_room_str != 'None':
                    print(hall_room_str)
                    hall_room_index = hall_room_str.lower().index('rm ')
                    section['hall'] = hall_room_str[:hall_room_index-1]
                    section['room'] = hall_room_str[hall_room_index+3:]

        execute_query(connection, INSERT_SECTION, (section['days'][0], section['days'][1], section['days'][2],
                                                   section['days'][3], section['days'][4], section['start'],
                                                   section['end'], section['hall'], section['room']))


if __name__ == '__main__':
    main()
