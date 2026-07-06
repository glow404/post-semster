"""SIFT 特征提取与匹配模块。

脚本作用：
1. 读取两张小面积指纹灰度图；
2. 可选使用 CLAHE 增强局部对比度；
3. 使用 SIFT 提取关键点和描述子；
4. 使用 BFMatcher 和 Lowe 比率测试筛选匹配；
5. 可选使用 RANSAC 过滤几何不一致匹配；
6. 输出用于指纹验证的相似度分数。
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class SiftMatchResult:
    """保存一对图像的 SIFT 匹配结果。"""

    score: float
    num_keypoints_img1: int
    num_keypoints_img2: int
    raw_matches: int
    good_matches: int
    used_ransac: bool


def str_to_bool(value: str) -> bool:
    """将命令行字符串解析为布尔值。"""
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def create_sift() -> cv2.SIFT:
    """创建 OpenCV SIFT 提取器，并在环境不支持时给出明确提示。"""
    if hasattr(cv2, "SIFT_create"):
        return cv2.SIFT_create()
    if hasattr(cv2, "xfeatures2d") and hasattr(cv2.xfeatures2d, "SIFT_create"):
        return cv2.xfeatures2d.SIFT_create()
    raise RuntimeError(
        "OpenCV SIFT is unavailable. Please install opencv-contrib-python."
    )


def read_gray_image(image_path: Path, use_clahe: bool = False) -> np.ndarray:
    """读取灰度图，并按需使用 CLAHE 增强。"""
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Failed to read image: {image_path}")

    if use_clahe:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        image = clahe.apply(image)
    return image


def extract_sift_features(
    image: np.ndarray,
    sift: cv2.SIFT | None = None,
) -> tuple[tuple[cv2.KeyPoint, ...], np.ndarray | None]:
    """从单张图像中提取 SIFT 关键点和描述子。"""
    extractor = sift if sift is not None else create_sift()
    keypoints, descriptors = extractor.detectAndCompute(image, None)
    return tuple(keypoints), descriptors


def lowe_ratio_matches(
    descriptors1: np.ndarray,
    descriptors2: np.ndarray,
    ratio: float = 0.75,
) -> tuple[list[cv2.DMatch], int]:
    """使用 BFMatcher 匹配描述子，并用 Lowe 比率测试过滤弱匹配。"""
    matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    knn_matches = matcher.knnMatch(descriptors1, descriptors2, k=2)

    # Lowe 比率测试保留“最佳匹配明显优于次佳匹配”的结果，减少误匹配。
    good_matches: list[cv2.DMatch] = []
    for match_group in knn_matches:
        if len(match_group) < 2:
            continue
        best, second_best = match_group
        if best.distance < ratio * second_best.distance:
            good_matches.append(best)
    return good_matches, len(knn_matches)


def filter_matches_with_ransac(
    keypoints1: tuple[cv2.KeyPoint, ...],
    keypoints2: tuple[cv2.KeyPoint, ...],
    matches: list[cv2.DMatch],
    reproj_threshold: float = 5.0,
) -> tuple[list[cv2.DMatch], bool]:
    """在匹配数量足够时使用 RANSAC 过滤几何不一致匹配。"""
    if len(matches) < 4:
        return matches, False

    points1 = np.float32([keypoints1[match.queryIdx].pt for match in matches]).reshape(-1, 1, 2)
    points2 = np.float32([keypoints2[match.trainIdx].pt for match in matches]).reshape(-1, 1, 2)
    _, mask = cv2.findHomography(points1, points2, cv2.RANSAC, reproj_threshold)
    if mask is None:
        return matches, False

    filtered = [match for match, keep in zip(matches, mask.ravel().tolist()) if keep]
    return filtered, True


def compute_sift_score(
    img1_path: Path,
    img2_path: Path,
    use_clahe: bool = False,
    use_ransac: bool = False,
    ratio: float = 0.75,
    ransac_reproj_threshold: float = 5.0,
    sift: cv2.SIFT | None = None,
) -> SiftMatchResult:
    """计算两张指纹图像的 SIFT 匹配相似度分数。"""
    extractor = sift if sift is not None else create_sift()
    img1 = read_gray_image(img1_path, use_clahe=use_clahe)
    img2 = read_gray_image(img2_path, use_clahe=use_clahe)

    keypoints1, descriptors1 = extract_sift_features(img1, extractor)
    keypoints2, descriptors2 = extract_sift_features(img2, extractor)
    num_keypoints1 = len(keypoints1)
    num_keypoints2 = len(keypoints2)

    # 小面积图像可能检测不到关键点；此时无法匹配，直接返回 0 分。
    if descriptors1 is None or descriptors2 is None or num_keypoints1 == 0 or num_keypoints2 == 0:
        return SiftMatchResult(
            score=0.0,
            num_keypoints_img1=num_keypoints1,
            num_keypoints_img2=num_keypoints2,
            raw_matches=0,
            good_matches=0,
            used_ransac=False,
        )

    good_matches, raw_matches = lowe_ratio_matches(descriptors1, descriptors2, ratio=ratio)
    used_ransac_flag = False
    if use_ransac:
        good_matches, used_ransac_flag = filter_matches_with_ransac(
            keypoints1,
            keypoints2,
            good_matches,
            reproj_threshold=ransac_reproj_threshold,
        )

    # 用较大的关键点数量归一化，避免关键点数量差异导致分数不可比。
    denominator = max(num_keypoints1, num_keypoints2, 1)
    score = len(good_matches) / denominator
    return SiftMatchResult(
        score=float(score),
        num_keypoints_img1=num_keypoints1,
        num_keypoints_img2=num_keypoints2,
        raw_matches=raw_matches,
        good_matches=len(good_matches),
        used_ransac=used_ransac_flag,
    )


def parse_args() -> argparse.Namespace:
    """解析命令行参数，用于快速计算单个图像对分数。"""
    parser = argparse.ArgumentParser(description="Compute SIFT matching score for one image pair.")
    parser.add_argument("--img1", type=Path, required=True, help="First image path.")
    parser.add_argument("--img2", type=Path, required=True, help="Second image path.")
    parser.add_argument("--use_clahe", type=str_to_bool, default=False, help="Apply CLAHE. Default: false.")
    parser.add_argument("--use_ransac", type=str_to_bool, default=False, help="Apply RANSAC. Default: false.")
    parser.add_argument("--ratio", type=float, default=0.75, help="Lowe ratio threshold.")
    parser.add_argument(
        "--ransac_reproj_threshold",
        type=float,
        default=5.0,
        help="RANSAC reprojection threshold.",
    )
    return parser.parse_args()


def main() -> None:
    """脚本入口：计算并打印一对图像的 SIFT 匹配结果。"""
    args = parse_args()
    result = compute_sift_score(
        args.img1,
        args.img2,
        use_clahe=args.use_clahe,
        use_ransac=args.use_ransac,
        ratio=args.ratio,
        ransac_reproj_threshold=args.ransac_reproj_threshold,
    )
    for key, value in asdict(result).items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
