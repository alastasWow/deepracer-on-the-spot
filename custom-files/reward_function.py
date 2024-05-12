import math
import uuid

MAX_SPEED = 4
MIN_SPEED = 1
MAX_STEERING = 30
MIN_STEERING = -30
FORCAST = 15
STEPS_PER_SECOND = 15
VEHICLE_WIDTH = 0.225
#Should be 8.5*track_length ~= 141.08
TOP_CONST = 140
FACTOR_TOP=8.5
#Should be 67/track_length ~= 4.03
FACTOR_REWARD_TOP=67

BONUS_PROGRESSION = 5
BONUS_NOT_OUT_BUT_NO_PROGRESS = 1
PUNITION_SORTIE_FACTOR = 0
ELIGIBILITY_BONUS_END_PROGRESSION = 99
BONUS_END_PROGRESSION_FACTOR = 60


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

class RewardV3:
    def __init__(self):
        self.iteration=0
        self.reInit()

    def reInit(self):
        #Global Iteration
        self.iteration += 1
        #UUID
        self.uuid = uuid.uuid4()
        #Progress
        self.lastCurrentProgress = 0
        self.lastProgress = 0
        self.maxLastProgress = 0
        self.totalProgress = 0
        self.consumedEndProgressionBonus = 0
        #Out
        self.outCount = 0
        self.outLastTime = False
        #Reward
        self.totalReward = 0
        self.totalRewardWithoutCap = 0
        #Closest Way Point
        self.lastClosestWayPoint = 0
        #Step
        self.stepCount = 1

    def reward_function(self, params):
        if (self.startLap(params)):
            self.reInit()
        speed = params['speed']
        closest_waypoints = params['closest_waypoints']
        all_wheels_on_track = params['all_wheels_on_track']
        distance_from_center = params['distance_from_center']
        newClosestWayPoint = params['closest_waypoints'][0]
        self.lastClosestWayPoint = newClosestWayPoint
        reward = self.regularStep(params)
        #reward = self.regularStepv80(params)
        rewardCap = float(min(1e3, max(reward, 1e-3)))
        self.totalReward += rewardCap
        self.totalRewardWithoutCap +=reward
        print(f'### jerome - iteration {self.iteration}, uuid {self.uuid}, reward {reward}, rewardCap {rewardCap}, speed {speed}, all_wheels_on_track {all_wheels_on_track}, distance_from_center {distance_from_center}, stepCount {self.stepCount}, lastCurrentProgress {self.lastCurrentProgress}, lastProgress {self.lastProgress}, maxLastProgress {self.maxLastProgress}, totalProgress {self.totalProgress}, consumedEndProgressionBonus {self.consumedEndProgressionBonus}, outCount {self.outCount}, outLastTime {self.outLastTime}, totalReward {self.totalReward}, totalRewardWithoutCap {self.totalRewardWithoutCap}, lastClosestWayPoint {self.lastClosestWayPoint}, closest_waypoints {closest_waypoints}')
        if (self.endLap(params)):
            self.reInit()
        return rewardCap

    def regularStep(self,params):
        #Manage Step
        self.manageStep(params)
        #Check if out
        wasOut = self.outLastTime
        if (not self.manageOut(params)):
            #Not out
            #Check progression
            currentProgress = self.manageProgression(params,wasOut)
            self.lastCurrentProgress=currentProgress
            #Attibruate reward
            return self.manageRewardForProgression93(params,currentProgress)
        else:
            #Out
            self.lastCurrentProgress=0
            return 1e-3

    def regularStepv80(self,params):
        #Manage Step
        self.manageStep(params)
        #Check if out
        wasOut = self.outLastTime
        self.manageOut(params)
        #Don't care about out
        #Check progression
        currentProgress = self.manageProgression(params,wasOut)
        self.lastCurrentProgress=currentProgress
        #Attibruate reward
        return self.manageRewardForProgression77(params,currentProgress)

    def manageRewardForProgression61(self,params,currentProgress):
        if (currentProgress>0):
            distance_from_center = params['distance_from_center']
            if (distance_from_center>0.6):
                #100% ok 12% échec à 0.8
                return 1e-2
            if (distance_from_center<0.2807):
                #100% ok 0% échec
                #0.8 bonusCenter = 22
                #0.4 bonusCenter = 35
                bonusCenter = 33
            else:
                #Here we are between 0.2807 and 0.8
                #bonusCenter = math.exp(6*(0.8-distance_from_center))-0.99
                #from 34.84 to 0.1
                #bonusCenter = math.exp(30*(0.4-distance_from_center))-0.9
                #from 34.84 to 0.1
                bonusCenter = math.exp(11*(0.6-distance_from_center))-0.9
            top = self.stepCount + (PUNITION_SORTIE_FACTOR * 45 * self.outCount)
            if top < TOP_CONST:
                return self.bonusEndProgression(params,top)+((bonusCenter + BONUS_PROGRESSION + (100 - (top/2))) * currentProgress)
                #return bonusCenter + BONUS_PROGRESSION + ((100 - (top / 2)) * currentProgress)
            else:
                return (bonusCenter + BONUS_NOT_OUT_BUT_NO_PROGRESS) * currentProgress
                #return bonusCenter + BONUS_NOT_OUT_BUT_NO_PROGRESS + currentProgress
        else:
            #No progress
            return 1e-3

    def manageRewardForProgression64(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            distance_from_center = params['distance_from_center']
            if (distance_from_center<0.3):
                #We are close to center
                #Calculate bonusCenter from 1 to 31
                bonusCenter = max(1,((0.3-distance_from_center)*100)+1)
                #Calculate top with punition for out
                top = self.stepCount + (PUNITION_SORTIE_FACTOR * 45 * self.outCount)
                if (top<TOP_CONST):
                    #We did less than TOP_CONST from to 1 to 561
                    bonusTop=1+((TOP_CONST-top)*4)
                    #Normal track from 2 to 592
                    return (bonusCenter+bonusTop)*currentProgress
                else:
                    #Too many top from 2 to 32
                    return (bonusCenter+1)*currentProgress
            else :
                #Too far from center
                return 1e-2
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression65(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            distance_from_center = params['distance_from_center']
            if (distance_from_center<0.3):
                #We are close to center
                #Calculate bonusCenter from 1 to 91
                bonusCenter = max(1,((0.3-distance_from_center)*300)+1)
                #Calculate top with punition for out
                top = self.stepCount + (PUNITION_SORTIE_FACTOR * 45 * self.outCount)
                if (top<TOP_CONST):
                    #We did less than TOP_CONST from to 1 to 57
                    bonusTop=1+((TOP_CONST-top)*0.4)
                    #Normal track from 2 to 592
                    return (bonusCenter+bonusTop)*currentProgress
                else:
                    #Too many top from 2 to 32
                    return (bonusCenter+1)*currentProgress
            else :
                #Too far from center
                return 1e-2
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression66(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            distance_from_center = params['distance_from_center']
            if (distance_from_center<0.3):
                #We are close to center
                #Calculate bonusCenter from 1 to 31
                bonusCenter = max(1,((0.3-distance_from_center)*100)+1)
                #Calculate top with punition for out
                top = self.stepCount + (PUNITION_SORTIE_FACTOR * 45 * self.outCount)
                if (top<TOP_CONST):
                    #We did less than TOP_CONST from to 1 to 561
                    bonusTop=1+((TOP_CONST-top)*4)
                    #Normal track from 2 to 592
                    return (bonusCenter+bonusTop)*currentProgress
                else:
                    #Too many top from 2 to 32
                    return (bonusCenter+1)*currentProgress
            else :
                #Too far from center
                return 1*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression67(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            topMax = track_length*FACTOR_TOP
            factorRewardTop = FACTOR_REWARD_TOP/track_length
            if (distance_from_center<0.3):
                #We are close to center
                #Calculate bonusCenter from 1 to 31
                bonusCenter = max(1,((0.3-distance_from_center)*100)+1)
                #Calculate top with punition for out
                top = self.stepCount + (PUNITION_SORTIE_FACTOR * 45 * self.outCount)
                if (top<topMax):
                    #We did less than TOP_CONST from to 1 to 561
                    bonusTop=1+((topMax-top)*factorRewardTop)
                    #Normal track from 2 to 592
                    return (bonusCenter+bonusTop)*currentProgress
                else:
                    #Too many top from 2 to 32
                    return (bonusCenter+1)*currentProgress
            else :
                #Too far from center
                return 1*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression69(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 1 to 193
            bonusProgress=math.exp(progress/19)
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            topMax = track_length*FACTOR_TOP
            factorRewardTop = FACTOR_REWARD_TOP/track_length
            if (distance_from_center<0.3):
                #We are close to center
                #Calculate bonusCenter from 1 to 31
                bonusCenter = max(1,((0.3-distance_from_center)*100)+1)
                #Calculate top with punition for out
                top = self.stepCount + (PUNITION_SORTIE_FACTOR * 45 * self.outCount)
                if (top<topMax):
                    #We did less than TOP_CONST from to 1 to 561
                    bonusTop=1+((topMax-top)*factorRewardTop)
                    #Normal track from 3 to 785
                    return (bonusProgress+bonusCenter+bonusTop)*currentProgress
                else:
                    #Too many top from 3 to 225
                    return (bonusProgress+bonusCenter+1)*currentProgress
            else :
                #Too far from center
                return 1*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression70(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 1 to 193
            bonusProgress=math.exp(progress/19)
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            topMax = track_length*FACTOR_TOP
            factorRewardTop = FACTOR_REWARD_TOP/track_length
            if (distance_from_center<0.3):
                #We are close to center
                #Calculate bonusCenter from 1 to 31
                bonusCenter = max(1,((0.3-distance_from_center)*100)+1)
                #Calculate top with punition for out
                top = self.stepCount + (PUNITION_SORTIE_FACTOR * 45 * self.outCount)
                if (top<topMax):
                    #We did less than TOP_CONST from to 1 to 561
                    bonusTop=1+((topMax-top)*factorRewardTop)
                    #Normal track from 3 to 785
                    return (bonusProgress+bonusCenter+bonusTop)*currentProgress
                else:
                    #Too many top from 3 to 225
                    return (bonusProgress+bonusCenter+1)*currentProgress
            else :
                #Too far from center from 2 to 194
                return (1+bonusProgress)*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression71(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 1 to 193
            bonusProgress=math.exp(progress/19)
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            topMax = track_length*FACTOR_TOP
            factorRewardTop = FACTOR_REWARD_TOP/track_length
            if (distance_from_center<0.3):
                #We are close to center
                #Calculate bonusCenter from 1 to 31
                bonusCenter = max(1,((0.3-distance_from_center)*100)+1)
                #Calculate top with punition for out
                top = self.stepCount + (PUNITION_SORTIE_FACTOR * 45 * self.outCount)
                if (top<topMax):
                    #We did less than TOP_CONST from to 1 to 561
                    bonusTop=1+((topMax-top)*factorRewardTop)
                    #Normal track from 3 to 785
                    return (bonusProgress+bonusCenter+bonusTop)*currentProgress
                else:
                    #Too many top from 3 to 225
                    return (bonusProgress+bonusCenter+1)*currentProgress
            else :
                #Too far from center from 1.1 to 20.3
                return (1+(bonusProgress/10))*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression72b(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 1 to 193
            bonusProgress=math.exp(progress/19)
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            topMax = track_length*FACTOR_TOP
            factorRewardTop = FACTOR_REWARD_TOP/track_length
            #Calculate top without punition
            top = self.stepCount
            if (top<topMax):
                #We did less than TOP_CONST from to 1 to 561
                bonusTop=1+((topMax-top)*factorRewardTop)
                #Normal track from 2 to 754
                return (bonusProgress+bonusTop)*currentProgress
            else:
                #Too many top from 2 to 194
                return (bonusProgress+1)*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression72(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 1 to 193
            bonusProgress=math.exp(progress/19)
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            topMax = track_length*FACTOR_TOP
            factorRewardTop = FACTOR_REWARD_TOP/track_length
            #Calculate top without punition
            top = self.stepCount
            if (top<topMax):
                #We did less than TOP_CONST from to 1 to 561
                bonusTop=1+((topMax-top)*factorRewardTop)
                #Normal track from 2 to 754
                return (bonusProgress+bonusTop)*currentProgress
            else:
                #Too many top from 2 to 194
                return (bonusProgress+1)*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression73(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 1 to 518
            bonusProgress=math.exp(progress/16)
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            topMax = track_length*FACTOR_TOP
            factorRewardTop = FACTOR_REWARD_TOP/track_length
            #Calculate top without punition
            top = self.stepCount
            if (top<topMax):
                #We did less than TOP_CONST from to 1 to 561
                bonusTop=1+((topMax-top)*factorRewardTop)
                #Normal track from 2 to 1079
                return (bonusProgress+bonusTop)*currentProgress
            else:
                #Too many top from 2 to 519
                return (bonusProgress+1)*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression74(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 1 to 785
            bonusProgress=math.exp(progress/15)
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            topMax = track_length*FACTOR_TOP
            factorRewardTop = FACTOR_REWARD_TOP/track_length
            #Calculate top without punition
            top = self.stepCount
            if (top<topMax):
                #We did less than TOP_CONST from to 1 to 561
                bonusTop=1+((topMax-top)*factorRewardTop)
                #Normal track from 2 to 1346
                return (bonusProgress+bonusTop)*currentProgress
            else:
                #Too many top from 2 to 786
                return (bonusProgress+1)*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression76(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 4 to 488
            bonusProgress=math.exp((progress+30)/21)
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            #topMax = track_length*FACTOR_TOP
            topMax=139
            #factorRewardTop = FACTOR_REWARD_TOP/track_length
            #Calculate top without punition
            top = self.stepCount
            if (top<topMax):
                #We did less than TOP_CONST from to 1 to 561
                bonusTop=562-math.exp(top/22)
                #Normal track from 2 to 1079
                return (bonusProgress+bonusTop)*currentProgress
            else:
                #Too many top from 2 to 489
                return (bonusProgress+1)*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression77(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 4 to 488
            bonusProgress=math.exp((progress+30)/21)
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            #topMax = track_length*FACTOR_TOP
            topMax=139
            #factorRewardTop = FACTOR_REWARD_TOP/track_length
            #Calculate top without punition
            top = self.stepCount
            if (top<topMax):
                #We did less than TOP_CONST from to 1 to 281
                bonusTop=1+((561-math.exp(top/22))/2)
                #Normal track from 2 to 769
                return (bonusProgress+bonusTop)*currentProgress
            else:
                #Too many top from 2 to 489
                return (bonusProgress+1)*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression78(self,params,currentProgress):
        #distance_from_center = params['distance_from_center']
        #track_length = params['track_length']
        if (currentProgress>0):
            #We made currentProgress
            progress = params['progress']
            #Calculate bonus progression from 4 to 488
            bonusProgress=math.exp((progress+30)/21)
            #topMax = track_length*FACTOR_TOP
            topMax=139
            top = self.stepCount
            if (top<topMax):
                factorTop=1-(math.exp(top/30.2)/100)
                #From 0.011 to 483
                return bonusProgress*factorTop*currentProgress
            else:
                #We give current progress point
                return currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression79(self,params,currentProgress):
        #distance_from_center = params['distance_from_center']
        #track_length = params['track_length']
        if (currentProgress>0):
            #We made currentProgress
            progress = params['progress']
            #Calculate bonus progression from 4 to 488
            bonusProgress=math.exp((progress+30)/21)
            #topMax = track_length*FACTOR_TOP
            topMax=151
            top = self.stepCount
            if (top<topMax):
                factorTop=1-(math.exp(top/33)/100)
                #From 0.011 to 483
                return bonusProgress*factorTop*currentProgress
            else:
                #We give current progress point
                return currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression90(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 298 to 600
            bonusProgress=math.exp(5.7+(progress*0.007))
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            #topMax = track_length*FACTOR_TOP
            topMax=150
            #factorRewardTop = FACTOR_REWARD_TOP/track_length
            #Calculate top without punition
            top = self.stepCount
            if (top<topMax):
                #FactorTop from 100% to 43%
                factorTop=math.log(2.52-(top*top*top/1805000),10)+0.6
                #Normal track from 2 to 769
                return bonusProgress*factorTop*currentProgress
            else:
                #We give only 30% of bonus Progress
                return bonusProgress*0.3*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression91(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 301 to 602
            bonusProgress=math.exp(5.7+(progress*0.007))
            distance_from_center = params['distance_from_center']
            track_length = params['track_length']
            #topMax = track_length*FACTOR_TOP
            topMax=140
            #factorRewardTop = FACTOR_REWARD_TOP/track_length
            #Calculate top without punition
            top = self.stepCount
            if (top<topMax):
                #FactorTop from 100% to 61%
                factorTop=math.log(2.52-(top*top*top/1805000),10)+0.6
                #Normal track from 180 to 602
                return bonusProgress*factorTop*currentProgress
            else:
                #We give only 30% of bonus Progress
                return bonusProgress*0.3*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression92(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 301 to 602
            bonusProgress=math.exp(5.7+(progress*0.007))
            distance_from_center = params['distance_from_center']
            #From 1 to 257
            bonusCenter=math.exp(1/(distance_from_center+0.18))-1
            track_length = params['track_length']
            #topMax = track_length*FACTOR_TOP
            topMax=140
            #factorRewardTop = FACTOR_REWARD_TOP/track_length
            #Calculate top without punition
            top = self.stepCount
            if (top<topMax):
                #FactorTop from 100% to 61%
                factorTop=math.log(2.52-(top*top*top/1805000),10)+0.6
                #Normal track from 181 to 859
                return ((bonusProgress*factorTop)+bonusCenter)*currentProgress
            else:
                #We give only 30% of bonus Progress
                return ((bonusProgress*0.3)+bonusCenter)*currentProgress
        else :
            #No progress
            return 1e-3

    def manageRewardForProgression93(self,params,currentProgress):
        if (currentProgress>0):
            #We made progress
            progress = params['progress']
            #Calculate bonus progression from 301 to 602
            bonusProgress=math.exp(5.7+(progress*0.007))
            distance_from_center = params['distance_from_center']
            #From 1 to 26
            bonusCenter=(math.exp(1/(distance_from_center+0.18))-1)/10
            track_length = params['track_length']
            #topMax = track_length*FACTOR_TOP
            topMax=140
            #factorRewardTop = FACTOR_REWARD_TOP/track_length
            #Calculate top without punition
            top = self.stepCount
            if (top<topMax):
                #FactorTop from 100% to 61%
                factorTop=math.log(2.52-(top*top*top/1805000),10)+0.6
                #Normal track from 180 to 628
                return ((bonusProgress*factorTop)+bonusCenter)*currentProgress
            else:
                #We give only 30% of bonus Progress
                return ((bonusProgress*0.3)+bonusCenter)*currentProgress
        else :
            #No progress
            return 1e-3

    def bonusEndProgression(self,params,top):
        progress = params['progress']
        if (progress>ELIGIBILITY_BONUS_END_PROGRESSION):
            bonusFactor = (progress-ELIGIBILITY_BONUS_END_PROGRESSION)*BONUS_END_PROGRESSION_FACTOR
            basedBonusEndProgression = ((bonusFactor*bonusFactor/2)-self.consumedEndProgressionBonus)
            self.consumedEndProgressionBonus+=basedBonusEndProgression
            bonusEndProgression = (basedBonusEndProgression*TOP_CONST/top)
            print(f'### marcelBonusEndProgression - iteration {self.iteration}, uuid {self.uuid}, progress {progress}, bonusEndProgression {bonusEndProgression}, top {top} => consumedEndProgressionBonus {self.consumedEndProgressionBonus}')
        else:
            #No Bonus for end of progression
            return 0

    def manageProgression(self,params,wasOut):
        progress = params['progress']
        currentProgress = progress - self.maxLastProgress
        self.totalProgress = progress
        self.lastProgress = progress
        if (currentProgress>0):
            #We made a progress
            self.maxLastProgress = progress
            return currentProgress
        else:
            #No progress do not change maxLastProgress
            if (not wasOut):
                #No progress strange : we keep previous totalProgress and lastProgress
                print(f'### marcelWasOut - iteration {self.iteration}, uuid {self.uuid}, progress {progress}, stepCount {self.stepCount}, lastCurrentProgress {self.lastCurrentProgress}, lastProgress {self.lastProgress}, maxLastProgress {self.maxLastProgress}, totalProgress {self.totalProgress}, consumedEndProgressionBonus {self.consumedEndProgressionBonus}, outCount {self.outCount}, outLastTime {self.outLastTime}, totalReward {self.totalReward}, totalRewardWithoutCap {self.totalRewardWithoutCap}, lastClosestWayPoint {self.lastClosestWayPoint}')
                return 0
            else:
                #No progress due to out
                return 0

    def manageProgressionOld(self,params,wasOut):
        progress = params['progress']
        if (progress>self.lastProgress):
            #We made a progress
            currentProgress = progress - self.lastProgress
            self.totalProgress += currentProgress
            self.lastProgress = progress
            return currentProgress
        else:
            #No progress
            if (not wasOut):
                #No progress strange : we keep previous totalProgress and lastProgress
                print(f'### marcelWasOut - iteration {self.iteration}, uuid {self.uuid}, progress {progress}, stepCount {self.stepCount}, lastCurrentProgress {self.lastCurrentProgress}, lastProgress {self.lastProgress}, maxLastProgress {self.maxLastProgress}, totalProgress {self.totalProgress}, consumedEndProgressionBonus {self.consumedEndProgressionBonus}, outCount {self.outCount}, outLastTime {self.outLastTime}, totalReward {self.totalReward}, totalRewardWithoutCap {self.totalRewardWithoutCap}, lastClosestWayPoint {self.lastClosestWayPoint}')
                return 0
            else:
                #No progress due to out
                currentProgress = progress
                self.totalProgress += currentProgress
                self.lastProgress = progress
                return currentProgress

    def manageStep(self,params):
        self.stepCount += 1

    def manageOut(self,params):
        all_wheels_on_track = params['all_wheels_on_track']
        if not all_wheels_on_track:
            #Vehicule out
            if (self.outLastTime):
                #We were already out
                return True
            else:
                self.outLastTime = True
                self.outCount += 1
                return True
        else:
            self.outLastTime = False
            return False

    def startLap(self,params):
        currentStep = params['steps']
        progress = params['progress']
        if (currentStep==2):
            print(f'### marcelWillInit - iteration {self.iteration}, uuid {self.uuid}, progress {progress}, stepCount {self.stepCount}, lastCurrentProgress {self.lastCurrentProgress}, lastProgress {self.lastProgress}, maxLastProgress {self.maxLastProgress}, totalProgress {self.totalProgress}, consumedEndProgressionBonus {self.consumedEndProgressionBonus}, outCount {self.outCount}, outLastTime {self.outLastTime}, totalReward {self.totalReward}, totalRewardWithoutCap {self.totalRewardWithoutCap}, lastClosestWayPoint {self.lastClosestWayPoint}')
            return True
        else:
            return False

    def endLap(self,params):
        progress = params['progress']
        is_offtrack = params['is_offtrack']
        is_reversed = params['is_reversed']
        if (is_offtrack):
            print(f'### marcelOffTrack - iteration {self.iteration}, uuid {self.uuid}, progress {progress}, is_offtrack {is_offtrack}, stepCount {self.stepCount}, lastCurrentProgress {self.lastCurrentProgress}, lastProgress {self.lastProgress}, maxLastProgress {self.maxLastProgress}, totalProgress {self.totalProgress}, consumedEndProgressionBonus {self.consumedEndProgressionBonus}, outCount {self.outCount}, outLastTime {self.outLastTime}, totalReward {self.totalReward}, totalRewardWithoutCap {self.totalRewardWithoutCap}, lastClosestWayPoint {self.lastClosestWayPoint}')
            return True
        if (progress==100):
            print(f'### marcel100Progression - iteration {self.iteration}, uuid {self.uuid}, progress {progress}, is_offtrack {is_offtrack}, stepCount {self.stepCount}, lastCurrentProgress {self.lastCurrentProgress}, lastProgress {self.lastProgress}, maxLastProgress {self.maxLastProgress}, totalProgress {self.totalProgress}, consumedEndProgressionBonus {self.consumedEndProgressionBonus}, outCount {self.outCount}, outLastTime {self.outLastTime}, totalReward {self.totalReward}, totalRewardWithoutCap {self.totalRewardWithoutCap}, lastClosestWayPoint {self.lastClosestWayPoint}')
            return True
        if (is_reversed):
            print(f'### marcelReversed - iteration {self.iteration}, uuid {self.uuid}, progress {progress}, is_offtrack {is_offtrack}, stepCount {self.stepCount}, lastCurrentProgress {self.lastCurrentProgress}, lastProgress {self.lastProgress}, maxLastProgress {self.maxLastProgress}, totalProgress {self.totalProgress}, consumedEndProgressionBonus {self.consumedEndProgressionBonus}, outCount {self.outCount}, outLastTime {self.outLastTime}, totalReward {self.totalReward}, totalRewardWithoutCap {self.totalRewardWithoutCap}, lastClosestWayPoint {self.lastClosestWayPoint}')
            return True
        if (progress>99.5):
            print(f'### marcel99Progression - iteration {self.iteration}, uuid {self.uuid}, progress {progress}, is_offtrack {is_offtrack}, stepCount {self.stepCount}, lastCurrentProgress {self.lastCurrentProgress}, lastProgress {self.lastProgress}, maxLastProgress {self.maxLastProgress}, totalProgress {self.totalProgress}, consumedEndProgressionBonus {self.consumedEndProgressionBonus}, outCount {self.outCount}, outLastTime {self.outLastTime}, totalReward {self.totalReward}, totalRewardWithoutCap {self.totalRewardWithoutCap}, lastClosestWayPoint {self.lastClosestWayPoint}')
        return False

    def endLapV4(self,params):
        newClosestWayPoint = params['closest_waypoints'][0]
        if ((newClosestWayPoint+30)<self.lastClosestWayPoint):
            self.lastClosestWayPoint=newClosestWayPoint
            return True
        else:
            self.lastClosestWayPoint=newClosestWayPoint
            return False

class Reward:
    def __init__(self):
        self.last_progress = 0
        self.nb_sortie = 0
        self.uuid = uuid.uuid4()
        self.totalProgress = 0
        self.totalReward = 0
        self.jeromeStep = 0
        self.lastClosest = 0

    def reward_function(self, params):
        self.jeromeStep += 1
        all_wheels_on_track = params['all_wheels_on_track']
        if not all_wheels_on_track:
            self.nb_sortie += 1
        #COucou
        newLastClosest = params['closest_waypoints'][1]
        speed = params['speed']
        closest_waypoints = params['closest_waypoints']
        nb_progress = params['progress'] - self.last_progress
        if (nb_progress>0):
            self.totalProgress += nb_progress
        self.last_progress = params['progress']
        currentStep = params['steps']
        top = self.jeromeStep + (PUNITION_SORTIE_FACTOR * 45 * self.nb_sortie)
        if top < TOP_CONST:
            if not all_wheels_on_track:
                reward = (100 - (top / 2)) * nb_progress
            else :
                reward = 1e-3
        else:
            reward = 1e-3
        self.totalReward += reward
        print(f'### jerome - uuid {self.uuid}, jeromeStep {self.jeromeStep}, currentStep {currentStep}, top {top}, closest_waypoints {closest_waypoints}, speed {speed}, nb_progress {nb_progress}, lastProgress {self.last_progress}, totalProgress {self.totalProgress}, nbSortie {self.nb_sortie}, all_wheels_on_track {all_wheels_on_track}, reward {reward} and totalReward {self.totalReward}')
        return reward

reward_state = RewardV3()


def reward_function(params):
    print('params =>', params)
    reward = reward_state.reward_function(params)
    print('reward final result: ', reward)
    return float(min(1e3, max(reward, 1e-3)))
