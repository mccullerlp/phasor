# -*- coding: utf-8 -*-
"""
Generators implementing Topological Sort and Strongly-connected-component detection using the `Tarjan Algorithm<http://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm>`_ for `Strongly-connected-components<http://en.wikipedia.org/wiki/Strongly_connected_component>`_

These are medium-duty implementations, they still use a hash-table for lookup, rather than raw integer tables.

.. autoexception:: SCCError

.. autofunction:: topological_sort_recursive

.. autofunction:: topological_sort
"""
from __future__ import division, print_function, unicode_literals
#from builtins import str


class SCCError(RuntimeError):
    """
    Exception Class used to annotate when a Strongly Connected Component is found
    """
    def __init__(self, scc):
        self.scc = scc

    @property
    def message(self):
        return ("Found a Strongly Connected Component of nodes: {0}").format(str(self.scc))

    def __str__(self):
        return self.message


def topological_sort(nodes, successor_func, single = False):
    """
    Implements a stack-based implementation of the Tarjan Algorithm.

    :param nodes: container or iterator of nodes to use (can just contain starting nodes)
    :param successor_func: function mapping a node to a container/iterator of nodes (representing edges)
    :param single: (defaults False) When True, only return the nodes and raise SCCError on cycles, otherwise
        always returns tuples of nodes in the topo-sort of the SCC's
    """
    #this algorithm uses negative lowlinks to tag that the node as already been seen/extracted from an SCC
    #this prevents the need of tracking who is on the stack or keeping an additional set container around

    #must start at 1 because of the negative-sign tagging
    index_counter = [1]
    lowlinks = {}
    index = {}
    stack = []
    iter_stack = []

    def strongconnect(node):
        if node in lowlinks:
            return

        def insert_node(node):
            stack.append(node)
            iter_stack.append(iter(successor_func(node)))
            # set the depth index for this node to the smallest unused index
            index[node] = index_counter[0]
            lowlinks[node] = index_counter[0]
            index_counter[0] += 1
            return

        #insert the initial node
        insert_node(node)

        while True:
            node = stack[-1]
            for successor in iter_stack[-1]:
                successor_ll = lowlinks.get(successor, None)
                if successor_ll is None:
                    insert_node(successor)
                    break
                elif successor_ll < 0:
                    pass
                else:
                    lowlinks[node] = min(lowlinks[node], successor_ll)
            #this else is against the for loop, it triggers when the iterator runs out of elements
            #and break is NOT called
            else:
                child_node = node
                node = stack.pop()
                iter_stack.pop()
                #both of these lowlinks must be positive because they are on the stack
                lowlinks[node] = min(lowlinks[child_node],lowlinks[node])

                #here is the only place that the stack could be empty
                if not stack:
                    assert(lowlinks[node] > 0)
                    lowlinks[node] *= -1
                    if single:
                        yield node
                    else:
                        yield (node,)
                    break

                # If `node` is a root node, pop the stack and generate an SCC
                if lowlinks[node] < index[node]:
                    assert(lowlinks[node] > 0)
                    lowlinks[node] *= -1
                    component = [node]
                    while stack:
                        ND = stack.pop()
                        component.append(ND)
                        assert(lowlinks[ND] > 0)
                        lowlinks[ND] *= -1
                        if -lowlinks[ND] == index[ND]:
                            break
                    else:
                        #didn't hit break, so the stack is empty
                        component = tuple(component)
                        yield component
                        return
                    component = tuple(component)
                    if single:
                        raise SCCError(component)
                    else:
                        yield component

                elif lowlinks[node] == index[node]:
                    assert(lowlinks[node] > 0)
                    lowlinks[node] *= -1
                    if single:
                        yield node
                    else:
                        yield (node,)

    for node in nodes:
        for component in strongconnect(node):
            yield component
    return

def topological_sort_dict(graph):
    """
    Helper generator for topological sorting a dict-stored graph, throws SCCError if there are cycles
    """
    for component in topological_sort(iter(list(graph.keys())), lambda k:graph.get(k, ()), single = True):
        yield component
    return
