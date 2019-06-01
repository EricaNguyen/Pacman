import random
import time

import captureAgents
import capture
import game
import util

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
        first = 'NomNomAgent', second = 'OffensiveReflexAgent'):
    """
    This function should return a list of two agents that will form the
    team, initialized using firstIndex and secondIndex as their agent
    index numbers. isRed is True if the red team is being created, and
    will be False if the blue team is being created.
    As a potentially helpful development aid, this function can take
    additional string-valued keyword arguments ("first" and "second" are
    such arguments in the case of this function), which will come from
    the --redOpts and --blueOpts command-line arguments to capture.py.
    For the nightly contest, however, your team will be created without
    any extra arguments, so you should make sure that the default
    behavior is what you want for the nightly contest.
    """

    # The following line is an example only; feel free to change it.
    return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########
class ReflexCaptureAgent(captureAgents.CaptureAgent):
    
    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index)
        #actions.remove('Stop')
        values = [self.evaluate(gameState, a) for a in actions]
        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]
        return random.choice(bestActions)

    def getSuccessor(self, gameState, action):
        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            return successor.generateSuccessor(self.index, action)
        else:
            return successor
    def evaluate(self, gameState, action):
        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)

        return features * weights

    def getFeatures(self, gameState, action):
        """
        Returns a counter of features for the state
        """

        features = util.Counter()
        successor = self.getSuccessor(gameState, action)
        features['successorScore'] = self.getScore(successor)

        return features

    def getWeights(self, gameState, action):
        """
        Normally, weights do not depend on the gamestate.
        They can be either a counter or a dictionary.
        """

        return {'successorScore': 1.0}


class OffensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that seeks food. This is an agent
    we give you to get an idea of what an offensive agent might look like,
    but it is by no means the best or only way to build an offensive agent.
    """
        
    def getFeatures(self, gameState, action):
                
        successorGameState = self.getSuccessor(gameState, action)
        successor = gameState.generateSuccessor(self.index, action)
        newPosition = successor.getAgentState(self.index).getPosition()
        oldFood = self.getFood(gameState)
        newEnemyStates = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        danger = [a for a in newEnemyStates if a.isPacman is False and a.getPosition() != None]
        newScaredTimes = [ghostState.scaredTimer for ghostState in danger]
        
        score = self.getScore(successor)
        g = 0
        f = 0
        m = 0
        
        foodList = oldFood.asList()
        if len(danger) > 0:
            for ghost in danger:
                ghostPosition = ghost.getPosition()
                (gX, gY) = (ghostPosition[0], ghostPosition[1])
                (pX, pY) = (newPosition)
                dist = abs(gX - pX) + abs(gY - pY)
                if dist > 0:
                    g = -(1 / (dist * dist * dist * dist))
                
        # Compute distance to the nearest food
        foodList = self.getFood(successor).asList()
        beforeFood = self.getFood(gameState).asList()
        
        if newPosition in beforeFood:
            f = 1
        if len(foodList) > 0:  # This should always be True, but better safe than sorry
            myPos = successor.getAgentState(self.index).getPosition()
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            m = abs(1/minDistance)

        return util.Counter({
            'food' : f,
            'closestfood' : m,
            'ghost' : g,
            'score' : score
        })

    def getWeights(self, gameState, action):
        return util.Counter({
            'food': 500,
            'closestfood': 100,
            'ghost' : 1000,
            'score' : 1
        })

class DefensiveReflexAgent(ReflexCaptureAgent):
    """
    A reflex agent that keeps its side Pacman-free.
    Again, this is to give you an idea of what a defensive agent could be like.
    It is not the best or only way to make such an agent.
    """
        
    def getFeatures(self, gameState, action):
        features = util.Counter()
        successor = self.getSuccessor(gameState, action)

        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0).
        features['onDefense'] = 1
        if myState.isPacman:
            features['onDefense'] = 0

        # Computes distance to invaders we can see.
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
        features['numInvaders'] = len(invaders)

        if len(invaders) > 0:
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

        if action == game.Directions.STOP:
            features['stop'] = 1

        rev = game.Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
        if action == rev:
            features['reverse'] = 1

        return features

    def getWeights(self, gameState, action):
        return {
            'numInvaders': -1000,
            'onDefense': 100,
            'invaderDistance': -10,
            'stop': -100,
            'reverse': -2
        }

        
class NomNomAgent(captureAgents.CaptureAgent):

    def registerInitialState(self, gameState):
        """
        This method handles the initial setup of the
        agent to populate useful fields (such as what team
        we're on). 
        
        A distanceCalculator instance caches the maze distances
        between each pair of positions, so your agents can use:
        self.distancer.getDistance(p1, p2)
        IMPORTANT: This method may run for at most 15 seconds.
        """

        """ 
        Make sure you do not delete the following line. If you would like to
        use Manhattan distances instead of maze distances in order to save
        on initialization time, please take a look at
        CaptureAgent.registerInitialState in captureAgents.py. 
        """

        captureAgents.CaptureAgent.registerInitialState(self, gameState)
        #print("width: ", gameState.data.layout.width)
        #print("height: ", gameState.data.layout.height)
        """ 
        Your initialization code goes here, if you need any.
        """

    def chooseAction(self, gameState):
        actions = gameState.getLegalActions(self.index) #list of possible actions

        # Choose the best action
        scores = [self.evaluationFunction(gameState, action) for action in actions]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best, if there's more than 1

        return actions[chosenIndex]
        
    def getSuccessor(self, gameState, action):
        """
        Finds the next successor which is a grid position (location tuple).
        """

        successor = gameState.generateSuccessor(self.index, action)
        pos = successor.getAgentState(self.index).getPosition()
        if pos != util.nearestPoint(pos):
            # Only half a grid position was covered.
            return successor.generateSuccessor(self.index, action)
        else:
            return successor
        
    def evaluationFunction(self, currentGameState, action):
        successor = currentGameState.generateSuccessor(self.index, action) #successor game state after this agent moves
        newPosition = successor.getAgentState(self.index).getPosition() #agent's position after moving
        oldFood = self.getFood(currentGameState) 
        newEnemyStates = [successor.getAgentState(i) for i in self.getOpponents(successor)] #successor state of each enemy
        newTeamPosition = [successor.getAgentState(i) for i in self.getTeam(successor)]
        danger = [a for a in newEnemyStates if a.isPacman is False and a.getPosition() != None] #list of each enemy that can kill
        newScaredTimes = [ghostState.scaredTimer for ghostState in danger]

        # *** Your Code Here ***
        
        #priority from low to high:
        #has danger
        #danger nearby
        #dead end with no food
        #free space / edible ghost (considered netural option)
        #enemy pacman nearby
        #has capsule
        #has food
        
        currEnemies = [currentGameState.getAgentState(j) for j in self.getOpponents(currentGameState)] 
        for e in currEnemies:
            if e.getPosition() != None and e.isPacman and e.getPosition() == newPosition and successor.getAgentState(self.index).isPacman is False and currentGameState.getAgentState(self.index).scaredTimer == 0:
                return 999 #eat edible enemy if they are right next to this agent
        
        foodList = oldFood.asList() #list of food positions
        for enemy in newEnemyStates:
            if enemy.isPacman and enemy.getPosition() != None and currentGameState.getAgentState(self.index).scaredTimer == 0: 
                foodList.append(enemy.getPosition()) #enemy in pacman form is considered food, as long as this agent is not a scared ghost
        capsules = self.getCapsules(currentGameState)
        for cap in capsules:
            foodList.append(cap) #capsules count as food
        
        for ghost in danger:
            if ghost.getPosition() == newPosition and ghost.scaredTimer == 0: 
                return 0 #if next space has a dangerous ghost, avoid that space
            if self.getMazeDistance(newPosition, ghost.getPosition()) < 2 and ghost.scaredTimer < 1: #ghost.scaredTimer < 2
                return 1 #if a dangerous ghost is nearby, try to avoid that space
        
        #if next space does not have anything to eat and theres a wall on 3 sides, try to avoid that space bc its easy to get trapped in by a ghost
        if newPosition not in foodList:
            x, y = newPosition
            wallCount = 0
            if successor.hasWall(int(x+1), int(y)) is True:
                wallCount +=1
            if successor.hasWall(int(x), int(y+1)) is True:
                wallCount +=1
            if successor.hasWall(int(x-1), int(y)) is True:
                wallCount +=1
            if successor.hasWall(int(x), int(y-1)) is True:
                wallCount +=1
            if wallCount >= 3:
                return 2
        
        minDistance = min([self.getMazeDistance(newPosition, food) for food in foodList])
        if newTeamPosition[0].isPacman and newTeamPosition[1].isPacman and self.getMazeDistance(newTeamPosition[0].getPosition(),newTeamPosition[1].getPosition()) < 4: 
            return 999 - minDistance - 2
        return 999-minDistance #gives a higher value the closer pacman is to food
    
 