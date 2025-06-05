import math

MAX_SPEED = 4
MIN_SPEED = 0
MAX_STEERING = 25
MIN_STEERING = -25
MAX_VISION = 30
MIN_VISION = -30
FORCAST = 15
STEPS_PER_SECOND = 15
VEHICLE_WIDTH = 0.225
SWITCH = 7
REWARD_FASTEST = 20


def dist(p1, p2, p3):
    return abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])) / math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def direction_waypoint(pos, waypoint):
    x, y = pos
    waypoint_x, waypoint_y = waypoint
    waypoint_direction = math.atan2(waypoint_y - y, waypoint_x - x)
    res = math.degrees(waypoint_direction)
    return res if res >= 0 else res + 360


def forcast_v4(next_waypoint_index, waypoints, pos, heading, max_dist):
    tmp_heading = heading if heading >= 0 else heading + 360
    r_line_direction, l_line_direction = tmp_heading + MIN_VISION, tmp_heading + MAX_VISION
    start_forcast_index = (next_waypoint_index + FORCAST - 1) % len(waypoints)
    if start_forcast_index > next_waypoint_index:
        middle_waypoints = [i for i in range(start_forcast_index, next_waypoint_index - 1, -1)]
    else:
        middle_waypoints = [i for i in range(start_forcast_index, -1, -1)] + [i for i in range(len(waypoints) - 1, next_waypoint_index - 1, -1)]
    diff_index = len(middle_waypoints)
    for i in range(len(middle_waypoints)):
        # check within cone
        waypoint_direction = direction_waypoint(pos, waypoints[middle_waypoints[i]])
        if r_line_direction <= waypoint_direction <= l_line_direction:
            visible = True
            for j in range(i + 1, len(middle_waypoints)):
                d = dist(waypoints[middle_waypoints[i]], pos, waypoints[middle_waypoints[j]])
                if d >= max_dist:
                    visible = False
                    break
            if visible:
                diff_index = len(middle_waypoints) - i
                break
            else:
                diff_index -= 1
        else:
            diff_index -= 1
    return (next_waypoint_index + diff_index - 1) % len(waypoints), diff_index


class Reward:
    prev_progress = 0
    prev_steering = 0
    best_time = 10
    best_reward = REWARD_FASTEST

    def __init__(self):
        self.reset()

    def reset(self):
        self.prev_progress = 0
        self.prev_steering = 0

    def turn(self, speed, steering, progress, diff_direction):
        speed_ratio = (speed - MIN_SPEED) / (MAX_SPEED - MIN_SPEED)
        # direction_ratio = diff_direction / MAX_VISION
        # steering_ratio = abs(steering - self.prev_steering) / (2 * MAX_STEERING)
        # steering_ratio_1 = abs(steering) / MAX_STEERING
        # progress_diff = progress - self.prev_progress
        res = round(1 - speed_ratio, 3)
        # res = round((1 / (speed_ratio + 0.1)) - 0.9, 3)
        return res

    def speedup(self, speed, steering, progress, diff_direction):
        speed_ratio = (speed - MIN_SPEED) / (MAX_SPEED - MIN_SPEED)
        # direction_ratio = diff_direction / MAX_VISION
        # steering_ratio = abs(steering - self.prev_steering) / (2 * MAX_STEERING)
        # steering_ratio_1 = abs(steering) / MAX_STEERING
        # progress_diff = progress - self.prev_progress
        res = round(speed_ratio, 3)
        # res = round((1 / (1.1 - speed_ratio)) - 0.9, 3)
        return res

    def reward_function(self, params):
        reward = 1e-3
        all_wheels_on_track = params['all_wheels_on_track']
        track_width = params['track_width']
        distance_from_center = params['distance_from_center']
        progress = params['progress']
        steps = params['steps']
        speed = params['speed']
        steering = params['steering_angle']
        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        heading = params['heading']
        car_coord = (params['x'], params['y'])
        # Calculate the direction of the center line based on the closest waypoints
        heading = heading + steering
        if heading > 180:
            heading -= 360
        elif heading < -180:
            heading += 360
        next_point = waypoints[closest_waypoints[1]]
        prev_point = waypoints[closest_waypoints[0]]
        track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
        # Convert to degree
        track_direction = math.degrees(track_direction)
        # Calculate the difference between the track direction and the heading direction of the car
        direction_diff = abs(track_direction - heading)
        if direction_diff > 180:
            direction_diff = 360 - direction_diff
        max_dist = 0.5 * (track_width + VEHICLE_WIDTH)
        forcast_index, diff_index = forcast_v4(closest_waypoints[1], waypoints, car_coord, heading, max_dist)
        # print(f'forcast: {closest_waypoints}, {diff_index}, {forcast_index}')
        if distance_from_center < max_dist and direction_diff < 90:
            w1 = round(1 / (1 + math.exp(diff_index - SWITCH)), 3)
            w2 = round(1 - w1, 3)
            if diff_index > 0:
                forcast_car_coord = waypoints[forcast_index]
                forcast_direction = math.atan2(forcast_car_coord[1] - car_coord[1], forcast_car_coord[0] - car_coord[0])
                forcast_direction = math.degrees(forcast_direction)
                forcast_direction_diff = abs(forcast_direction - heading)
                if forcast_direction_diff > 180:
                    forcast_direction_diff = 360 - forcast_direction_diff
            else:
                forcast_direction_diff = MAX_VISION
            # print(f'speed_ratio: {(speed - MIN_SPEED) / (MAX_SPEED - MIN_SPEED)}, steering_ratio_1: {abs(steering) / MAX_STEERING}')
            x = self.turn(speed, steering, progress, forcast_direction_diff)
            y = self.speedup(speed, steering, progress, forcast_direction_diff)
            reward = round(w1 * x + w2 * y, 3)
            print(f'reward {reward} = {w1} * {x} + {w2} * {y}')
        self.prev_progress = progress
        self.prev_steering = steering
        is_complete_lap = int(progress) == 100
        is_offtrack = params['is_offtrack']
        is_reversed = params['is_reversed']
        is_crashed = params['is_crashed']
        is_final_step = is_complete_lap or is_offtrack or is_reversed or is_crashed
        if is_final_step:
            if is_complete_lap:
                time = steps / STEPS_PER_SECOND
                if time < self.best_time:
                    self.best_time = time
                    self.best_reward += REWARD_FASTEST
                    print(f'time {self.best_time} with best reward {self.best_reward}')
                    reward += self.best_reward
            self.reset()
        return float(min(1e3, max(reward, 1e-3)))


reward_state = Reward()


def reward_function(params):
    print('params =>', params)
    reward = reward_state.reward_function(params)
    print('reward final result: ', reward)
    return reward
