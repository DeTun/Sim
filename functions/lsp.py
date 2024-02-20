import math


class LSP:
    def __init__(self):
        self.length_1, self.length_2, self.length_3, self.length_4 = 0, 0, 0, 0
        self.length_5, self.length_6, self.length_7 = 0, 0, 0
        self.y_4, self.y_5 = 0, 0
        self.alpha_max, self.gamma_max, self.pos_lsp_max, self.pos_ch_max = 0, 0, 0, 0

    def set_length(self, l1, l2, l3, l4, l5, l6, y_4, y_5):
        self.length_1 = l1
        self.length_2 = l2
        self.length_3 = l3
        self.length_4 = l4
        self.length_5 = l5
        self.length_6 = l6
        self.length_7 = math.sqrt(l3**2 + l4**2)
        self.y_4 = y_4
        self.y_5 = y_5
        self.alpha_max = self.calculate_alpha_max(y_4, y_5, l4, l5, l6)
        self.gamma_max = self.calculate_gamma_max(self.alpha_max, y_4, l1, l2, l3, l4)
        self.pos_lsp_max = math.sqrt((self.length_4 + self.length_5 + self.length_6)**2 + (self.y_4 - self.y_5)**2)
        self.pos_ch_max = self.calculate_pos_ch_max(self.alpha_max, self.gamma_max, l2, l3, l4)

    @staticmethod
    def calculate_alpha_max(y_4: float, y_5: float, length4: float, length5: float, length6: float) -> float:
        return math.acos((y_4 - y_5) / (length4 + length5 + length6))

    @staticmethod
    def calculate_gamma_max(alpha: float, y_4: float, length1: float, length2: float, length3: float, length4: float) -> float:
        tmp = y_4 - (math.cos(alpha) * length4) - (math.sin(alpha) * length3)
        return math.asin((tmp - length1) / length2)

    @staticmethod
    def calculate_pos_ch_max(alpha: float, gamma: float, length2: float, length3: float, length4: float) -> float:
        tmp = (math.sin(alpha) * length4) - (math.cos(alpha) * length3)
        return tmp - (math.cos(gamma) * length2)

    def pos_lsp(self, pos_ch_input: float) -> float:
        pos_ch = self.pos_ch_max + pos_ch_input
        l_8 = math.sqrt(pos_ch**2 + (self.y_4 - self.length_1)**2)
        alpha_1 = math.atan(self.length_3 / self.length_4)
        alpha_2 = math.atan(pos_ch / (self.y_4 - self.length_1))
        alpha_3 = math.acos((-(self.length_2**2) + self.length_7**2 + l_8**2) / (2 * self.length_7 * l_8))

        pos_3 = math.sin(alpha_1 + alpha_2 + alpha_3) * (self.length_4 + self.length_5)
        y_3 = self.y_4 - math.cos(alpha_1 + alpha_2 + alpha_3) * (self.length_4 + self.length_5)
        pos_lsp_ref = pos_3 + (math.sqrt(self.length_6**2 - (y_3 - self.y_5)**2))
        return pos_lsp_ref - self.pos_lsp_max
