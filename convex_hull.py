from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF, QObject
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
#
PAUSE = 0.25


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

    # Class constructor
    def __init__(self):
        super().__init__()
        self.pause = False

    # Some helper methods that make calls to the GUI, allowing us to send updates
    # to be displayed.

    def showTangent(self, line, color):
        self.view.addLines(line, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseTangent(self, line):
        self.view.clearLines(line)

    def blinkTangent(self, line, color):
        self.showTangent(line, color)
        self.showHull([], BLUE)
        self.eraseTangent(line)
        self.showHull([], BLUE)

    def showHull(self, polygon, color):
        self.view.addLines(polygon, color)
        if self.pause:
            time.sleep(PAUSE)

    def eraseHull(self, polygon):
        self.view.clearLines(polygon)

    def showText(self, text):
        self.view.displayStatusText(text)

    # This is the method that gets called by the GUI and actually executes
    # the finding of the hull
    # Entire algorithm should be O(n log n) time complexity
    def compute_hull(self, points, pause, view):
        self.pause = pause
        self.view = view
        assert (type(points) == list and type(points[0]) == QPointF)

        t1 = time.time()
        # Sort points by x value
        points.sort(key=lambda point: point.x())
        t2 = time.time()

        t3 = time.time()
        # this is a dummy polygon of the first 3 unsorted points
        polygon = [QLineF(points[i], points[(i + 1) % 3]) for i in range(3)]
        self.divide_and_conquer_solver(points)
        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        # self.showHull(polygon, RED)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4 - t3))

    def divide_and_conquer_solver(self, points):
        # if len(points) == 1:
        #     return points[0]
        # left_half = points[:len(points) // 2]
        # right_half = points[len(points) // 2:]
        # left = self.divide_and_conquer_solver(left_half)
        # right = self.divide_and_conquer_solver(right_half)
        # return self.combine_hulls(left, right)

        left_half = self.sort_clockwise(points[1:4])
        right_half = self.sort_clockwise(points[4:7])

        polygon1 = [QLineF(left_half[i], left_half[(i + 1) % len(left_half)]) for i in range(len(left_half))]
        polygon2 = [QLineF(right_half[i], right_half[(i + 1) % len(right_half)]) for i in range(len(right_half))]

        self.showHull(polygon1, BLUE)
        self.showHull(polygon2, BLUE)

        self.combine_hulls(left_half, right_half)

    # O(n) time complexity
    def combine_hulls(self, left, right):
        if len(left) == 0:
            return right or []
        if len(right) == 0:
            return left or []

        # upper_tangent = self.get_upper_tangent_indexes(left, right)
        lower_tangent = self.get_lower_tangent_indexes(left, right)

    def get_upper_tangent_indexes(self, left, right):
        # Both left and right lists are sorted in clockwise order
        left_index, right_index = self.get_inner_indexes(left, right)
        done = False
        while not done:
            done = True
            # Step up the left half
            current_slope = self.get_slope(left[left_index], right[right_index])
            next_slope = None
            while next_slope != current_slope:
                next_left_index = (left_index - 1) % len(left)  # Next counter-clockwise index of left
                next_slope = self.get_slope(left[next_left_index], right[right_index])
                if next_slope < current_slope:
                    # We want to keep the next left index
                    left_index = next_left_index
                    current_slope = next_slope
                    next_slope = None
                    done = False
                    self.blinkTangent([QLineF(left[left_index], right[right_index])], RED)
                else:
                    next_slope = current_slope
            # Step up the right half
            current_slope = self.get_slope(left[left_index], right[right_index])
            next_slope = None
            while next_slope != current_slope:
                next_right_index = (right_index + 1) % len(right)  # Next clockwise index of right
                next_slope = self.get_slope(left[left_index], right[next_right_index])
                if next_slope > current_slope:
                    # We want to keep the next right index
                    right_index = next_right_index
                    current_slope = next_slope
                    next_slope = None
                    done = False
                    self.blinkTangent([QLineF(left[left_index], right[right_index])], RED)
                else:
                    next_slope = current_slope
        self.showTangent([QLineF(left[left_index], right[right_index])], GREEN)
        return left_index, right_index

    def get_lower_tangent_indexes(self, left, right, upper=True):
        # Both left and right lists are sorted in clockwise order
        left_index, right_index = self.get_inner_indexes(left, right)
        done = False
        while not done:
            done = True
            # Step up the left half
            current_slope = self.get_slope(left[left_index], right[right_index])
            next_slope = None
            while next_slope != current_slope:
                next_left_index = (left_index - 1) % len(left)  # Next counter-clockwise index of left
                next_slope = self.get_slope(left[next_left_index], right[right_index])
                if next_slope < current_slope:
                    # We want to keep the next left index
                    left_index = next_left_index
                    current_slope = next_slope
                    next_slope = None
                    done = False
                    self.blinkTangent([QLineF(left[left_index], right[right_index])], RED)
                else:
                    next_slope = current_slope
            # Step up the right half
            current_slope = self.get_slope(left[left_index], right[right_index])
            next_slope = None
            while next_slope != current_slope:
                next_right_index = (right_index + 1) % len(right)  # Next clockwise index of right
                next_slope = self.get_slope(left[left_index], right[next_right_index])
                if next_slope > current_slope:
                    # We want to keep the next right index
                    right_index = next_right_index
                    current_slope = next_slope
                    next_slope = None
                    done = False
                    self.blinkTangent([QLineF(left[left_index], right[right_index])], RED)
                else:
                    next_slope = current_slope
        self.showTangent([QLineF(left[left_index], right[right_index])], GREEN)
        return left_index, right_index

    def get_slope(self, point1, point2):
        assert type(point1) == QPointF and type(point2) == QPointF
        return (point1.y() - point2.y()) / (point1.x() - point2.x())

    def get_inner_indexes(self, left, right):
        largest_list_size = 0
        if len(left) > len(right):
            largest_list_size = len(left)
        else:
            largest_list_size = len(right)

        # Get the far right point of the left list and the far left point of the right list O(n)
        right_index = left_index = -1
        for i in range(largest_list_size):
            if i < len(right):
                if right_index < 0:
                    right_index = i
                elif right[i].x() < right[right_index].x():
                    right_index = i
            if i < len(left):
                if left_index < 0:
                    left_index = i
                elif left[i].x() > left[left_index].x():
                    left_index = i
        return left_index, right_index

    # TODO delete this method. It's for testing only
    def sort_clockwise(self, points):
        if len(points) < 2:
            return
        points.sort(key=lambda item: item.y())  # Sort by y value
        lowest = points[0]
        highest = points[len(points) - 1]
        middle = (lowest.y() + highest.y()) / 2
        points.sort(key=lambda item: item.x())  # Sort by x value
        top_half = []
        bottom_half = []
        for point in points:
            if point.y() > middle:
                top_half.append(point)
            else:
                bottom_half.append(point)
        bottom_half.reverse()
        top_half.extend(bottom_half)
        return top_half
