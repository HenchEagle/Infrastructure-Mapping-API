from abc import ABC, abstractmethod

class Persister(ABC):
    @abstractmethod
    def get_connection(self):
        pass

    # Scan Repository
    @abstractmethod
    def get_scan_queue(self):
        pass

    @abstractmethod
    def create_scan_record(self):
        pass

    @abstractmethod
    def update_scan_status(self):
        pass

    @abstractmethod
    def get_last_scan(self):
        pass

    # Graph Repository
    @abstractmethod
    def write_edges(self):
        pass

    @abstractmethod
    def write_nodes(self):
        pass

    @abstractmethod
    def write_scan_relationships(self):
        pass

    @abstractmethod
    def get_full_graph(self):
        pass