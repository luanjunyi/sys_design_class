import threading
from collections import deque, defaultdict
import random
import time

class DataWriter:
	def __init__(self, file_path: str):
		self.q = defaultdict(deque)
		self.locks = {1: threading.Lock(), 2: threading.Lock(), 3: threading.Lock(), 4: threading.Lock()}
		self.result = []

	def push(self, data: int, current_thread_id):
		with self.locks[current_thread_id]:
			print(f'{current_thread_id} push: lock {current_thread_id} accquired')
			self.q[current_thread_id].append(data)
			print(f'{current_thread_id} push: self.q[{current_thread_id}] after pushing {self.q[current_thread_id]}')
			time.sleep(random.randint(1,4)) #assume doing some work
			print(f'{current_thread_id} push: for threadsafety self.q[{current_thread_id}] after pushing {self.q[current_thread_id]}')
			print(f'{current_thread_id} push: lock {current_thread_id} released')

		time.sleep(random.randint(1,4))

	def write(self):
		while True:
			for current_thread_id in self.locks.keys():
				cur_q = self.q[current_thread_id]
				cur_lock = self.locks[current_thread_id]
				if cur_lock.acquire(blocking=False):
					print(f'{current_thread_id} write: lock  accquired')
					try:
						if len(cur_q) > 0:
							data_to_write = cur_q.popleft()
							print(f'{current_thread_id} write: after popleft self.q[{current_thread_id}] {cur_q}, data_to_write {data_to_write}')
							self.result.append(data_to_write)
							time.sleep(random.randint(1,2)) #assume doing some work
							print(f'{current_thread_id} write: for threadsafe self.q[{current_thread_id}] {cur_q}, data_to_write {data_to_write}')

							print(f'{current_thread_id} write: data_to_write {data_to_write} and self.result {self.result}')
						cur_lock.release()
					finally:
						print(f'{current_thread_id} write: lock released')

				time.sleep(random.randint(1,4))

dw = DataWriter("my_file_path_1")
def thread_target_1(thread_id):
	for cur_data in range(10):
		dw.push(cur_data, thread_id)

def thread_target_2(thread_id):
	for cur_data in range(100,110):
		dw.push(cur_data, thread_id)

def thread_target_3(thread_id):
	for cur_data in range(200,210):
		dw.push(cur_data, thread_id)

def thread_target_4(thread_id):
	for cur_data in range(300,310):
		dw.push(cur_data, thread_id)

t1 = threading.Thread(target=thread_target_1, args=(1,))
t2 = threading.Thread(target=thread_target_2, args=(2,))
t3 = threading.Thread(target=thread_target_3, args=(3,))
t4 = threading.Thread(target=thread_target_4, args=(4,))
t5 = threading.Thread(target=dw.write)

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()

t1.join()
t2.join()
t3.join()

print(dw.result)




