import re


def get_commands_from_file(command_file_string):
    # Split file into lines
    lines = re.split('\n+|\r+', command_file_string)
    entries = []
    for line in lines:
        # Skip comments and lines starting with whitespace
        if not line or line[0] == '#' or line[0] == '\t' or line[0] == ' ':
            continue
        # Clean up
        entry = {}
        line = line.replace('/ ', '/')

        # Split on whitespace
        split_line = re.split(r'\s+', line)

        # Set command
        command = split_line[0]
        if len(split_line) > 1:
            command += ' ' + split_line[1]
        entry['command'] = command.lower()

        # Set options and values
        options = []
        values = []
        for i in range(2, len(split_line)):
            # Objects have leading "/"
            if split_line[i] and split_line[i][0] == '/':
                options.append(split_line[i][1:].lower())
            else:  # Value or password
                if split_line[1] == 'password':
                    pwd = split_line[i].split('=')
                    values.append(pwd[0].upper() + '=' + pwd[1])
                else:
                    values.append(split_line[i])
        entry['options'] = options
        entry['values'] = values
        entries.append(entry)
    return entries
