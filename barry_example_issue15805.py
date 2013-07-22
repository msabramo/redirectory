from redirectory import stdout_to_file

with stdout_to_file('/tmp/debug.log', 'w', encoding='utf-8'):
    print('hello')
