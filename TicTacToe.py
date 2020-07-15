import collections.abc
from easyAI import TwoPlayersGame, Negamax
from easyAI.Player import Human_Player
import speech_recognition as sr
from gtts import gTTS
import os
import nltk
from nltk import grammar, parse
from nltk import load_parser 
from nltk.parse.generate import generate

# ______________________________________________________________________________
class Thing:
    def __repr__(self):
        return '<{}>'.format(getattr(self, '__name__', self.__class__.__name__))

    def is_alive(self):
        return hasattr(self, 'alive') and self.alive

    def show_state(self):
        print("I don't know how to show_state.")
#-----------------------------------------------------------------------
class Agent(Thing):
    def __init__(self, program=None):
        self.alive = True
        self.performance = 0

        if program is None or not isinstance(program, collections.abc.Callable):
            print("Can't find a valid program for {}, falling back to default.".format(self.__class__.__name__))

            def program(percept):
                return eval(input('Percept={}; action? '.format(percept)))

        self.program = program
#-----------------------------------------------------------------------
def TraceAgent(agent):
    old_program = agent.program

    def new_program(percept):
        action = old_program(percept)
        print('{} percibe {} y juega en la casilla {}'.format(agent, percept, action))
        return action

    agent.program = new_program
    return agent
# ______________________________________________________________________________
class Environment:
    def __init__(self):
        self.things = []
        self.agents = []

    def percept(self, agent):
    	raise NotImplementedError

    def execute_action(self, agent, action):
        raise NotImplementedError

    def default_jugadas(self, thing):
        return None

    def exogenous_change(self):
        pass

    def is_done(self):
        return not any(agent.is_alive() for agent in self.agents)

    def step(self):
        if not self.is_done():
            actions = []
            for agent in self.agents:
                if agent.alive:
                    actions.append(agent.program(self.percept(agent)))
                else:
                    actions.append("")
            for (agent, action) in zip(self.agents, actions):
                self.execute_action(agent, action)
            self.exogenous_change()

    def run(self, steps=1):
        for step in range(steps):
            if self.is_done():
                return
            self.step()

    def agrega_agente(self, thing, location=None):
        if not isinstance(thing, Thing):
            thing = Agent(thing)
        if thing in self.things:
            print("Can't add the same thing twice")
        else:
            thing.location = location if location is not None else self.default_jugadas(thing)
            self.things.append(thing)
            if isinstance(thing, Agent):
                thing.performance = 0
                self.agents.append(thing)
# ______________________________________________________________________________
def Reflex():
    def program(percept):
    	game, nplayer = percept
    	grammar1 = grammar.FeatureGrammar.fromstring("""
          %start S                                           
          S[SEM=<vp(?np)>] -> VP[SEM=?np] NP[SEM=?vp]
          VP[SEM=<jugar>] -> "Jugar" | "jugar"
          NP[SEM=?v] -> CO[SEM=?v]          
          CO[SEM=<\\x.coord(x)>] -> "1,1" | "1,2" | "1,3" | "2,1" | "2,2" | "2,3" | "3,1" | "3,2" | "3,3"
          """)
    	if nplayer == 1:
    		while True:
    			r = sr.Recognizer()
    			with sr.Microphone() as source:
    				print("Di tu tirada con 'Jugar x,y'...")
    				r.adjust_for_ambient_noise(source, duration=1)
    				audio = r.listen(source,phrase_time_limit=5)
    				estado = r.recognize_google(audio, language="es-MX")
    				print(estado)
    				tokens = estado.split()
    				rd_parser = parse.FeatureEarleyChartParser(grammar1)
    				error=0
    				try:
    					for tree in rd_parser.parse(tokens):
    						error=""
    				except ValueError:
    					error="Error, gramática no válida"
    					print("Audio detectado: "+estado)
    				if error=="":
    					try:
    						if estado == "jugar 1,1":
    							move = '1'
    							estado = '1'
    							speak("El jugador tiró en la casilla"+estado)
    						elif estado == "jugar 1,2":
    							move = '2'
    							estado = '2'
    							speak("El jugador tiró en la casilla"+estado)
    						elif estado == "jugar 1,3":
    							move = '3'
    							estado = '3'
    							speak("El jugador tiró en la casilla"+estado)
    						elif estado == "jugar 2,1":
    							move = '4'
    							estado = '4'
    							speak("El jugador tiró en la casilla"+estado)
    						elif estado == "jugar 2,2":
    							move = '5'
    							estado = '5'
    							speak("El jugador tiró en la casilla"+estado)
    						elif estado == "jugar 2,3":
    							move = '6'
    							estado = '6'
    							speak("El jugador tiró en la casilla"+estado)
    						elif estado == "jugar 3,1":
    							move = '7'
    							estado = '7'
    							speak("El jugador tiró en la casilla"+estado)
    						elif estado == "jugar 3,2":
    							move = '8'
    							estado = '8'
    							speak("El jugador tiró en la casilla"+estado)
    						elif estado == "jugar 3,3":
    							move = '9'
    							estado = '9'
    							speak("El jugador tiró en la casilla"+estado)
    						else:
    							move = '0'
    							estado = '0'
    							speak("No es una jugada válida")
    						return estado
    					except sr.UnknownValueError:
    						print("No se reconoce el audio")
    					except sr.RequestError as e:
	        				print("No puede generar resultados del servicio de Google Speech Recognition; {0}".format(e))
    				else:
    					print("El audio hablado no es válido en la gramática.")
    				if estado in ('1','2','3','4','5','6','7','8','9'):
    					move = estado
    				else:
    					print(estado+" no es válido, vuelve a decir tu jugada: ")
    					r.adjust_for_ambient_noise(source, duration=1)
    					audio = r.listen(source,phrase_time_limit=5)
    					estado = r.recognize_google(audio, language="es-MX")
    					move = estado
    				return move
    				break

    	if nplayer == 2:
    		if algorithm(game):
    			move = algorithm(game)
    			return move
    return Agent(program)
