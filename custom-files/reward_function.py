import math

MAX_ANGLE = 180
MAX_SPEED = 3.5
MIN_SPEED = 1
FORCAST = 9


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
        prev_point = (params['x'], params['y'])
        track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        track_direction = math.degrees(track_direction)
        heading = params['heading']
        direction_diff = abs(track_direction - heading)
        if direction_diff > MAX_ANGLE:
            direction_diff = 360 - direction_diff
        reward_direction = math.exp(-15 * direction_diff / MAX_ANGLE)
        print('direction_diff in degrees: ', direction_diff)
        print('reward_direction: ', reward_direction)

        # steering
        prev_steering_angle = self.prev_steering_angle
        steering_angle = params['steering_angle']
        steering_diff = abs(steering_angle - prev_steering_angle)
        reward_steering = math.exp(-0.1 * steering_diff)
        print('steering_diff in degrees: ', steering_diff)
        print('reward_steering: ', reward_steering)
        self.prev_steering_angle = steering_angle

        # orientation
        prev_point = waypoints[closest_waypoints[1]]
        track_curve = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        track_curve = abs(math.degrees(track_curve))
        target_speed = MAX_SPEED - ((MAX_SPEED - MIN_SPEED) / MAX_ANGLE) * track_curve
        speed = params['speed']
        speed_diff = abs(target_speed - speed)
        reward_speed = math.exp(-1.5 * speed_diff)
        # prev_speed_diff = abs(target_speed - self.prev_speed)
        # if prev_speed_diff > speed_diff and self.prev_speed > 0:
        #     reward_speed = 1
        print('speed_diff: ', speed_diff)
        print('reward_speed: ', reward_speed)
        self.prev_speed = speed
        w1, w2, w3 = -1, -2, -0.5
        c = -(w1 + w2 + w3)
        # reward_direction, reward_speed, reward_steering = reward_direction, reward_speed, reward_steering
        # print(w1 * (reward_direction - 1) ** 2)
        # print(w2 * (reward_speed - 1) ** 2)
        # print(w3 * (reward_steering - 1) ** 2)
        # print(c)

        return w1 * (reward_direction - 1) ** 2 + w2 * (reward_speed - 1) ** 2 + w3 * (reward_steering - 1) ** 2 + c


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
    TOTAL_NUM_STEPS = 160
    if (steps % 40) == 0 and progress > (steps / TOTAL_NUM_STEPS) * 100:
        reward += 20
        print('reward +10 for efficiency')

    print('reward final result: ', reward)
    return float(min(1e3, max(reward, 1e-3)))
