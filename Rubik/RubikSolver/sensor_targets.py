# The expected ratios for each sensor at 75 brightness
RED_TARGET_RATIOS_75 = [
    [4.161, 3.266, 0.785],  # sensor 0
    [3.574, 2.956, 0.827],  # sensor 1
    [4.156, 3.152, 0.775],  # sensor 2
    [3.673, 2.893, 0.787],  # sensor 3
    [4.303, 3.557, 0.827],  # sensor 4
    [2.791, 2.608, 0.934],  # sensor 5
    [3.684, 2.928, 0.795],  # sensor 6
    [3.855, 3.185, 0.826],  # sensor 7
    [3.03, 2.719, 0.897],  # sensor 8
]
GREEN_TARGET_RATIOS_75 = [
    [0.424, 0.566, 1.388],  # sensor 0
    [0.157, 0.516, 1.448],  # sensor 1
    [0.481, 0.658, 1.368],  # sensor 2
    [0.404, 0.567, 1.405],  # sensor 3
    [0.436, 0.621, 1.424],  # sensor 4
    [0.362, 0.514, 1.42],  # sensor 5
    [0.405, 0.569, 1.406],  # sensor 6
    [0.158, 0.524, 1.465],  # sensor 7
    [0.37, 0.538, 1.154]  # sensor 8
]
BLUE_TARGET_RATIOS_75 = [
    [0.242, 0.252, 1.041],  # sensor 0
    [0.241, 0.257, 1.065],  # sensor 1
    [0.307, 0.333, 1.085],  # sensor 2
    [0.266, 0.295, 1.107],  # sensor 3
    [0.284, 0.31, 1.092],  # sensor 4
    [0.242, 0.263, 1.09],  # sensor 5
    [0.267, 0.296, 1.108],  # sensor 6
    [0.24, 0.248, 1.032],  # sensor 7
    [0.258, 0.281, 1.086],  # sensor 8
]
ORANGE_TARGET_RATIOS_75 = [
    [2.144, 2.123, 0.991],  # sensor 0
    [2.163, 2.21, 1.022],  # sensor 1
    [1.74, 1.697, 0.976],  # sensor 2
    [1.903, 1.868, 0.981],  # sensor 3
    [1.769, 1.767, 0.999],  # sensor 4
    [1.847, 2.008, 1.087],  # sensor 5
    [1.883, 1.785, 0.948],  # sensor 6
    [2.217, 2.225, 1.004],  # sensor 7
    [1.914, 2.039, 1.065],  # sensor 8
]
YELLOW_TARGET_RATIOS_75 = [
    [1.046, 1.273, 1.216],  # sensor 0
    [0.993, 1.192, 1.2],  # sensor 1
    [1.036, 1.13, 1.091],  # sensor 2
    [1.03, 1.215, 1.179],  # sensor 3
    [1.006, 1.173, 1.166],  # sensor 4
    [0.981, 1.172, 1.194],  # sensor 5
    [1.048, 1.247, 1.19],  # sensor 6
    [0.993, 1.28, 1.289],  # sensor 7
    [0.978, 1.276, 1.304],  # sensor 8
]
WHITE_TARGET_RATIOS_75 = [
    [1.053, 1.084, 1.029],  # sensor 0
    [1.012, 1.023, 1.011],  # sensor 1
    [1.048, 1.029, 0.982],  # sensor 2
    [1.042, 1.063, 1.02],  # sensor 3
    [1.026, 1.011, 0.985],  # sensor 4
    [1.005, 1.005, 1.0],  # sensor 5
    [1.058, 1.078, 1.019],  # sensor 6
    [1.019, 1.031, 1.011],  # sensor 7
    [1.007, 1.014, 1.006],  # sensor 8
]

# All the target arrays for 75 brightness in one big array
COLOR_TARGETS_75 = [RED_TARGET_RATIOS_75, GREEN_TARGET_RATIOS_75, BLUE_TARGET_RATIOS_75,
                    YELLOW_TARGET_RATIOS_75, ORANGE_TARGET_RATIOS_75, WHITE_TARGET_RATIOS_75]

