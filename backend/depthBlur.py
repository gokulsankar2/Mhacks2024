def depth_dependent_blur(image, depth_map):
    blurred = np.zeros_like(image)
    for depth in np.unique(depth_map):
        mask = depth_map == depth
        kernel_size = int(depth * blur_factor)  # blur_factor is a constant you'd need to tune
        kernel_size = max(1, kernel_size if kernel_size % 2 else kernel_size + 1)
        blurred_region = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        blurred[mask] = blurred_region[mask]
    return blurred