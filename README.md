# yamlx

yaml内で変数や計算式を扱えるようにしたもの

## How to install

```
>> pip install yamlx
```

## How to use

存在しているキーの値を代入したいとき　->  \${key1.key2.key3 ...}

計算式を入れたいとき -> 普通に演算子を用いて書いてください(+,-,\*,/,%,//,\*\*)が使えます．\${...}も使えます．

```
# example.ymx

train :
  batch_size    : 16
  learning_rate : 0.001
  epochs        : 50

signal : 
  sample_rate : 16000
  hop_size : 256
  n_mels   : 80
  eps      : 1 / 100
  max_len  : ${signal.sample_rate} // ${signal.hop_size}

model :
  input_dim      : 128
  input_channel  : ${signal.n_mels}
  output_channel : 5
```

```
>> import vaml
>> path_to_vaml = "./example.vaml"
>> data = vaml.load(path_to_vaml)
>> print(data)
>> {'train': {'batch_size': 16, 'learning_rate': 0.001, 'epochs': 50}, 'signal': {'sample_rate': 16000, 'hop_size': 256, 'n_mels': 80, 'eps': 0.01, 'max_len': 62.0}, 'model': {'input_dim': 128, 'input_channel': 80, 'output_channel': 5}}  
```
