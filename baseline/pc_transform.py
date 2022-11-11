import torch
from typing import List, Tuple
from util import las_to_pc, project_point_cloud

default_views = [
    (0, 0, 0),
    (0, 180, 0),
    (0, 90, 0),
    (90, 90, 0),
    (180, 90, 0),
    (270, 90, 0),
]

class ToPointCloud:
    def __init__(
        self,
        hide_class_10: bool = False,
    ):
        self.hide_class_10 = hide_class_10

    def __call__(self, las):
        pc, _ = las_to_pc(las, self.hide_class_10)
        return pc

class ProjectPointCloud:
    def __init__(
        self,
        views: List[Tuple[float, float, float]] = default_views,
    ):
        self.views = views

    def __call__(self, x):
        proj = []
        for xrot, yrot, zrot in self.views:
            proj.append(project_point_cloud(x, xrot=xrot, yrot=yrot, zrot=zrot))
        proj = torch.stack(proj)
        return proj

class ExpandChannels:
    def __init__(
        self,
        channels: int = 3,
    ):
        self.channels = channels

    def __call__(self, x):
        x = x.unsqueeze(dim=-3)
        x = x.repeat((1, self.channels, 1, 1))
        return x






# from __future__ import (
#     division,
#     absolute_import,
#     with_statement,
#     print_function,
#     unicode_literals,
# )
# import numpy as np
# from typing import List, Tuple







# def angle_axis(angle, axis):
#     # type: (float, np.ndarray) -> float
#     r"""Returns a 4x4 rotation matrix that performs a rotation around axis by angle

#     Parameters
#     ----------
#     angle : float
#         Angle to rotate by
#     axis: np.ndarray
#         Axis to rotate about

#     Returns
#     -------
#     torch.Tensor
#         3x3 rotation matrix
#     """
#     u = axis / np.linalg.norm(axis)
#     cosval, sinval = np.cos(angle), np.sin(angle)

#     # yapf: disable
#     cross_prod_mat = np.array([[0.0, -u[2], u[1]],
#                                 [u[2], 0.0, -u[0]],
#                                 [-u[1], u[0], 0.0]])

#     R = torch.from_numpy(
#         cosval * np.eye(3)
#         + sinval * cross_prod_mat
#         + (1.0 - cosval) * np.outer(u, u)
#     )
#     # yapf: enable
#     return R.float()


# class PCScale:
#     def __init__(self, lo=0.8, hi=1.25):
#         self.lo, self.hi = lo, hi

#     def __call__(self, points):
#         scaler = np.random.uniform(self.lo, self.hi)
#         points[:, 0:3] *= scaler
#         return points


# class PCRotate:
#     def __init__(self, axis=np.array([0.0, 1.0, 0.0])):
#         self.axis = axis

#     def __call__(self, points):
#         rotation_angle = np.random.uniform() * 2 * np.pi
#         rotation_matrix = angle_axis(rotation_angle, self.axis)

#         normals = points.size(1) > 3
#         if not normals:
#             return torch.matmul(points, rotation_matrix.t())
#         else:
#             pc_xyz = points[:, 0:3]
#             pc_normals = points[:, 3:]
#             points[:, 0:3] = torch.matmul(pc_xyz, rotation_matrix.t())
#             points[:, 3:] = torch.matmul(pc_normals, rotation_matrix.t())

#             return points


# class PCRotatePerturbation:
#     def __init__(self, angle_sigma=0.06, angle_clip=0.18):
#         self.angle_sigma, self.angle_clip = angle_sigma, angle_clip

#     def _get_angles(self):
#         angles = np.clip(
#             self.angle_sigma * np.random.randn(3), -self.angle_clip, self.angle_clip
#         )

#         return angles

#     def __call__(self, points):
#         angles = self._get_angles()
#         Rx = angle_axis(angles[0], np.array([1.0, 0.0, 0.0]))
#         Ry = angle_axis(angles[1], np.array([0.0, 1.0, 0.0]))
#         Rz = angle_axis(angles[2], np.array([0.0, 0.0, 1.0]))

#         rotation_matrix = torch.matmul(torch.matmul(Rz, Ry), Rx)

#         normals = points.size(1) > 3
#         if not normals:
#             return torch.matmul(points, rotation_matrix.t())
#         else:
#             pc_xyz = points[:, 0:3]
#             pc_normals = points[:, 3:]
#             points[:, 0:3] = torch.matmul(pc_xyz, rotation_matrix.t())
#             points[:, 3:] = torch.matmul(pc_normals, rotation_matrix.t())

#             return points


# class PCJitter:
#     def __init__(self, std=0.01, clip=0.05):
#         self.std, self.clip = std, clip

#     def __call__(self, points):
#         jittered_data = (
#             points.new(points.size(0), 3)
#             .normal_(mean=0.0, std=self.std)
#             .clamp_(-self.clip, self.clip)
#         )
#         points[:, 0:3] += jittered_data
#         return points


# class PCTranslate:
#     def __init__(self, translate_range=0.1):
#         self.translate_range = translate_range

#     def __call__(self, points):
#         translation = np.random.uniform(-self.translate_range, self.translate_range)
#         points[:, 0:3] += translation
#         return points

# class LASToPC:
#     def __init__(self, hide_class_10: bool = True):
#         self.hide_class_10 = hide_class_10

#     def __call__(self, las):
#         mask = las.classification != (10 if self.hide_class_10 else -1)
#         x = (las.points.X * las.header.scale[0] + las.header.offset[0])[mask]
#         y = (las.points.Y * las.header.scale[1] + las.header.offset[1])[mask]
#         z = (las.points.Z * las.header.scale[2] + las.header.offset[2])[mask]
#         pc = torch.Tensor([x.tolist(), y.tolist(), z.tolist()])
#         return pc

# class PCRandomInputDropout:
#     def __init__(self, max_dropout_ratio=0.875):
#         assert max_dropout_ratio >= 0 and max_dropout_ratio < 1
#         self.max_dropout_ratio = max_dropout_ratio

#     def __call__(self, points):
#         pc = points.numpy()

#         dropout_ratio = np.random.random() * self.max_dropout_ratio  # 0~0.875
#         drop_idx = np.where(np.random.random((pc.shape[0])) <= dropout_ratio)[0]
#         if len(drop_idx) > 0:
#             pc[drop_idx] = pc[0]  # set to the first point

#         return torch.from_numpy(pc).float()
