class HTTP:

    def __init__(self):
        self.request = None
        

    def run(self):
        while True:
            self.recv_from_client()
            self.server()
            self.send_to_client()

    def recv_from_client(self):
        # Get request from client

        # Process


    def send_to_client(self):
        # Send to client

    def server(self):
        # Send
        # Recv

