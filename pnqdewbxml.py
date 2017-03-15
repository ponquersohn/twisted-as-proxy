import subprocess


def pnqwbxml2xml(sourcexml):
    cmd  = ['/usr/local/bin/wbxml2xml', '-', '-l', 'ACTIVESYNC', '-o', '-' ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          stdin=subprocess.PIPE)
    out, err = p.communicate(sourcexml)
    #print "err: %s" % err
    #print "out: %s" % out
    return out