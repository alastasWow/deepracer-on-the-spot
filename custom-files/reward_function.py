import math

MAX_TRACK_CURVE = 90
# TOTAL_NUM_STEPS = 120
MAX_SPEED = 3.5
MIN_SPEED = 0.5
DELTA_DIST = 0.05
FORCAST = 20


def dist(p1, p2, p3):
    return abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])) / math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


class Reward:
    def __init__(self):
        self.prev_speed = 0

    def reward_funciton(self, params):
        # distance
        # distance_from_center = params['distance_from_center']
        # track_width = params['track_width']
        # reward_distance = 1 - (distance_from_center / (0.5 * track_width))
        # print('reward_distance: ', reward_distance)

        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        potential_forcast_index = (closest_waypoints[1] + FORCAST) % len(waypoints)
        car_pos = (params['x'], params['y'])
        if potential_forcast_index > closest_waypoints[1]:
            waypoints_middle = [i for i in range(potential_forcast_index, closest_waypoints[1] - 1, -1)]
        else:
            waypoints_middle = \
                [i for i in range(potential_forcast_index, -1, -1)] \
                + [i for i in range(len(waypoints) - 1, closest_waypoints[1] - 1, -1)]
        for i in range(len(waypoints_middle)):
            out_of_track = False
            for j in range(i + 1, len(waypoints_middle)):
                d = dist(waypoints[waypoints_middle[i]], car_pos, waypoints[waypoints_middle[j]])
                if d - (params['track_width'] / 2) >= DELTA_DIST:
                    out_of_track = True
                    break
            if not out_of_track:
                potential_forcast_index = waypoints_middle[i]
                break
        next_point = waypoints[potential_forcast_index]
        print('projected waypoint: ', potential_forcast_index)

        # direction
        track_direction = math.atan2(next_point[1] - car_pos[1], next_point[0] - car_pos[0])
        track_direction = math.degrees(track_direction)
        heading = params['heading'] + params['steering_angle']
        direction_diff = abs(track_direction - heading)
        if direction_diff > 180:
            direction_diff = 360 - direction_diff
        print('direction_diff in degrees: ', direction_diff)
        reward_direction = direction_diff / 180
        print('reward_direction formula: direction_diff / 180: ', reward_direction)

        # orientation
        p_w = waypoints[closest_waypoints[0]]
        n_w = waypoints[closest_waypoints[1]]
        track_curve = math.atan2(n_w[1] - p_w[1], n_w[0] - p_w[0]) - math.atan2(next_point[1] - p_w[1], next_point[0] - p_w[0])
        track_curve = abs(math.degrees(track_curve))
        if track_curve > 180:
            track_curve = 360 - track_curve
        target_speed = MAX_SPEED - ((MAX_SPEED - MIN_SPEED) / MAX_TRACK_CURVE) * track_curve
        speed = params['speed']
        speed_diff = abs(target_speed - speed)
        print('speed_diff: ', speed_diff)
        reward_speed = speed_diff / (MAX_SPEED - MIN_SPEED)
        print('reward_speed formula: speed_diff / (MAX_SPEED - MIN_SPEED): ', reward_speed)
        print(f'formula for total reward: -x^2-y^2+1')
        return - reward_direction ** 2 - reward_speed ** 2 + 1.001

        # steering
        # prev_steering_angle = self.prev_steering_angle
        # steering_angle = params['steering_angle']
        # steering_diff = abs(steering_angle - prev_steering_angle)
        # print('steering_diff in degrees: ', steering_diff)
        # reward_steering = math.exp(-0.1 * steering_diff)
        # print('reward_steering: ', reward_steering)
        # self.prev_steering_angle = steering_angle


reward_state = Reward()


def reward_function(params):
    print('params =>', params)
    all_wheels_on_track = params['all_wheels_on_track']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    reward = 1e-3
    if all_wheels_on_track and (0.5 * track_width - distance_from_center) >= DELTA_DIST:
        reward = reward_state.reward_funciton(params)
        steps = params['steps']
        progress = params['progress']
        if progress == 100:
            bonus = (progress / steps) * 100
            reward += bonus
            print(f'reward {bonus} for efficiency')
    print('reward final result: ', reward)
    return float(min(1e3, max(reward, 1e-3)))
