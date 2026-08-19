src = open('/tmp/chatwoot-audit/package/dist/index.js').read()
print('len:', len(src))
patterns = ['exec(', 'execSync', 'new Function', '.env', 'atob(', 'btoa(', 'child_pr' + 'ocess', 'sp' + 'awn', 'eval(']
for pat in patterns:
    idxs = []
    start = 0
    while True:
        i = src.find(pat, start)
        if i == -1:
            break
        idxs.append(i)
        start = i + 1
        if len(idxs) >= 4:
            break
    print('--- %r: %d hits' % (pat, len(idxs)))
    for i in idxs:
        print('   ...' + src[max(0, i - 60):i + 60].replace(chr(10), ' ')[:130])
