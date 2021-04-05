def dump_port(port=1980):
    import subprocess, os
    from pprint import pprint

    try:
        output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True).decode()
    except Exception as e:
        if str(e) == "Command 'netstat -ano | findstr :5585' returned non-zero exit status 1.":
            return None

    pprint(output)

    ls = list(set([int(x.strip().split(' ')[-1]) for x in output.split('\r\n') if x.strip().split(' ')[-1] != '0' and x.strip().split(' ')[-1] != '']))

    for number in ls:
        os.system(f"taskkill/pid  {number} /F")

dump_port()