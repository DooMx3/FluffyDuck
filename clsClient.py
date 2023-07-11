import queue


class Client:
    def __init__(self, skt, address):
        self.skt = skt
        self.address = address
        self.uuid = None
        self.to_receive = queue.Queue()

    def put_mess(self, content):
        self.to_receive.put(content)

    def get_all(self):
        messages = []
        for _ in range(self.to_receive.qsize()):
            content = self.to_receive.get()
            messages.append(content)
        return messages

    def config(self, dict_data):
        self.uuid = dict_data["uuid"]
        print(f"set name to {self.uuid}")

    def __str__(self):
        return f"Client({self.uuid}, {self.address})"
