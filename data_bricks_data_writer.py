'''
This is side to be asked by DataBricks

source: https://www.1point3acres.com/bbs/thread-1066176-1-1.html
'''

import threading
import time
import numpy as np

class DataWriter:
    def __init__(self, filepath, file_appender):
        self.buf = []
        self.file_appender = file_appender
        self.filepath = filepath
        file_appender.register(filepath)

    def push(self, data):
        self.buf.append(data)

    def commit(self):
        self.file_appender.flush(self.filepath, self.buf)
        self.buf.clear()

class FileAppender:
    def __init__(self):
        self.files = {}  # filepath -> fd
        self.lock = threading.Lock()

    def register(self, filepath):
        self.lock.acquire()
        if filepath not in self.files:
            self.files[filepath] = open(filepath, 'w+') # should be "a+" if not for easy testing
        self.lock.release()

    def flush(self, filepath, buf):
        if filepath not in self.files:
            return
        
        self.lock.acquire()
        for t in buf:
            self.files[filepath].write(f"{t} ")
            # [Critical] It's critical to sleep and simulate a "slow" disk write. Otherwise very
            # fast file write (mostly done by SSD) will hide the file corruption caused by 
            # racing condition
            time.sleep(np.random.randint(0, 100) / 1000000)
        self.files[filepath].flush()
        self.lock.release()
        print(f"flushed {len(buf)} integers")

    def close_files(self):
        for path, fd in self.files.items():
            fd.close()
            print(f"File {path} closed")
        

def worker_func(filepath, data, appender):
    dw = DataWriter(filepath, appender)
    for t in data:
        dw.push(t)
        if np.random.rand() < 0.2:
            dw.commit()

    dw.commit()
    
        
global_appender = FileAppender()
F = "./concurrent_file"
N = 200
SIZE = 1000

threads = []

for i in range(N):
    t = threading.Thread(target = worker_func, args = (F, range(i * SIZE, (i+1) * SIZE), global_appender))
    threads.append(t)

start_time = time.time()
    
for t in threads:
    t.start()

for t in threads:
    t.join()

global_appender.close_files()

end_time = time.time()

time_cost = end_time - start_time
print(f"Time elapsed: {time_cost} seconds")
print("Running tests")

# Check result
with open(F, 'r') as f:
    lst = [int(t) for t in f.read().split() if len(t) > 0]
    check = {}
    for idx, val in enumerate(lst):
        check[val] = idx

    for i in range(N):
        prev = -1
        count = 0
        for v in range(SIZE * i, SIZE * (i+1)):
            assert v in check, f"{v} is missing"
                
            cur = check[v]
            assert cur > prev, f"{prev}, {cur}"
            prev = cur
            count += 1
        assert count == SIZE, "%d:%d" % (i, count)

    print("All tests passed")
    
