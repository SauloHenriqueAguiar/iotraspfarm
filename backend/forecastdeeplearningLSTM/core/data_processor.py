import math
import numpy as np
import pandas as pd

class DataLoader():
    """Uma classe para carregar e transformar dados para o modelo lstm"""

    def __init__(self, filename, split, cols):
        dataframe = pd.read_csv(filename)
        i_split = int(len(dataframe) * split)
        self.data_train = dataframe.get(cols).values[:i_split]
        self.data_test  = dataframe.get(cols).values[i_split:]
        self.len_train  = len(self.data_train)
        self.len_test   = len(self.data_test)
        self.len_train_windows = None

    def get_test_data(self, seq_len, normalise):
        '''
       Criar janelas de dados de teste x, y
         Aviso: método em lote, não generativo, certifique-se de ter memória suficiente para
         carregar dados, caso contrário, reduza o tamanho da divisão de treinamento.
        '''
        data_windows = []
        for i in range(self.len_test - seq_len): 
            data_windows.append(self.data_test[i:i+seq_len]) #preparar dados de acordo com seq_len

        data_windows = np.array(data_windows).astype(float)
        data_windows = self.normalise_windows(data_windows, single_window=False) if normalise else data_windows

        x = data_windows[:, :-1]  #obter matriz(array) 3D
        y = data_windows[:, -1, [0]] #obter matriz(array) 2D
        return x,y

    def get_train_data(self, seq_len, normalise):
        '''
       Crie janelas de dados de trem x, y
         Aviso: método em lote, não generativo, certifique-se de ter memória suficiente para
         carregar dados, caso contrário, use o método generate_training_window().
        '''
        data_x = []
        data_y = []
        for i in range(self.len_train - seq_len):#
            x, y = self._next_window(i, seq_len, normalise)
            data_x.append(x)
            data_y.append(y)
        return np.array(data_x), np.array(data_y)

    def generate_train_batch(self, seq_len, batch_size, normalise):
        '''Gera um gerador de dados de treinamento do nome do arquivo em uma determinada lista de colunas divididas para treinar/teste'''
        i = 0
        while i < (self.len_train - seq_len):
            x_batch = []
            y_batch = []
            for b in range(batch_size):
                if i >= (self.len_train - seq_len):
                    # condição de parada para um lote final menor se os dados não forem divididos uniformemente
                    yield np.array(x_batch), np.array(y_batch)
                    i = 0
                x, y = self._next_window(i, seq_len, normalise)
                x_batch.append(x)
                y_batch.append(y)
                i += 1
            yield np.array(x_batch), np.array(y_batch)

    def _next_window(self, i, seq_len, normalise):
        '''Gera a próxima janela de dados a partir do local de índice fornecido i'''
        window = self.data_train[i:i+seq_len]
        window = self.normalise_windows(window, single_window=True)[0] if normalise else window
        x = window[:-1]
        y = window[-1, [0]]
        return x, y

    def normalise_windows(self, window_data, single_window=False):
        '''Gera a próxima janela de dados a partir do local de índice fornecido i'''
        normalised_data = []
        window_data = [window_data] if single_window else window_data
        for window in window_data:
            normalised_window = []
            for col_i in range(window.shape[1]):
                normalised_col = [((float(p) / float(window[0, col_i])) - 1) for p in window[:, col_i]]
                normalised_window.append(normalised_col)
            normalised_window = np.array(normalised_window).T # remodelar e transpor a matriz de volta ao formato multidimensional original
            normalised_data.append(normalised_window)
        return np.array(normalised_data)
    
 # get train data daily data 24 hours
