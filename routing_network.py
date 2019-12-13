import requests
import json
import sys


def main():
    #url = sys.argv[1]
    #top = sys.argv[2]
    url = "www.goatgoose.com:8080"
    top = "topology1"

    get_url = "http://" + url + "/get_topology/" + top
    post_url = "http://" + url + "/set_tables/" + top
    r = requests.get(get_url)

    js = r.json()

    nodes = []
    node_relations = []

    forwarding_array = []
    forwarding_table = {}
    hosts = []
    for i in range(len(js["connected"])):
        n = js["connected"][i]
        if n[0] == str(n[0]):
            hosts.append(n[0])

    for i in range(len(js["connected"])):
        n = js["connected"][i]
        node_relations.append([n[0], n[1], n[2]])
        if str(n[0]) not in nodes:
            nodes.append(str(n[0]))

    graph = Graph()

    for i in nodes:
        graph.add_node(i)

    for i in node_relations:
        graph.add_edge(str(i[0]), str(i[1]), 1, i[2])

    results = []

    for x in nodes:
        for y in hosts:
            if x != y:
                results.append(shortest_path(graph, x, y))

    for i in results:
        d = {}
        from_node = i[1][0]
        to_node = i[1][1]
        dst_node = i[1][-1]
        forwarding_port = graph.ports[(to_node, from_node)]
        if len(from_node) < 4:
            d["switch_id"] = int(from_node)
            d["dst_ip"] = dst_node
            d["out_port"] = forwarding_port
            forwarding_array.append(d)

    forwarding_table["table_entries"] = forwarding_array

    table_json = json.dumps(forwarding_table)

    t = requests.post(post_url, data=table_json)
    print(t.text)


def dijkstra(graph, start, end):
    path = {}
    node_set = set(graph.nodes)  # unordered set
    visited = {start: 0}
    while node_set:
        min_node = None  # no minimum node on first run

        for node in node_set:
            if node in visited:  # loops until it finds the start node
                if min_node is None:
                    min_node = node  # the minimum node on the first node will be the start node
                elif visited[node] < visited[min_node]:  # if the cost to get to the next node is less than the current min node
                    min_node = node  # the min node now becomes the current node

        node_set.remove(min_node)  # remove the min node from the set as it has now been visited
        weight = visited[min_node]  # the weight will be the cost of getting to the current node

        for edge in graph.edges[min_node]:

            total_weight = weight + graph.weights[(min_node, edge)]  # the total weight becomes the current weight thus far, plus the cost of the new edge

            if edge not in visited or total_weight < visited[edge]:  # if the edge is not in visited we add to visited and path
                visited[edge] = total_weight
                path[edge] = min_node

        if end in visited:
            break  # This creates the modified version of dijkstra, without this it would check all the nodes, however it ends when the end node is in the set of visited nodes

    return visited, path


def shortest_path(graph, origin, destination):  # helps display all the data
    visited, paths = dijkstra(graph, origin, destination)

    traveled = []
    end = paths[destination]

    while end != origin:
        traveled.insert(0, end)
        end = paths[end]

    traveled.insert(0, origin)
    traveled.append(destination)

    return round(visited[destination], 1), traveled


class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = {}
        self.weights = {}
        self.ports = {}

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, from_node, to_node, distance, port):
        self.edges.setdefault(from_node, []).append(to_node)
        self.edges.setdefault(to_node, []).append(from_node)
        self.weights[(from_node, to_node)] = distance
        self.weights[(to_node, from_node)] = distance
        self.ports[(to_node, from_node)] = port


main()