# The expected ratios for each sensor at 15 brightness
RED_TARGET_RATIOS_15 = [
[4.027, 3.24, 0.804],  # sensor 0
[3.299, 2.877, 0.872],  # sensor 1
[3.462, 2.943, 0.85],  # sensor 2
[3.225, 2.733, 0.847],  # sensor 3
[3.56, 3.191, 0.896],  # sensor 4
[2.28, 2.245, 0.985],  # sensor 5
[3.374, 2.955, 0.876],  # sensor 6
[2.809, 2.419, 0.861],  # sensor 7
[2.57, 2.452, 0.954],  # sensor 8
]
GREEN_TARGET_RATIOS_15 = [
[0.239, 0.472, 1.973],  # sensor 0
[0.191, 0.404, 2.112],  # sensor 1
[0.24, 0.415, 1.812],  # sensor 2
[0.226, 0.423, 1.875],  # sensor 3
[0.238, 0.451, 1.896],  # sensor 4
[0.157, 0.344, 2.184],  # sensor 5
[0.218, 0.406, 1.863],  # sensor 6
[0.185, 0.395, 2.138],  # sensor 7
[0.165, 0.157, 2.165],  # sensor 8
]
BLUE_TARGET_RATIOS_15 = [
[0.208, 0.145, 0.699],  # sensor 0
[0.149, 0.11, 0.741],  # sensor 1
[0.158, 0.118, 0.747],  # sensor 2
[0.176, 0.12, 0.682],  # sensor 3
[0.166, 0.123, 0.742],  # sensor 4
[0.131, 0.108, 0.826],  # sensor 5
[0.174, 0.119, 0.684],  # sensor 6
[0.17, 0.121, 0.714],  # sensor 7
[0.14, 0.107, 0.761],  # sensor 8
]
ORANGE_TARGET_RATIOS_15 = [
[3.482, 3.654, 1.05],  # sensor 0
[3.154, 3.73, 1.112],  # sensor 1
[3.196, 3.316, 1.038],  # sensor 2
[3.038, 3.283, 1.081],  # sensor 3
[3.147, 3.41, 1.083],  # sensor 4
[2.716, 3.311, 1.219],  # sensor 5
[3.27, 3.429, 1.049],  # sensor 6
[3.265, 3.653, 1.119],  # sensor 7
[3.001, 3.503, 1.167],  # sensor 8
]
YELLOW_TARGET_RATIOS_15 = [
[0.877, 1.338, 1.527],  # sensor 0
[0.781, 1.23, 1.575],  # sensor 1
[0.924, 1.23, 1.331],  # sensor 2
[0.827, 1.174, 1.419],  # sensor 3
[0.913, 1.228, 1.344],  # sensor 4
[0.598, 1.052, 1.76],  # sensor 5
[0.846, 1.189, 1.406],  # sensor 6
[0.57, 1.123, 1.97],  # sensor 7
[0.637, 1.147, 1.801],  # sensor 8
]
WHITE_TARGET_RATIOS_15 = [
[0.916, 0.972, 1.06],  # sensor 0
[0.825, 0.869, 1.053],  # sensor 1
[0.969, 0.996, 1.027],  # sensor 2
[0.88, 0.919, 1.044],  # sensor 3
[0.963, 0.987, 1.025],  # sensor 4
[0.656, 0.699, 1.065],  # sensor 5
[0.895, 0.939, 1.049],  # sensor 6
[0.659, 0.71, 1.077],  # sensor 7
[0.763, 0.819, 1.073],  # sensor 8
]

# All the target arrays for 15 brightness in one big array
COLOR_TARGETS_15 = [RED_TARGET_RATIOS_15, GREEN_TARGET_RATIOS_15, BLUE_TARGET_RATIOS_15,
                    YELLOW_TARGET_RATIOS_15, ORANGE_TARGET_RATIOS_15, WHITE_TARGET_RATIOS_15]
