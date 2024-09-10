import subprocess
from io import StringIO
import os
def run(cmd, throw=True, dry=False):

    if dry:
        print(cmd)
        return 0, ''

    print('Running: ', cmd)
    text = ''
    # try:
    #     with subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p, StringIO() as buf:
    #         for line in p.stdout:
    #             print(line)
    #             buf.write(line)
    #         text = buf.getvalue()
    #     returncode = 0
    # except:
    #     returncode = 1
    returncode = os.system(cmd)
    print(returncode)
    if throw and returncode != 0:
        raise Exception('Error')
    return returncode, text