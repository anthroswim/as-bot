import os

class FileCache:
    cache_dir = "tmp"
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    def getfile(file) -> str:
        fullpath = FileCache.pathjoin(file)
        if os.path.exists(fullpath):
            return fullpath
        return None
    
    def getpath(path) -> str:
        if os.path.exists(path):
            return path
        return None

    def pathjoin(file) -> str:
        return os.path.join(FileCache.cache_dir, file)
    
    def removefile(file):
        os.remove(FileCache.pathjoin(file))

    def removepath(path):
        os.remove(path)

    def clear():
        for file in os.listdir(FileCache.cache_dir):
            os.remove(FileCache.pathjoin(file))