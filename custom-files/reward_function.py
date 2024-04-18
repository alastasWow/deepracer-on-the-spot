from deep_racer_framework import Framework, get_reward


def reward_function(params):
    global framework_global
    if not framework_global:
        framework_global = Framework(params)
    framework_global.process_params(params)
    framework_global.print_debug()
    raw_reward = float(get_reward(framework_global))
    if raw_reward > 0:
        return raw_reward
    else:
        tiny_reward = 0.0001
        print("WARNING - Invalid reward " + str(raw_reward) + " replaced with " + str(tiny_reward))
        return tiny_reward


framework_global = None
