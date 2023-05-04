import math


class EaseFunction:

    @staticmethod
    def out_expo(x:float) -> float:
        return 1 - math.pow(2, -10 * x)

    @staticmethod
    def out_back(x:float) -> float:
        c1 = 1.70158
        c3 = c1 + 1
        return 1 + c3 * math.pow(x - 1, 3) + c1 * math.pow(x - 1, 2)