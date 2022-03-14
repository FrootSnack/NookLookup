import re
import sqlite3


def main():
    html_file = 'courses.html'
    split_line = '<!-- https://docs.djangoproject.com/en/3.0/ref/templates/builtins/#autoescape -->'
    with open(html_file, 'r') as f:
        text = [line.strip() for line in f.read().split('\n') if len(line)]
    # grab all indices of lines matching split_line to define boundaries between courses
    indices = []
    for idx, line in enumerate(text):
        if line == split_line:
            indices.append(idx)

    sections = []
    max_ind = len(indices) - 1
    for outer_index, i in enumerate(indices):
        section = {'days': [], 'start': -1, 'end': -1, 'hall': '', 'room': -1}
        if outer_index == max_ind:
            break
        lines = text[i:indices[i+1]]
        for inner_index, line in enumerate(lines):
            if '<!-- schedule -->' in line:
                schedule_str = re.match('<td[^>]*>(.*?)</td>', lines[inner_index+1]).group(1)
                # days are stored in a tuple of five boolean values, one for each weekday.
                # MWF = (True, False, True, False, True), Th = (False, False, False, True, False), etc.
                if schedule_str != 'None':
                    days_str = schedule_str.split(' ')[0]
                    days = [False, False, False, False, False]
                    if 'M' in days_str:
                        days[0] = True
                        days_str = days_str.replace('M', '')
                    if 'TH' in days_str:
                        days[3] = True
                        days_str = days_str.replace('TH', '')
                    if 'T' in days_str:
                        days[1] = True
                        days_str = days_str.replace('T', '')
                    if 'W' in days_str:
                        days[2] = True
                        days_str = days_str.replace('W', '')
                    if 'F' in days_str:
                        days[4] = True
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
            elif '<!-- room -->' in line:
                hall_room_str = re.match('<td[^>]*>(.*?)</td>', lines[inner_index+1]).group(1)
                section['hall'] = '' if hall_room_str == 'None' else hall_room_str.split(' - ')[0]
                section['room'] = -1 if hall_room_str == 'None' else int(hall_room_str.split(' - ')[0][3:])

        sections.append(section)

    print(sections)


if __name__ == '__main__':
    main()
