import math

MAX_SPEED = 4
MIN_SPEED = 1
MAX_STEERING = 30
MIN_STEERING = -30
FORCAST = 20
STEPS_PER_SECOND = 15
VEHICLE_WIDTH = 0.225


def dist(p1, p2, p3):
    return abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])) / math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


class Reward:
    def __init__(self):
        self.prev_steering_angle = None
        self.prev_heading = None

    def reward_function(self, params):
        waypoints = params['waypoints']
        closest_waypoints = params['closest_waypoints']
        track_width = params['track_width']
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
                distance_from_extreme_edge = float(max(0.0, (track_width + VEHICLE_WIDTH) / 2 - d))
                if distance_from_extreme_edge <= 0:
                    out_of_track = True
                    break
            if not out_of_track:
                potential_forcast_index = waypoints_middle[i]
                break
        next_point = waypoints[potential_forcast_index]
        print('projected waypoint:', potential_forcast_index)

        # direction
        track_direction = math.atan2(next_point[1] - car_pos[1], next_point[0] - car_pos[0])
        track_direction = math.degrees(track_direction)
        heading = params['heading'] + params['steering_angle']
        if self.prev_steering_angle is not None and self.prev_heading is not None:
            prev_heading = self.prev_heading + self.prev_steering_angle
        else:
            prev_heading = heading
        if abs(prev_heading-heading) > 20:
            return 1e-3
        direction_diff = abs(track_direction - heading)
        if direction_diff > 180:
            direction_diff = 360 - direction_diff
        print('direction_diff in degrees:', direction_diff)
        if direction_diff > 40:
            return 1e-3
        reward_direction = 40 * (1 - (direction_diff / 40))
        print('reward_direction:', reward_direction)

        # speed
        p_w = waypoints[closest_waypoints[0]]
        n_w = waypoints[closest_waypoints[1]]
        track_curve = math.atan2(n_w[1] - p_w[1], n_w[0] - p_w[0]) - math.atan2(next_point[1] - p_w[1], next_point[0] - p_w[0])
        track_curve = abs(math.degrees(track_curve))
        if track_curve > 180:
            track_curve = 360 - track_curve
        target_speed = MAX_SPEED - ((MAX_SPEED - MIN_SPEED) / 90) * track_curve
        speed = params['speed']
        speed_diff = abs(target_speed - speed)
        print('speed_diff: ', speed_diff)
        reward_speed = (MAX_SPEED - MIN_SPEED) * (1 - (speed_diff / (MAX_SPEED - MIN_SPEED)))
        print('reward_speed:', reward_speed)

        # steering
        prev_steering_angle = self.prev_steering_angle if self.prev_steering_angle is not None else 0
        steering_angle = params['steering_angle']
        steering_diff = abs(steering_angle - prev_steering_angle)
        print('steering_diff in degrees:', steering_diff)
        if steering_diff > 30:
            return 1e-3
        reward_steering = 10 * (1 - (steering_diff / 30))
        print('reward_steering:', reward_steering)
        self.prev_steering_angle = steering_angle

        return reward_direction * reward_speed + reward_steering


reward_state = Reward()


def reward_function(params):
    print('params =>', params)
    all_wheels_on_track = params['all_wheels_on_track']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    reward = 1e-3
    distance_from_extreme_edge = float(max(0.0, (track_width + VEHICLE_WIDTH) / 2 - distance_from_center))
    if all_wheels_on_track and distance_from_extreme_edge > 0:
        reward = reward_state.reward_function(params)
    is_complete_lap = params['progress'] == 100
    is_offtrack = params['is_offtrack']
    is_reversed = params['is_reversed']
    is_final_step = is_complete_lap or is_offtrack or is_reversed
    steps = params['steps']
    if is_final_step:
        if is_complete_lap:
            reward += 100 / (steps / STEPS_PER_SECOND)
        if is_offtrack or is_reversed:
            reward -= steps
    print('reward final result: ', reward)
    return float(min(1e3, max(reward, 1e-3)))
