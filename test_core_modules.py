import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    print("=" * 60)
    print("测试核心模块导入...")
    print("=" * 60)

    from app.models.schemas import JansenParameters, TerrainData, TerrainPoint, ObstacleAssessmentRequest
    print("✅ 数据模型模块导入成功")

    from app.simulation.jansen_linkage import JansenLinkageSolver
    print("✅ Jansen连杆模块导入成功")

    from app.simulation.multibody_dynamics import MultibodyDynamics
    print("✅ 多体动力学模块导入成功")

    from app.simulation.gait_engine import GaitEngine
    print("✅ 步态引擎模块导入成功")

    from app.analysis.stability_analysis import StabilityAnalyzer
    print("✅ 稳定性分析模块导入成功")

    from app.analysis.obstacle_analysis import ObstacleAnalyzer
    print("✅ 越障分析模块导入成功")

    from app.analysis.terrain_recognition import TerrainRecognizer
    print("✅ 地形识别模块导入成功")

    default_params = JansenParameters()

    print("\n" + "=" * 60)
    print("测试Jansen连杆求解...")
    print("=" * 60)

    jansen = JansenLinkageSolver(default_params)
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        joints = jansen.solve_linkage(angle)
        foot = joints['foot_tip']
        print(f"  曲柄角度 {angle:3d}°: 足端位置 ({foot.x:.2f}, {foot.y:.2f}, {foot.z:.2f}) mm")
    print("✅ Jansen连杆求解成功")

    print("\n" + "=" * 60)
    print("测试足端轨迹生成...")
    print("=" * 60)

    trajectory = jansen.generate_foot_trajectory(0, 360, 360)
    y_coords = [p.y for p in trajectory]
    x_coords = [p.x for p in trajectory]
    print(f"  轨迹点数: {len(trajectory)}")
    print(f"  足端抬升高度: {max(y_coords) - min(y_coords):.2f} mm")
    print(f"  步幅: {max(x_coords) - min(x_coords):.2f} mm")
    print("✅ 足端轨迹生成成功")

    print("\n" + "=" * 60)
    print("测试步态参数计算...")
    print("=" * 60)

    gait_params = jansen.calculate_gait_parameters(0.0)
    print(f"  步幅: {gait_params['stride_length']:.2f} mm")
    print(f"  步频: {gait_params['cadence']:.1f} 步/分钟")
    print(f"  支撑相比例: {gait_params['support_phase']:.1f}%")
    print(f"  摆动相比例: {gait_params['swing_phase']:.1f}%")
    print(f"  足端离地高度: {gait_params['foot_clearance']:.2f} mm")
    print("✅ 步态参数计算成功")

    print("\n" + "=" * 60)
    print("测试多体动力学...")
    print("=" * 60)

    dynamics = MultibodyDynamics(default_params)
    joints = jansen.solve_linkage(90.0)
    com_positions = dynamics.calculate_link_centers_of_mass(joints)
    total_com = dynamics.calculate_total_center_of_mass(com_positions, 0.0)
    print(f"  总重心位置: ({total_com.x:.2f}, {total_com.y:.2f}, {total_com.z:.2f}) mm")

    forces = dynamics.calculate_joint_forces(joints, com_positions, 0.0)
    zmp = dynamics.calculate_zero_moment_point(total_com, forces, joints, 0.0)
    print(f"  零力矩点(ZMP): ({zmp.x:.2f}, {zmp.y:.2f}) mm")

    support_polygon = dynamics.calculate_support_polygon(joints)
    stability_margin = dynamics.calculate_stability_margin(zmp, support_polygon)
    print(f"  稳定裕度: {stability_margin:.2f} mm")

    torques = dynamics.calculate_joint_torques(90.0, 0.0, 0.0)
    print(f"  曲柄力矩: {torques['crank']:.2f} N·mm")
    print(f"  膝关节力矩: {torques['knee']:.2f} N·mm")
    print("✅ 多体动力学计算成功")

    print("\n" + "=" * 60)
    print("测试步态引擎...")
    print("=" * 60)

    gait = GaitEngine(default_params)
    gait_result = gait.compute_gait_analysis(
        device_id='woodox-001',
        crank_angle=0.0,
        body_inclination=0.0
    )
    print(f"  设备ID: {gait_result.device_id}")
    print(f"  步幅: {gait_result.stride_length:.2f} mm")
    print(f"  步频: {gait_result.cadence:.1f} 步/分钟")
    print(f"  稳定裕度: {gait_result.stability_margin:.2f}")
    print("✅ 步态引擎计算成功")

    print("\n" + "=" * 60)
    print("测试稳定性分析...")
    print("=" * 60)

    stability = StabilityAnalyzer(default_params)
    static_result = stability.analyze_static_stability(
        crank_angle=0.0,
        body_inclination=0.0,
        num_legs=4
    )
    print(f"  稳定裕度: {static_result['stability_margin']:.2f} mm")
    print(f"  稳定性等级: {static_result['stability_level']}")
    print(f"  是否稳定: {static_result['is_stable']}")

    critical_angle = stability.calculate_critical_inclination(0.0, 'pitch')
    print(f"  临界倾角(俯仰): {critical_angle:.2f}°")
    print("✅ 稳定性分析成功")

    print("\n" + "=" * 60)
    print("测试地形识别...")
    print("=" * 60)

    terrain_recognizer = TerrainRecognizer()
    terrain_points = []
    for i in range(20):
        for j in range(20):
            elev = 0.0
            if 8 <= i <= 12 and 8 <= j <= 12:
                elev = 80.0
            terrain_points.append(TerrainPoint(
                x=i * 100.0,
                y=j * 100.0,
                elevation=elev
            ))
    
    terrain_data = TerrainData(
        grid_size=50,
        resolution=100.0,
        points=terrain_points
    )
    
    terrain_analysis = terrain_recognizer.analyze_terrain(terrain_data)
    print(f"  地形类型: {terrain_analysis['terrain_type']}")
    print(f"  地形粗糙度: {terrain_analysis['roughness']:.2f}")
    print(f"  障碍物数量: {len(terrain_analysis['obstacles'])}")
    print(f"  可通行性评分: {terrain_analysis['traversability_score']:.1f}%")
    print("✅ 地形识别成功")

    print("\n" + "=" * 60)
    print("测试越障能力分析...")
    print("=" * 60)

    obstacle = ObstacleAnalyzer(default_params)
    
    sim_result = obstacle.simulate_obstacle_traversal(
        obstacle_height=50.0,
        obstacle_width=200.0,
        approach_speed=30.0,
        body_inclination=0.0
    )
    print(f"  是否成功通过: {sim_result['successful']}")
    print(f"  最小间隙: {sim_result['minimum_clearance']:.2f} mm")
    print(f"  最大应力: {sim_result['maximum_stress']:.2f}")
    print(f"  所需能量: {sim_result['energy_required']:.2f}")
    print("✅ 越障能力分析成功")

    print("\n" + "=" * 60)
    print("测试步态相位识别...")
    print("=" * 60)

    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        phase = gait.get_gait_phase(angle)
        status = "支撑" if phase['is_support_phase'] else "摆动"
        print(f"  曲柄角度 {angle:3d}°: {phase['phase_name']} ({status}) - {phase['gait_cycle_percentage']:.1f}%")
    print("✅ 步态相位识别成功")

    print("\n" + "=" * 60)
    print("测试稳定性椭球...")
    print("=" * 60)

    ellipsoid = stability.compute_stability_ellipsoid(0.0)
    print(f"  最大安全横滚角: {ellipsoid['max_safe_roll']:.2f}°")
    print(f"  最大安全俯仰角: {ellipsoid['max_safe_pitch']:.2f}°")
    print("✅ 稳定性椭球计算成功")

    print("\n" + "=" * 60)
    print("🎉 所有核心模块测试通过！")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