# ______________________________________________________________________________
class TicTacToe(TwoPlayersGame):
    def __init__(self, players):
    	self.board = [0 for i in range(9)]
    	self.players = players
    	self.nplayer = 1
    
    def possible_moves(self):
        return [i+1 for i,e in enumerate(self.board) if e==0]
    
    def make_move(self, move):
        self.board[int(move)-1] = self.nplayer
    
    def lose(self):
        return any( [all([(self.board[c-1]== self.nopponent)
                      for c in line])
                      for line in [[1,2,3],[4,5,6],[7,8,9],
                                   [1,4,7],[2,5,8],[3,6,9],
                                   [1,5,9],[3,5,7]]])
        
    def is_over(self):
        return (self.possible_moves() == []) or self.lose()
        
    def show(self):  
        print ('\n'+'\n'.join([
                        ' '.join([['.','O','X'][self.board[3*j+i]]
                        for i in range(3)])
                 for j in range(3)]) +'\n' )
                 
    def scoring(self):
        return -100 if self.lose() else 0

#---------------------------------------------------------------------------------
class TrivialEnvironment(Environment):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.board = self.game.board
        self.nplayer = self.game.nplayer
        self.move = {}

    def thing_classes(self):
        return [Reflex]

    def percept(self, agent):
        return self.game, self.nplayer

    def execute_action(self, agent, action):
        if self.nplayer == 1:
            self.move = action

        if self.nplayer == 2:
            self.move = action
            self.text = 'Jugador dos juega ' + str(self.move)
            speak(self.text)
# ----------------------------------------------------------------------
class AI_Player:
    def __init__(self, algorithm, name = 'AI'):
    	self.algorithm = algorithm
    	self.name = name
    	self.move = {}

    def ask_move(self, game):  
        self.move = correr_agente(TrivialEnvironment(game), Reflex())     
        return self.move
#-----------------------------------------------------------------------------
class MyHuman_Player:
    def __init__(self, name = 'Human'):
        self.name = name
        self.move = {}

    def ask_move(self, game):
        possible_moves = game.possible_moves()
        possible_moves_str = list(map(str, game.possible_moves()))
        move = "NO_MOVE_DECIDED_YET"
        while True:
            move = correr_agente(TrivialEnvironment(game), Reflex())
            if move == 'show moves':
                print ("Possible moves:\n"+ "\n".join(
                       ["#%d: %s"%(i+1,m) for i,m in enumerate(possible_moves)])
                       +"\nType a move or type 'move #move_number' to play.")
            elif move == 'quit':
                raise KeyboardInterrupt
            elif move.startswith("#"):
                move = possible_moves[int(move[6:])-1]
                return move
            elif str(move) in possible_moves_str:
                move = possible_moves[possible_moves_str.index(str(move))]
                return move
            else:
                print('Jugada no permitida. \nIntenta otra jugada')
#-------------------------------------------------------------------------------
estado = 0
algorithm = Negamax(7)

def speak(audioString):
    tts = gTTS(text=audioString, lang='es')
    tts.save("audio.mp3")
    os.system("mpg123 audio.mp3")

def Simulator():
	game = TicTacToe([MyHuman_Player(),AI_Player(algorithm)])
	game.play()

def correr_agente(environment, agent):
    e = environment
    a = agent
    e.agrega_agente(TraceAgent(a))
    e.run()
    move = e.move
    return move

if __name__ == "__main__":
    Simulator()