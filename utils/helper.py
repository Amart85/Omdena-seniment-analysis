from tensorflow.keras import regularizers
from tensorflow.keras.layers import *
from tensorflow.keras.models import *
from tensorflow.keras.layers import concatenate
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import one_hot
from sklearn.model_selection import StratifiedKFold

def get_folds(df, source, target, split=4, getvalue=0):
    df.loc[:, "kfold"] = -1
    df = df.sample(frac=1).reset_index(drop=True)
    X = df[source].values
    y = df[target].values
    skf = StratifiedKFold(n_splits=split)

    for fold_, (train_, val_) in enumerate(skf.split(X=X, y=y)):
        df.loc[val_, "kfold"] = fold_
    return df.loc[df['kfold'] == getvalue]

def word_dictionary(text):
    text = set(list(text))
    dictionary = {}
    for i, word in enumerate(text):
        dictionary[word] = i

    return dictionary

def predict(text, model, tokenize, vocab, maxlen):
    text, _, _ = tokenize(text)
    vector, temp = [], []
    for d in text:
        for i in d:
            temp.extend(one_hot(i, vocab))
        vector.append(temp)
        temp=[]
    vector = pad_sequences(vector, maxlen=maxlen, padding="post")
    return vector

def get_model(X, y, vocab_size, embedding_size, maxlen, method):
    if method == "simpleRNN":
        model = Sequential()
        model.add(Embedding(vocab_size, embedding_size, input_length=maxlen ,name="embedding"))
        model.add(SimpleRNN(64))
        model.add(Flatten())
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(32, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(3, activation='softmax'))
    
    elif method == "bidRNN":
        model = Sequential()
        model.add(Embedding(vocab_size, embedding_size, input_length=maxlen ,name="embedding"))
        model.add(Bidirectional(LSTM(64)))
        model.add(Flatten())
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(3, activation='softmax'))
        
    elif method == "1DConv":
        model = Sequential()
        model.add(Embedding(vocab_size, embedding_size, input_length=maxlen ,name="embedding"))
        model.add(Conv1D(20, 6, activation='relu',kernel_regularizer=regularizers.l1_l2(l1=2e-3, l2=2e-3),bias_regularizer=regularizers.l2(2e-3)))
        model.add(MaxPooling1D(5))
        model.add(Dropout(0.1))
        model.add(GlobalMaxPooling1D())
        model.add(Dropout(0.2))
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.2))
        model.add(Dense(3, activation='softmax'))

    elif method == "lstm":
        sequence = Input(shape=(maxlen,), dtype='int32')
        embedded = Embedding(vocab_size, embedding_size, input_length=maxlen)(sequence)
        forwards = LSTM(64)(embedded)
        backwards = LSTM(64, go_backwards=True)(embedded)
        merged = concatenate([forwards, backwards])
        after_dp = Dropout(0.5)(merged)
        output = Dense(3, activation='softmax')(after_dp)
        model = Model(inputs=sequence, outputs=output)

    return model
