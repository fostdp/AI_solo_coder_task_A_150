import numpy as np
from typing import Tuple, List, Dict
import math

from app.models.schemas import JansenParameters, Point3D, LegPosition, LinkageState


class JansenLinkageSolver:
    def __init__(self, params: JansenParameters):
        self.params = params
        self.joint_names = [
            'crank_pivot',
            'crank_pin',
            'rocker_pivot',
            'upper_rocker_pin',
            'lower_rocker_pin',
            'coupler_pin',
            'knee_joint',
            'ankle_joint',
            'foot_tip'
        ]

    def solve_linkage(self, crank_angle_deg: float) -> Dict[str, Point3D]:
        a = self.params.crank_length
        b = self.params.rocker_length
        c = self.params.coupler_length
        d = self.params.ground_link
        
        theta = np.radians(crank_angle_deg)
        
        joints = {}
        
        joints['crank_pivot'] = Point3D(x=0.0, y=0.0, z=0.0)
        joints['rocker_pivot'] = Point3D(x=d, y=0.0, z=0.0)
        
        joints['crank_pin'] = Point3D(
            x=a * np.cos(theta),
            y=a * np.sin(theta),
            z=0.0
        )
        
        dx = joints['crank_pin'].x - joints['rocker_pivot'].x
        dy = joints['crank_pin'].y - joints['rocker_pivot'].y
        dist = np.sqrt(dx**2 + dy**2)
        
        if dist > (b + c) or dist < abs(b - c):
            dist = np.clip(dist, abs(b - c), b + c)
        
        cos_phi = (b**2 + dist**2 - c**2) / (2 * b * dist)
        cos_phi = np.clip(cos_phi, -1.0, 1.0)
        phi = np.arccos(cos_phi)
        
        gamma = np.arctan2(dy, dx)
        rocker_angle = gamma - phi
        
        joints['upper_rocker_pin'] = Point3D(
            x=joints['rocker_pivot'].x + b * np.cos(rocker_angle),
            y=joints['rocker_pivot'].y + b * np.sin(rocker_angle),
            z=0.0
        )
        
        lower_rocker_ratio = 0.6
        joints['lower_rocker_pin'] = Point3D(
            x=joints['rocker_pivot'].x + b * lower_rocker_ratio * np.cos(rocker_angle),
            y=joints['rocker_pivot'].y + b * lower_rocker_ratio * np.sin(rocker_angle),
            z=0.0
        )
        
        cos_psi = (c**2 + dist**2 - b**2) / (2 * c * dist)
        cos_psi = np.clip(cos_psi, -1.0, 1.0)
        psi = np.arccos(cos_psi)
        coupler_angle = gamma + psi
        
        joints['coupler_pin'] = Point3D(
            x=joints['crank_pin'].x + c * np.cos(coupler_angle),
            y=joints['crank_pin'].y + c * np.sin(coupler_angle),
            z=0.0
        )
        
        thigh_length = self.params.rocker_length * 0.8
        shin_length = self.params.rocker_length * 0.9
        
        hip_to_knee = joints['coupler_pin']
        knee_direction = np.arctan2(
            hip_to_knee.y - joints['lower_rocker_pin'].y,
            hip_to_knee.x - joints['lower_rocker_pin'].x
        ) + np.pi / 6
        
        joints['knee_joint'] = Point3D(
            x=hip_to_knee.x + thigh_length * 0.5 * np.cos(knee_direction),
            y=hip_to_knee.y + thigh_length * 0.5 * np.sin(knee_direction),
            z=0.0
        )
        
        ankle_direction = knee_direction + np.pi / 4
        joints['ankle_joint'] = Point3D(
            x=joints['knee_joint'].x + shin_length * 0.6 * np.cos(ankle_direction),
            y=joints['knee_joint'].y + shin_length * 0.6 * np.sin(ankle_direction),
            z=0.0
        )
        
        foot_direction = ankle_direction + np.pi / 8
        joints['foot_tip'] = Point3D(
            x=joints['ankle_joint'].x + 50 * np.cos(foot_direction),
            y=joints['ankle_joint'].y + 50 * np.sin(foot_direction),
            z=0.0
        )
        
        return joints

    def calculate_leg_position(self, joints: Dict[str, Point3D]) -> LegPosition:
        return LegPosition(
            hip=joints['coupler_pin'],
            knee=joints['knee_joint'],
            ankle=joints['ankle_joint'],
            foot=joints['foot_tip']
        )

    def calculate_foot_velocity(
        self,
        crank_angle: float,
        delta_angle: float = 0.1
    ) -> Point3D:
        joints1 = self.solve_linkage(crank_angle)
        joints2 = self.solve_linkage(crank_angle + delta_angle)
        
        dt = delta_angle / (self.params.crank_speed * np.pi / 180)
        
        foot1 = joints1['foot_tip']
        foot2 = joints2['foot_tip']
        
        return Point3D(
            x=(foot2.x - foot1.x) / dt,
            y=(foot2.y - foot1.y) / dt,
            z=(foot2.z - foot1.z) / dt
        )

    def get_linkage_state(self, crank_angle: float) -> LinkageState:
        joints = self.solve_linkage(crank_angle)
        leg_pos = self.calculate_leg_position(joints)
        foot_vel = self.calculate_foot_velocity(crank_angle)
        
        joint_positions = [joints[name] for name in self.joint_names]
        
        return LinkageState(
            crank_angle=crank_angle,
            joint_positions=joint_positions,
            leg_position=leg_pos,
            foot_velocity=foot_vel
        )

    def generate_foot_trajectory(
        self,
        start_angle: float = 0.0,
        end_angle: float = 360.0,
        steps: int = 360
    ) -> List[Point3D]:
        trajectory = []
        angles = np.linspace(start_angle, end_angle, steps)
        
        for angle in angles:
            joints = self.solve_linkage(angle)
            trajectory.append(joints['foot_tip'])
        
        return trajectory

    def calculate_gait_parameters(
        self,
        crank_angle: float
    ) -> Dict[str, float]:
        trajectory = self.generate_foot_trajectory(0, 360, 720)
        
        y_coords = [p.y for p in trajectory]
        x_coords = [p.x for p in trajectory]
        
        min_y = min(y_coords)
        ground_contact_indices = [i for i, y in enumerate(y_coords) if y < min_y + 5]
        
        if ground_contact_indices:
            support_start = ground_contact_indices[0] * 0.5
            support_end = ground_contact_indices[-1] * 0.5
            support_phase = support_end - support_start
        else:
            support_phase = 180
        
        swing_phase = 360 - support_phase
        support_ratio = (support_phase / 360) * 100
        swing_ratio = (swing_phase / 360) * 100
        
        stride_length = max(x_coords) - min(x_coords)
        
        cadence = (self.params.crank_speed / 360) * 60
        
        foot_clearance = max(y_coords) - min_y
        
        return {
            'stride_length': stride_length,
            'cadence': cadence,
            'support_phase': support_ratio,
            'swing_phase': swing_ratio,
            'foot_clearance': foot_clearance,
            'step_height': max(y_coords) - min(y_coords)
        }

    def is_foot_on_ground(self, crank_angle: float, ground_y: float = 0.0) -> bool:
        joints = self.solve_linkage(crank_angle)
        foot_y = joints['foot_tip'].y
        return foot_y <= ground_y + 2

    def get_link_angles(self, crank_angle: float) -> Dict[str, float]:
        joints = self.solve_linkage(crank_angle)
        
        def angle_between(p1: Point3D, vertex: Point3D, p2: Point3D) -> float:
            v1 = np.array([p1.x - vertex.x, p1.y - vertex.y])
            v2 = np.array([p2.x - vertex.x, p2.y - vertex.y])
            cos_ang = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_ang = np.clip(cos_ang, -1.0, 1.0)
            return np.degrees(np.arccos(cos_ang))
        
        return {
            'crank_angle': crank_angle,
            'rocker_angle': angle_between(
                joints['rocker_pivot'], joints['upper_rocker_pin'], joints['coupler_pin']
            ),
            'knee_angle': angle_between(
                joints['coupler_pin'], joints['knee_joint'], joints['ankle_joint']
            ),
            'ankle_angle': angle_between(
                joints['knee_joint'], joints['ankle_joint'], joints['foot_tip']
            )
        }
