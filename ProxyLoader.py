import threading
import os

class ProxyLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.proxies = []
        self.load_proxies()
        self.lock = threading.Lock()
        
    def load_proxies(self):
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f"Le fichier {self.file_path} n'existe pas.")
        
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
            self.proxies = []
            for line in lines:
                parts = line.strip().split(':')
                if len(parts) == 4:
                    proxy_dict = {
                        "PROXY_HOST": parts[0],
                        "PROXY_PORT": parts[1],
                        "PROXY_USER": parts[2],
                        "PROXY_PASS": parts[3]
                    }
                    self.proxies.append(proxy_dict)
                else:
                    print(f"Format de ligne incorrect: {line.strip()}")

    def get_proxy(self, index):
        # Utilise l'opérateur modulo pour garantir que l'indice reste dans les limites de la liste
        index = index % len(self.proxies)
        return self.proxies[index]