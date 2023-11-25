

class Follow_Line:
    
    def __init__(self):
        self._ir_status = [0, 0, 0, 0, 0]
    
    def get_steering_angle(self, ir_status):
        """
        Function to filter a stream of data.
        Will keep track of the filter state.

        :param stream: a single point of a stream
        :return: The current output of the filter
        """
        self._ir_status = ir_status
        print("IR Status:", self._ir_status)

        # Angle calculate
        if	self._ir_status == [0,0,1,0,0]:
            step = 0
        elif self._ir_status == [0,1,1,0,0] or self._ir_status == [0,0,1,1,0]:
            step = 2
        elif self._ir_status == [0,1,0,0,0] or self._ir_status == [0,0,0,1,0]:
            step = 7
        elif self._ir_status == [1,1,0,0,0] or self._ir_status == [0,0,0,1,1]:
            step = 10
        elif self._ir_status == [1,0,0,0,0] or self._ir_status == [0,0,0,0,1]:
            step = 13
        elif self._ir_status == [1,1,1,1,1]:
            self.stop()
            return

        # Direction calculate
        if	self._ir_status == [0,0,1,0,0]:
            if turning_angle < 90:
                turning_angle += 1
            elif turning_angle > 90:
                turning_angle -= 1
            else:
                turning_angle = 90
        # turn right
        elif self._ir_status in ([0,1,1,0,0],[0,1,0,0,0],[1,1,0,0,0],[1,0,0,0,0]):
            if turning_angle > 0:
                turning_angle -= step
            else:
                turning_angle = 0
        # turn left
        elif self._ir_status in ([0,0,1,1,0],[0,0,0,1,0],[0,0,0,1,1],[0,0,0,0,1]):
            if turning_angle < 135:
                turning_angle += step
            else:
                turning_angle = 135
        #find line
        elif self._ir_status == [0,0,0,0,0]:
            turning_angle = turning_angle

        fw.turn(math.radians(turning_angle), frame)