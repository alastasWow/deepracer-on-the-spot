import math

MAX_SPEED = 4
MIN_SPEED = 1
MAX_STEERING = 30
MIN_STEERING = -30
FORCAST = 15
STEPS_PER_SECOND = 15
VEHICLE_WIDTH = 0.225


def forcast(start_forcast_index, next_waypoint, waypoints, track_width, pos):
    forcast_index = next_waypoint
    if start_forcast_index > next_waypoint:
        waypoints_middle = [i for i in range(start_forcast_index, next_waypoint - 1, -1)]
    else:
        waypoints_middle = [i for i in range(start_forcast_index, -1, -1)] + [i for i in range(len(waypoints) - 1, next_waypoint - 1, -1)]
    for i in range(len(waypoints_middle)):
        out_of_track = False
        for j in range(i + 1, len(waypoints_middle)):
            d = dist(waypoints[waypoints_middle[i]], pos, waypoints[waypoints_middle[j]])
            if d >= 0.5 * (track_width + VEHICLE_WIDTH):
                out_of_track = True
                break
        if not out_of_track:
            forcast_index = waypoints_middle[i]
            break
    print('projected waypoint:', forcast_index)
    diff_index = forcast_index - next_waypoint if forcast_index > next_waypoint else forcast_index + len(waypoints) - 1 - next_waypoint
    print('diff_index:', diff_index)
    return forcast_index, diff_index


def dist(p1, p2, p3):
    return abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])) / math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


class Reward:
    def __init__(self):
        self.prev_steering_angle = None

    def reward_function(self, params):
        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        # track_width = params['track_width']
        # potential_forcast_index = (closest_waypoints[1] + FORCAST) % len(waypoints)
        # car_pos = (params['x'], params['y'])
        # print('============')
        # print('car forcast')
        # forcast_car_index, diff_index = forcast(potential_forcast_index, closest_waypoints[1], waypoints, track_width, car_pos)
        # forcast_car = waypoints[forcast_car_index]
        # print('============')

        # print('track forcast')
        # forcast_track_index = forcast(potential_forcast_index, closest_waypoints[1], waypoints, track_width, waypoints[closest_waypoints[0]])
        # forcast_track = waypoints[forcast_track_index]

        # steering
        # if self.prev_steering_angle is not None:
        #     prev_steering_angle = self.prev_steering_angle
        # else:
        #     prev_steering_angle = params['steering_angle']
        # self.prev_steering_angle = params['steering_angle']
        # diff_steering = abs(prev_steering_angle - params['steering_angle'])
        # print('diff_steering in degrees:', diff_steering)
        # prev_steering_angle = self.prev_steering_angle if self.prev_steering_angle is not None else 0
        # steering_angle = params['steering_angle']
        # steering_diff = abs(steering_angle - prev_steering_angle)
        # print('steering_diff in degrees:', steering_diff)
        # if steering_diff > 30:
        #     return 1e-3
        # reward_steering = 10 * (1 - (steering_diff / 30))
        # print('reward_steering:', reward_steering)
        # self.prev_steering_angle = steering_angle

        # direction
        # car_direction = math.atan2(forcast_car[1] - car_pos[1], forcast_car[0] - car_pos[0])
        # car_direction = math.degrees(car_direction)
        # heading = params['heading']
        # direction_diff = abs(car_direction - heading)
        # if direction_diff > 180:
        #     direction_diff = 360 - direction_diff
        # print('direction_diff:', direction_diff)
        # print('============')

        # speed
        p_w = waypoints[closest_waypoints[0]]
        n_w = waypoints[closest_waypoints[1]]
        curve_forcast = waypoints[(closest_waypoints[1] + 6) % len(waypoints)]
        track_curve = math.atan2(n_w[1] - p_w[1], n_w[0] - p_w[0]) - math.atan2(curve_forcast[1] - p_w[1], curve_forcast[0] - p_w[0])
        track_curve = abs(math.degrees(track_curve))
        if track_curve > 180:
            track_curve = 360 - track_curve
        print('track_curve:', track_curve)
        if track_curve < 45:
            return params['speed']
        elif 45 <= track_curve < 60:
            return params['speed'] * 0.5
        else:
            return 1e-3
        # if direction_diff <= 90:
        # else:
        #     target_speed = -4
        # target_speed = (MAX_SPEED - MIN_SPEED) * math.exp(-5 * (track_curve / 90) ** 2) + MIN_SPEED
        # target_speed = MAX_SPEED - ((MAX_SPEED - MIN_SPEED) / 90) * track_curve
        # print('target_speed:', target_speed)
        # speed_diff = abs(target_speed - params['speed'])
        # print('speed_diff:', speed_diff)
        # print('============')

        # x, y = (direction_diff / 180), speed_diff / (MAX_SPEED - MIN_SPEED)
        # reward = -(2 * x) - (2 * y) + 1
        # reward = - 5 * x ** 2 - 5 * y ** 2 + 1.001
        # reward = (MAX_SPEED - MIN_SPEED) - ((MAX_SPEED - MIN_SPEED) / 90) * track_curve
        # return reward


reward_state = Reward()


def reward_function(params):
    print('params =>', params)
    all_wheels_on_track = params['all_wheels_on_track']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    reward = 1e-3
    if all_wheels_on_track and distance_from_center < 0.5 * (track_width + VEHICLE_WIDTH):
        reward = reward_state.reward_function(params)
    is_complete_lap = int(params['progress']) == 100
    is_offtrack = params['is_offtrack']
    is_reversed = params['is_reversed']
    is_crashed = params['is_crashed']
    is_final_step = is_complete_lap or is_offtrack or is_reversed or is_crashed
    steps = params['steps']
    if is_final_step:
        print('final step')
        if is_complete_lap:
            time = steps / STEPS_PER_SECOND
            print('time:', time)
            bonus = 10 * math.exp(7 - time)
            # bonus = 50 / (time - 6)
            print('bonus:', bonus)
            reward += bonus
    print('reward final result: ', reward)
    return float(min(1e3, max(reward, 1e-3)))
