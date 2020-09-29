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
def get_inner_indexes(left, right):
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


def get_slope(point1, point2):
    assert type(point1) == QPointF and type(point2) == QPointF
    return (point1.y() - point2.y()) / (point1.x() - point2.x())


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
        if self.pause:
            self.showHull([], BLUE)
        self.eraseTangent(line)

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
        points.sort(key=lambda point: point.x())  # Sort points by x value
        hull = self.divide_and_conquer_solver(points)
        t2 = time.time()

        polygon = [QLineF(hull[i], hull[(i + 1) % len(hull)]) for i in range(len(hull))]
        self.showHull(polygon, GREEN)
        self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t2 - t1))

    def divide_and_conquer_solver(self, points):
        if len(points) == 1:
            return points
        left_half = points[:len(points) // 2]
        right_half = points[len(points) // 2:]
        left = self.divide_and_conquer_solver(left_half)
        right = self.divide_and_conquer_solver(right_half)
        return self.combine_hulls(left, right)

    # O(n) time complexity
    def combine_hulls(self, left, right):
        # GUI Display
        polygon1, polygon2, line1, line2 = None, None, None, None
        if self.pause:
            polygon1 = [QLineF(left[i], left[(i + 1) % len(left)]) for i in range(len(left))]
            polygon2 = [QLineF(right[i], right[(i + 1) % len(right)]) for i in range(len(right))]
            self.showHull(polygon1, BLUE)
            self.showHull(polygon2, BLUE)

        upper_left, upper_right = self.get_tangent_indexes(left, right, True)
        # Show upper tangent on GUI
        if self.pause:
            line1 = QLineF(left[upper_left], right[upper_right])
            self.showTangent([line1], GREEN)

        lower_left, lower_right = self.get_tangent_indexes(left, right, False)
        # Show lower tangent on GUI
        if self.pause:
            line2 = QLineF(left[lower_left], right[lower_right])
            self.showTangent([line2], GREEN)

        new_hull = []

        # Add valid hull indexes from right hull (everything clockwise between upper_right and lower_right)
        i = upper_right
        while i != lower_right:
            new_hull.append(right[i])
            i = (i + 1) % len(right)  # next index clockwise
        new_hull.append(right[i])  # add the lower_right index

        # Add valid hull indexes from left hull (everything clockwise between lower_left and upper_left)
        i = lower_left
        while i != upper_left:
            new_hull.append(left[i])
            i = (i + 1) % len(left)  # next index clockwise
        new_hull.append(left[i])  # add the upper_left index

        if self.pause:
            self.eraseTangent([line1])
            self.eraseTangent([line2])
            self.eraseHull(polygon1)
            self.eraseHull(polygon2)

        return new_hull

    def get_tangent_indexes(self, left, right, upper=True):
        # Both left and right lists should be sorted in clockwise order
        left_index, right_index = get_inner_indexes(left, right)
        done = False
        while not done:
            done = True
            # Step up the left half
            current_slope = get_slope(left[left_index], right[right_index])
            next_slope = None
            while next_slope != current_slope:
                # if getting upper tangent -> next counter-clockwise index of left
                #            else if lower -> next clockwise index of left
                next_left_index = ((left_index - 1) if upper else left_index + 1) % len(left)
                next_slope = get_slope(left[next_left_index], right[right_index])
                if (next_slope < current_slope) if upper else (next_slope > current_slope):
                    # Keep the next_left_index
                    left_index = next_left_index
                    current_slope = next_slope
                    next_slope = None
                    done = False
                    if self.pause:
                        self.blinkTangent([QLineF(left[left_index], right[right_index])], RED)
                else:
                    next_slope = current_slope
            # Step up the right half
            current_slope = get_slope(left[left_index], right[right_index])
            next_slope = None
            while next_slope != current_slope:
                # if getting upper tangent -> next clockwise index of right
                #            else if lower -> next counter-clockwise index of right
                next_right_index = ((right_index + 1) if upper else (right_index - 1)) % len(right)
                next_slope = get_slope(left[left_index], right[next_right_index])
                if (next_slope > current_slope) if upper else (next_slope < current_slope):
                    # Keep the next_right_index
                    right_index = next_right_index
                    current_slope = next_slope
                    next_slope = None
                    done = False
                    if self.pause:
                        self.blinkTangent([QLineF(left[left_index], right[right_index])], RED)
                else:
                    next_slope = current_slope
        return left_index, right_index
