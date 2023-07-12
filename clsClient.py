import queue


class Client:
    def __init__(self, skt, address):
        self.skt = skt
        self.address = address
        self.data = dict()
        self.uuid = None
        self.to_receive = queue.Queue()
        self.server_info = queue.Queue()

    def put_mess(self, content):
        self.to_receive.put(content)

    def put_server_info(self, content):
        self.server_info.put(content)

    def get_all(self):
        messages = []
        for _ in range(self.to_receive.qsize()):
            content = self.to_receive.get()
            messages.append(content)
        return messages

    def get_server_info(self):
        if self.server_info.qsize() > 0:
            return self.server_info.get()
        return {}

    def config(self, dict_data):
        self.uuid = dict_data["uuid"]
        print(f"set name to {self.uuid}")

    def __str__(self):
        return f"Client({self.uuid}, {self.address})"
