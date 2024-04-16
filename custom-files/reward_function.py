import math

MAX_ANGLE = 90
TOTAL_NUM_STEPS = 100
MAX_SPEED = 4
MIN_SPEED = 1
FORCAST = 6


class Reward:
    def __init__(self):
        self.prev_steering_angle = 0
        self.prev_speed = 0

    def reward_funciton(self, params):
        # distance
        # distance_from_center = params['distance_from_center']
        # track_width = params['track_width']
        # reward_distance = 1 - (distance_from_center / (0.5 * track_width))
        # print('reward_distance: ', reward_distance)

        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        next_point = waypoints[(closest_waypoints[1] + FORCAST) % len(waypoints)]

        # direction
        track_direction = math.atan2(next_point[1] - params['y'], next_point[0] - params['x'])
        track_direction = math.degrees(track_direction)
        heading = params['heading']
        direction_diff = abs(track_direction - heading) % MAX_ANGLE
        print('direction_diff in degrees: ', direction_diff)
        # reward_direction = math.exp(-15 * direction_diff / MAX_ANGLE)
        reward_direction = direction_diff / MAX_ANGLE
        print('reward_direction formula: direction_diff / MAX_ANGLE: ', reward_direction)

        # orientation
        p_w = waypoints[closest_waypoints[0]]
        n_w = waypoints[closest_waypoints[1]]
        track_curve = math.atan2(n_w[1] - p_w[1], n_w[0] - p_w[0]) - math.atan2(next_point[1] - p_w[1], next_point[0] - p_w[0])
        track_curve = abs(math.degrees(track_curve))
        target_speed = MAX_SPEED - ((MAX_SPEED - MIN_SPEED) / MAX_ANGLE) * track_curve
        speed = params['speed']
        speed_diff = abs(target_speed - speed)
        print('speed_diff: ', speed_diff)
        reward_speed = speed_diff / (MAX_SPEED - MIN_SPEED)
        print('reward_speed formula: speed_diff / (MAX_SPEED - MIN_SPEED): ', reward_speed)
        c = 1
        print(f'formula for total reward: -{c}x2-{c}y2+{c}')
        return -c * reward_direction ** 2 - c * reward_speed ** 2 + c

        # steering
        # prev_steering_angle = self.prev_steering_angle
        # steering_angle = params['steering_angle']
        # steering_diff = abs(steering_angle - prev_steering_angle)
        # print('steering_diff in degrees: ', steering_diff)
        # reward_steering = math.exp(-0.1 * steering_diff)
        # print('reward_steering: ', reward_steering)
        # self.prev_steering_angle = steering_angle

        # w1, w2, w3 = 1, 4, 0
        # prev_speed_diff = abs(target_speed - self.prev_speed)
        # print('prev_speed_diff: ', prev_speed_diff)
        # if prev_speed_diff > speed_diff:
        #     w2 += 1
        # else:
        #     w1 = 0.3
        # self.prev_speed = speed
        # c = -(w1 + w2)
        # print('weights: (w1, w2, w3, c) = ', w1, w2, w3, c)
        # reward_direction, reward_speed, reward_steering = reward_direction, reward_speed, reward_steering
        # print(w1 * (reward_direction - 1) ** 2)
        # print(w2 * (reward_speed - 1) ** 2)
        # print(w3 * (reward_steering - 1) ** 2)
        # print(c)

        # return w1 * (reward_direction - 1) ** 2 + w2 * (reward_speed - 1) ** 2 + w3 * reward_steering + c


reward_state = Reward()


def reward_function(params):
    print('params =>', params)

    all_wheels_on_track = params['all_wheels_on_track']
    is_offtrack = params['is_offtrack']

    if is_offtrack or not all_wheels_on_track:
        return 1e-3

    reward = reward_state.reward_funciton(params)

    steps = params['steps']
    progress = params['progress']
    if (steps % (TOTAL_NUM_STEPS // 4)) == 0 and progress > (steps / TOTAL_NUM_STEPS) * 100:
        bonus = (steps / TOTAL_NUM_STEPS) * (TOTAL_NUM_STEPS / 10)
        reward += bonus
        print(f'reward {bonus} for efficiency')

    print('reward final result: ', reward)
    return float(min(1e3, max(reward, 1e-3)))
