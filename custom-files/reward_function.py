import math


def reward_function(params):
    print('params =>', params)
    all_wheels_on_track = params['all_wheels_on_track']
    reward = 1e-3
    if all_wheels_on_track:
        distance_from_center = params['distance_from_center']
        reward_distance = math.exp(-distance_from_center)

        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']

        prev_point = (params['x'], params['y'])
        l_waypoints = len(waypoints)
        next_point = waypoints[(closest_waypoints[0] + (l_waypoints // 10)) % l_waypoints]
        track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        track_direction = math.degrees(track_direction)
        heading = params['heading']
        steering_angle = params['steering_angle']
        heading = heading + steering_angle
        direction_diff = abs(track_direction - heading)
        if direction_diff > 180:
            direction_diff = 360 - direction_diff
        reward_direction = math.exp(-direction_diff)

        prev_point = waypoints[closest_waypoints[1]]
        next_point = waypoints[(closest_waypoints[1] + (l_waypoints // 10)) % l_waypoints]
        track_curve = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        track_curve = math.degrees(track_curve)
        max_v = 4
        min_v = 1
        target_speed = max_v - (track_curve * (max_v - min_v) / 90)
        speed = params['speed']
        speed_diff = abs(target_speed - speed)
        reward_speed = math.exp(-speed_diff)

        reward = reward_distance + 2 * reward_direction + 4 * reward_speed

        steps = params['steps']
        progress = params['progress']
        TOTAL_NUM_STEPS = 180
        if (steps % 60) == 0 and progress > (steps / TOTAL_NUM_STEPS) * 100:
            reward += 10
        print('reward =>', reward)

    return float(min(1e3, max(reward, 1e-3)))
