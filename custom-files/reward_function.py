import math

MAX_SPEED = 4
MIN_SPEED = 1
MAX_STEERING = 30
MIN_STEERING = -30
FORCAST = 15
STEPS_PER_SECOND = 15
VEHICLE_WIDTH = 0.225


def dist(p1, p2, p3):
    return abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])) / math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


class Reward:
    def __init__(self):
        self.score = 0
        self.prev_steering_angle = None

    def reward_function(self, params):
        reward = 1e-3
        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        track_width = params['track_width']
        potential_forcast_index = (closest_waypoints[1] + FORCAST) % len(waypoints)
        car_pos = (params['x'], params['y'])

        if potential_forcast_index > closest_waypoints[1]:
            waypoints_middle = [i for i in range(potential_forcast_index, closest_waypoints[1] - 1, -1)]
        else:
            waypoints_middle = [i for i in range(potential_forcast_index, -1, -1)] + [i for i in range(len(waypoints) - 1, closest_waypoints[1] - 1, -1)]

        for i in range(len(waypoints_middle)):
            out_of_track = False
            for j in range(i + 1, len(waypoints_middle)):
                d = dist(waypoints[waypoints_middle[i]], car_pos, waypoints[waypoints_middle[j]])
                if d >= 0.5 * (track_width + VEHICLE_WIDTH):
                    out_of_track = True
                    break
            if not out_of_track:
                potential_forcast_index = waypoints_middle[i]
                break
        n_point = waypoints[potential_forcast_index]
        print('projected waypoint:', potential_forcast_index)

        # steering
        if self.prev_steering_angle is not None:
            prev_steering_angle = self.prev_steering_angle
        else:
            prev_steering_angle = params['steering_angle']
        self.prev_steering_angle = params['steering_angle']
        diff_steering = abs(prev_steering_angle - params['steering_angle'])
        print('diff_steering in degrees:', diff_steering)
        if diff_steering > 20:
            return reward

        # direction
        track_direction = math.atan2(n_point[1] - car_pos[1], n_point[0] - car_pos[0])
        track_direction = math.degrees(track_direction)
        heading = params['heading']
        direction_diff = abs(track_direction - heading)
        if direction_diff > 180:
            direction_diff = 360 - direction_diff
        print('direction_diff normalized:', direction_diff / 180)

        # speed
        p_w = waypoints[closest_waypoints[0]]
        n_w = waypoints[closest_waypoints[1]]
        track_curve = math.atan2(n_w[1] - p_w[1], n_w[0] - p_w[0]) - math.atan2(n_point[1] - p_w[1], n_point[0] - p_w[0])
        track_curve = abs(math.degrees(track_curve))
        if track_curve > 180:
            track_curve = 360 - track_curve
        print('track_curve', track_curve)
        target_speed = MAX_SPEED * math.exp(-20 * (track_curve / 180) ** 2)
        speed = params['speed']
        speed_diff = abs(target_speed - speed)
        print('speed_diff normalized: ', speed_diff / (MAX_SPEED - MIN_SPEED))

        # steering
        # prev_steering_angle = self.prev_steering_angle if self.prev_steering_angle is not None else 0
        # steering_angle = params['steering_angle']
        # steering_diff = abs(steering_angle - prev_steering_angle)
        # print('steering_diff in degrees:', steering_diff)
        # if steering_diff > 30:
        #     return 1e-3
        # reward_steering = 10 * (1 - (steering_diff / 30))
        # print('reward_steering:', reward_steering)
        # self.prev_steering_angle = steering_angle
        reward = 5 * math.exp(-10 * (direction_diff / 180) ** 2 - 10 * speed_diff / (MAX_SPEED - MIN_SPEED) ** 2)
        self.score += reward
        return reward


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
            print('bonus')
            time = steps / STEPS_PER_SECOND
            print('time:', time)
            reward += 300 * math.exp(10 - time)
    print('reward final result: ', reward)
    return float(min(1e3, max(reward, 1e-3)))
