import zipfile, os.path
#Similar to extractall, but protects against path traversal vulnerabilities

def unzip(source_filename,dest_dir):
    flist = []
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            if member.filename.startswith('__MACOSX/'): continue
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                drive,word = os.path.splitdrive(word)
                head,word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''): continue
                path = os.path.join(path,word)
            zf.extract(member,path)
            flist.append(os.path.join(path,words[-1]))
    return flist

def check_depth(source_filename):
    with zipfile.ZipFile(source_filename) as zf:
        max_depth = 0
        for member in zf.infolist():
            if member.filename.startswith('__MACOSX/'): continue
            words = member.filename.split('/')
            depth = len(words)
            max_depth = max(depth,max_depth)
    return max_depth

def check_extentions(source_filename,desired_exts):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            if member.filename.startswith('__MACOSX/'): continue
            name,ext = os.path.splitext(member.filename)
            if ext.lower() not in desired_exts+['']:
                zf.close()
                return False
    return True

