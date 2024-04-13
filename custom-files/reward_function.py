import math


def reward_function(params):
    print('params =>', params)
    all_wheels_on_track = params['all_wheels_on_track']
    reward = 1e-3
    if all_wheels_on_track:
        distance_from_center = params['distance_from_center']
        track_width = params['track_width']
        reward_distance = 1 - (distance_from_center / (0.5 * track_width))

        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']

        prev_point = (params['x'], params['y'])
        l_waypoints = len(waypoints)
        forward_waypoint = l_waypoints // 10
        next_point = waypoints[(closest_waypoints[0] + forward_waypoint) % l_waypoints]
        track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        track_direction = round(math.degrees(track_direction))
        heading = params['heading'] + params['steering_angle']
        direction_diff = abs(track_direction - heading)
        if direction_diff > 180:
            direction_diff = 360 - direction_diff
        reward_direction = math.cos(math.radians(direction_diff))

        prev_point = waypoints[closest_waypoints[1]]
        next_point = waypoints[(closest_waypoints[1] + forward_waypoint) % l_waypoints]
        track_curve = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        track_curve = abs(round(math.degrees(track_curve), 1))
        max_v = 4
        min_v = 1
        target_speed = max_v - ((max_v - min_v) / 90) * track_curve
        speed = params['speed']
        speed_diff = abs(target_speed - speed)
        reward_speed = math.exp(-speed_diff)

        # reward = reward_distance + 4 * reward_direction + 2 * reward_speed
        reward = reward_direction * (4 + (2 * reward_speed))

        # print('reward_distance: ', reward_distance)
        print('reward_direction: ', 4 * reward_direction)
        print('reward_speed: ', 2 * reward_speed)

        steps = params['steps']
        progress = params['progress']
        TOTAL_NUM_STEPS = 180
        if (steps % 60) == 0 and progress > (steps / TOTAL_NUM_STEPS) * 100:
            reward += 5
            print('reward +10 for efficiency')
        print('reward final result: ', reward)

    return float(min(1e3, max(reward, 1e-3)))
