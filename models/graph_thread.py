from threading import Thread


class GraphThread(Thread):

    def __init__(self, graph):
        Thread.__init__(self)
        self.graph = graph

    def run(self):
        self.graph.set_figure()
