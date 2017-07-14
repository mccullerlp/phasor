# -*- coding: utf-8 -*-
"""
"""
from __future__ import division, print_function, unicode_literals
import heapq
import threading

#python 2.7 compatibility
try:
    from queue import Empty
except ImportError:
    from Queue import Empty


class HeapPriorityQueue(object):
    """
    Provide a priority Queue based on the :mod:`heapq` module. Should hold mostly to
    the :class:`Queue.Queue` interface with the addition of a peek method.

    This implementation is **not** threadsafe

    .. automethod:: __init__

    .. automethod:: peek

    .. automethod:: is_empty

    .. automethod:: pop

    .. automethod:: push

    .. automethod:: replace

    .. automethod:: pushpop

    """
    def __init__(self, iterable = ()):
        """
        :param iterable: iterable of initial items
        """
        heap = list(iterable)
        heapq.heapify(heap)
        self.heap = heap

    def peek(self):
        """
        View the first element without discarding

        :raises: :exc:`Queue.Empty` if no items contained
        """
        try:
            return self.heap[0]
        except IndexError:
            raise Empty()

    def is_empty(self):
        """
        Returns True when empty
        """
        return not self.heap

    def __bool__(self):
        return bool(self.heap)

    def __len__(self):
        return len(self.heap)

    def pop(self):
        """
        return first item

        :raises: :exc:`Queue.Empty` if no items contained
        """
        try:
            return heapq.heappop(self.heap)
        except IndexError:
            raise Empty()

    def push(self, item):
        """
        Add an item to the priority Queue
        """
        return heapq.heappush(self.heap, item)

    def replace(self, item):
        """
        get the smallest item and replace it with a new one

        :raises: :exc:`IndexError` when empty
        """
        return heapq.heapreplace(self.heap, item)

    def pushpop(self, item):
        """
        add item into the Queue then return the smallest
        """
        return heapq.heappushpop(self.heap, item)


class HeapPriorityQueueThreadsafe(object):
    """
    Provide a priority Queue based on the :mod:`heapq` module. Should hold mostly to
    the :class:`Queue.Queue` interface with the addition of a peek method.

    This implementation **is** threadsafe

    .. automethod:: __init__

    .. automethod:: peek

    .. automethod:: is_empty

    .. automethod:: pop

    .. automethod:: push

    .. automethod:: replace

    .. automethod:: pushpop

    """
    def __init__(self, iterable = ()):
        """
        :param iterable: iterable of initial items
        """
        self.lock = threading.Lock()
        heap = list(iterable)
        heapq.heapify(heap)
        self.heap = heap

    def peek(self):
        """
        View the first element without discarding

        :raises: :exc:`Queue.Empty` if no items contained
        """
        try:
            return self.heap[0]
        except IndexError:
            raise Empty()

    def is_empty(self):
        """
        Returns True when empty
        """
        return not self.heap

    def pop(self):
        """
        return first item

        :raises: :exc:`Queue.Empty` if no items contained
        """
        with self.lock:
            try:
                return heapq.heappop(self.heap)
            except IndexError:
                raise Empty()

    def push(self, item):
        """
        Add an item to the priority Queue
        """
        with self.lock:
            return heapq.heappush(self.heap, item)

    def replace(self, item):
        """
        get the smallest item and replace it with a new one

        :raises: :exc:`IndexError` when empty
        """
        with self.lock:
            return heapq.heapreplace(self.heap, item)

    def pushpop(self, item):
        """
        add item into the Queue then return the smallest
        """
        with self.lock:
            return heapq.pushpop(self.heap, item)


