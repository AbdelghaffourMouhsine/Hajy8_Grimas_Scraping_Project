import threading
import time
from SociteScraping import SociteScraping

# Classe ThreadWorker qui permet à chaque thread de traiter une ligne de SIRET
class ThreadWorker(threading.Thread):
    def __init__(self, thread_id, lines, result_lines, error_lines, lock, proxy, lock_grid):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.lines = lines
        self.result_lines = result_lines
        self.error_lines = error_lines
        self.lock = lock
        self.proxy = proxy
        self.lock_grid = lock_grid
        self.sociteScraping = None
        print(f"start thread_id : {thread_id} avec proxy : {proxy["PROXY_HOST"]}")
        
    def run(self):
        while True:
            with self.lock:
                if not self.lines:
                    break
                line = self.lines.pop(0)

            try:
                siret = line['SIRET']
                with self.lock_grid :
                    self.sociteScraping = SociteScraping(siret=siret, proxy=self.proxy)
                    # time.sleep(1)
                result = self.sociteScraping.start_scraping()
                
                if result["status"]:
                    info = result["data"]
                    line['effectif'] = info['effectif']
                    line['capital'] = info['capital']
                    line['gerant'] = info['gerant']
                    with self.lock:
                        self.result_lines.append(line)
                else:
                    line['error'] = str(result["data"])
                    with self.lock:
                        self.error_lines.append(line)
            except Exception as e:
                line['error'] = str(e)
                with self.lock:
                    self.error_lines.append(line)
                print(e)