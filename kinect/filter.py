import cv2
import numpy as np

class Filter:
    HSV_COLOR_RANGES = {
        'red1': [[180, 255, 255], [159, 50, 70]],
        'red2': [[9, 255, 255], [0, 50, 70]],
        'green': [[89, 255, 255], [36, 50, 70]],
        'blue': [[128, 255, 255], [90, 50, 70]],
        'yellow': [[35, 255, 255], [25, 50, 70]],
        'purple': [[158, 255, 255], [129, 50, 70]]
    }

    RGB_COLORS = {
        'red': [0,0,255],
        'green': [0,255,0],
        'blue': [255,0,0],
        'purple': [255,0,255],
        'yellow': [0,255,255]
    }

    def __init__(self, img, color, depth=None, gradient=5):
        self.img = img
        self.color = color
        if depth == None:
            self.depth = None
        else:
            self.depth = depth/gradient
        # self.depth = depth/gradient if (depth not None) else self.depth = None
        self.mask = self.get_mask

    @property
    def get_mask(self):
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)

        mask = None
        if self.color == 'red':
            lower_red1 = np.array(Filter.HSV_COLOR_RANGES['red1'][1])
            upper_red1 = np.array(Filter.HSV_COLOR_RANGES['red1'][0])

            lower_red2 = np.array(Filter.HSV_COLOR_RANGES['red2'][1])
            upper_red2 = np.array(Filter.HSV_COLOR_RANGES['red2'][0])

            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = mask1 + mask2
        else:
            lower = np.array(Filter.HSV_COLOR_RANGES[self.color][1])
            upper = np.array(Filter.HSV_COLOR_RANGES[self.color][0])
            mask = cv2.inRange(hsv, lower, upper)

        return mask

    @property
    def get_filtered(self):
        self.img[self.mask != 0] = Filter.RGB_COLORS[self.color]
        return self.img

    @property
    def get_PID_value(self):
        mask_T = self.mask.T
        col_count = []
        # count how many color pixels are in each column
        for col in mask_T:
            col_count.append(np.count_nonzero(col))

        # find largest location
        max_column = np.argmax(col_count)

        # largest value
        max_amount = col_count[max_column]
        # distance from center
        offset = max_column - len(mask_T)/2

        return offset, max_amount

    @property
    def mean_distance(self):
        return np.nanmean(self.depth[self.mask != 0])


if __name__ == "__main__":
    imgs = ['left.png', 'right.png']
    for name in imgs:
        img = cv2.imread(name)
        f = Filter(img, 'green', depth=None)
    	mask = f.get_mask
        print(mask)
        # cv2.imshow("f_img", f_img)
        # cv2.waitKey(0)
        # print(name)
        # print(Filter.get_PID_value(mask, 'green'))
    
    print("done")