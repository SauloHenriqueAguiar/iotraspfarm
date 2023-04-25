import os
import math
import numpy as np
import datetime as dt
from numpy import newaxis
from core.utils import Timer
from keras.layers import Dense, Activation, Dropout, LSTM
from keras.models import Sequential, load_model
from keras.callbacks import EarlyStopping, ModelCheckpoint

class Model():
	"""Uma classe para construir e inferir um modelo lstm"""

	def __init__(self):
		self.model = Sequential()

	def load_model(self, filepath):
		print('[Model] Carregando modelo do arquivo %s' % filepath)
		self.model = load_model(filepath)

	def build_model(self, configs):
		timer = Timer()
		timer.start()

		for layer in configs['model']['layers']:
			neurons = layer['neurons'] if 'neurons' in layer else None
			dropout_rate = layer['rate'] if 'rate' in layer else None
			activation = layer['activation'] if 'activation' in layer else None
			return_seq = layer['return_seq'] if 'return_seq' in layer else None
			input_timesteps = layer['input_timesteps'] if 'input_timesteps' in layer else None
			input_dim = layer['input_dim'] if 'input_dim' in layer else None

			if layer['type'] == 'dense':
				self.model.add(Dense(neurons, activation=activation))
			if layer['type'] == 'lstm':
				self.model.add(LSTM(neurons, input_shape=(input_timesteps, input_dim), return_sequences=return_seq))
			if layer['type'] == 'dropout':
				self.model.add(Dropout(dropout_rate))

		self.model.compile(loss=configs['model']['loss'], optimizer=configs['model']['optimizer'])

		print('[Model] Modelo Compilado')
		timer.stop()

	def train(self, x, y, epochs, batch_size, save_dir):
		timer = Timer()
		timer.start()
		print('[Model] Treinamento iniciado')
		print('[Model] %s epochs, %s batch size' % (epochs, batch_size))
		#salva modelo na pasta saved_models
		save_fname = os.path.join(save_dir, '%s-e%s.h5' % (dt.datetime.now().strftime('%d%m%Y-%H%M%S'), str(epochs)))
		callbacks = [
			EarlyStopping(monitor='val_loss', patience=2),
			ModelCheckpoint(filepath=save_fname, monitor='val_loss', save_best_only=True)
		]
		self.model.fit(
			x,
			y,
			epochs=epochs,
			batch_size=batch_size,
			callbacks=callbacks
		)
		# salva o modelo	
		self.model.save(save_fname)
  
		#remove o arquivo ant
		#os.remove('saved_models\28122022-151358-e1.h5')
		os.remove(save_fname)
		print('[Model] Treinamento Concluído. Modelo salvo como %s' % save_fname)
		timer.stop()

	def train_generator(self, data_gen, epochs, batch_size, steps_per_epoch, save_dir):
		timer = Timer()
		timer.start()
		print('[Model] Treinamento iniciado')
		print('[Model] %s epochs, %s batch size, %s batches per epoch' % (epochs, batch_size, steps_per_epoch))
		  #salva modelo na pasta saved_models
		save_fname = os.path.join(save_dir, '%s-e%s.h5' % (dt.datetime.now().strftime('%d%m%Y-%H%M%S'), str(epochs)))
		callbacks = [
			ModelCheckpoint(filepath=save_fname, monitor='loss', save_best_only=True)
		]
		self.model.fit_generator(
			data_gen,
			steps_per_epoch=steps_per_epoch,
			epochs=epochs,
			callbacks=callbacks,
			workers=1
		)
		
		print('[Model] Treinamento Concluído. Modelo salvo como %s' % save_fname)
		timer.stop()

	def predict_point_by_point(self, data):
		#Preveja cada passo de tempo dada a última sequência de dados verdadeiros, na verdade prevendo apenas 1 passo à frente de cada vez
		print('[Model] Prevendo ponto a ponto...')
		predicted = self.model.predict(data)
		predicted = np.reshape(predicted, (predicted.size,))
		return predicted

	def predict_sequences_multiple(self, data, window_size, prediction_len):
		#Preveja a sequência de 50 passos antes de mudar a previsão para avançar em 50 passos
		print('[Model] Prevendo Sequências Múltiplas...')
		prediction_seqs = []
		for i in range(int(len(data)/prediction_len)):
			curr_frame = data[i*prediction_len]
			predicted = []
			for j in range(prediction_len):
				predicted.append(self.model.predict(curr_frame[newaxis,:,:])[0,0])
				curr_frame = curr_frame[1:]
				curr_frame = np.insert(curr_frame, [window_size-2], predicted[-1], axis=0)
			prediction_seqs.append(predicted)
		return prediction_seqs

	def predict_sequence_full(self, data, window_size):
		#Mude a janela em 1 nova previsão a cada vez, execute novamente as previsões na nova janela
		print('[Model]Prevendo Sequências Completas...')
		curr_frame = data[0] #índice para a primeira janela de dados recebidos
		predicted = []
		for i in range(len(data)):
			predicted.append(self.model.predict(curr_frame[newaxis,:,:])[0,0]) #prever a janela de dados mais recente, anexar matriz de resultados[0,0] ao resultado previsto
			curr_frame = curr_frame[1:] #remover dados mais antigos na janela
			curr_frame = np.insert(curr_frame, [window_size-2], predicted[-1], axis=0) #anexar novos dados previstos ao último da janela, 
		return predicted
		
        #predictions = model.predict_sequence_full(x_test, configs['data']['sequence_length'])

	def predict_sequence_live(self, data, window_size):
		print('[Model] Predicting Sequences live...')
		curr_frame = data[0] #índice para a primeira janela de dados recebidos
		predicted = []
		predicted.append(self.model.predict(curr_frame[newaxis,:,:])[0,0]) #prever a janela de dados mais recente, anexar matriz de resultados[0,0] ao resultado previsto
		return predicted
	
	# prever o proximo dia de dados
	def predict_next_day(self, data, window_size):
		print('[Model] Predicting next day...')
		curr_frame = data[0]	#índice para a primeira janela de dados recebidos
		predicted = []
		for i in range(len(data)):
			predicted.append(self.model.predict(curr_frame[newaxis,:,:])[0,0])
			curr_frame = curr_frame[1:]
			curr_frame = np.insert(curr_frame, [window_size-2], predicted[-1], axis=0)
		return predicted
	
		
		# prever a proxima semana de dados
	def predict_next_week(self, data, window_size):
		print('[Model] Predicting next week...')
		curr_frame = data[0]	#índice para a primeira janela de dados recebidos
		predicted = []
		for i in range(len(data)):
			predicted.append(self.model.predict(curr_frame[newaxis,:,:])[0,0])
			curr_frame = curr_frame[1:]
			curr_frame = np.insert(curr_frame, [window_size-2], predicted[-1], axis=0)
		return predicted
	