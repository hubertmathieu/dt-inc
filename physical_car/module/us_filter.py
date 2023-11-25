from collections import deque

class US_Filter:
    
    def __init__(self, window_size):
        self._buffer = deque(maxlen=window_size)
        self._prev_ma = 100
    
    def filter_stream(self, stream):
        """
        Function to filter a stream of data.
        Will keep track of the filter state.

        :param stream: a single point of a stream
        :return: The current output of the filter
        """
        self._buffer.append(stream)
        self.prev_ma = sum(self._buffer) / len(self._buffer)
        return self.prev_ma
