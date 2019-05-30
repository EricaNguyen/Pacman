import random
import time

import captureAgents
import game
import util

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
        first = 'DummyAgent', second = 'DummyAgent'):
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

class DummyAgent(captureAgents.CaptureAgent):
    """
    A Dummy agent to serve as an example of the necessary agent structure.
    You should look at baselineTeam.py for more details about how to
    create an agent as this is the bare minimum.
    """

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
        """ 
        Your initialization code goes here, if you need any.
        """

    def chooseAction(self, gameState):
        """
        Picks among actions randomly.
        """
        actions = gameState.getLegalActions(self.index)

        """ 
        You should change this in your own agent.
        """
        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in actions]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        # *** Add more of your code here if you want to ***

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
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (oldFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """

        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = self.getSuccessor(currentGameState, action)
        successor = currentGameState.generateSuccessor(self.index, action)
        newPosition = successor.getAgentState(self.index).getPosition()
        oldFood = self.getFood(currentGameState)
        #newGhostStates = successorGameState.getGhostStates()
        newEnemyStates = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        newTeamPosition = [successor.getAgentState(i) for i in self.getTeam(successor)]
        danger = [a for a in newEnemyStates if a.isPacman is False and a.getPosition() != None]
        newScaredTimes = [ghostState.scaredTimer for ghostState in danger]

        # *** Your Code Here ***
        
        #priority from low to high:
        #has danger
        #danger nearby
        #free space
        #has capsule
        #has food
        foodList = oldFood.asList()
        if len(danger) > 0:
            for ghost in danger:
                if ghost.getPosition() == newPosition and ghost.scaredTimer == 0: 
                    return 0 #if next space has a dangerous ghost
                if self.getMazeDistance(newPosition, ghost.getPosition()) < 2 and ghost.scaredTimer < 2:
                    return 1 #if a dangerous ghost is nearby
            
        minDistance = min([self.getMazeDistance(newPosition, food) for food in foodList])
        # distance = self.getMazeDistance(newTeamPosition[0].getPosition(),newTeamPosition[1].getPosition())
        if newTeamPosition[0].isPacman and newTeamPosition[1].isPacman and self.getMazeDistance(newTeamPosition[0].getPosition(),newTeamPosition[1].getPosition()) < 4: 
            return 999 - minDistance - 2
        return 999-minDistance #gives a higher value the closer pacman is to food
 
 
class DefensiveReflexAgent(captureAgents.CaptureAgent):
    """
    A reflex agent that keeps its side Pacman-free.
    Again, this is to give you an idea of what a defensive agent could be like.
    It is not the best or only way to make such an agent.
    """
    def chooseAction(self, gameState):
        """
        Picks among the actions with the highest Q(s, a).
        """

        actions = gameState.getLegalActions(self.index)

        # You can profile your evaluation time by uncommenting these lines
        # start = time.time()
        values = [self.evaluate(gameState, a) for a in actions]
        # print('eval time for agent %d: %.4f' % (self.index, time.time() - start))

        maxValue = max(values)
        bestActions = [a for a, v in zip(actions, values) if v == maxValue]

        return random.choice(bestActions)

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

    def evaluate(self, gameState, action):
        """
        Computes a linear combination of features and feature weights
        """

        features = self.getFeatures(gameState, action)
        weights = self.getWeights(gameState, action)

        return features * weights

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
        
