import math

MAX_SPEED = 4
MIN_SPEED = 1
MAX_STEERING = 30
MIN_STEERING = -30
FORCAST = 15
STEPS_PER_SECOND = 15
VEHICLE_WIDTH = 0.225
TOP_CONST = 200


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
        self.last_progress = 0
        self.nb_sortie = 0

    def reward_function(self, params):

        all_wheels_on_track = params['all_wheels_on_track']
        if not all_wheels_on_track:
            self.nb_sortie += 1
        #COucou
        nb_progress = params['progress'] - self.last_progress
        self.last_progress = params['progress']
        top = params['steps'] + 45 * self.nb_sortie
        if top < TOP_CONST:
            return (100 - (top / 2)) * nb_progress
        else:
            return 1e-3


reward_state = Reward()


def reward_function(params):
    print('params =>', params)

    reward = reward_state.reward_function(params)
    print('reward final result: ', reward)
    return float(min(1e3, max(reward, 1e-3)))
