import yaml
import errno
import os

from parser import parse

def load(path: str):

    """
    input   : path (str)    > vaml file path as string
    output  : data (dict)   > parsed dict

    example)

    << INPUT(vaml file) >>
    train :
      batch_size    : 16
      learning_rate : 0.001
      epochs        : 50

    signal : 
      sample_rate : 16000
      hop_size    : 256
      n_mels      : 80
      eps         : 1 / 100
      max_len     : ${signal.sample_rate} // ${signal.hop_size}

    model :
      input_dim      : 128
      input_channel  : ${signal.n_mels}
      output_channel : 8

    << OUTPUT >>
    {"train"    : {"batch_size" : 16, "learning_rate" : 0.001, "epochs" : 50},
     "signal"   : {"sample_rate" : 16000, "hop_size" : 256, "n_mels" : 80, 
                   "eps" : 0.01, "max_len" : 62},
     "model"    : {"input_dim" : 128, "input_channel" : 80, "output_channel" : 5}
    }

    """

    # ファイルは存在してますか------------------------------
    if os.path.isfile(path) == False:
        raise FileNotFoundError("No such file or directory : {}".format(path))


    # ファイル読み込み yamlとして読み込む--------------------
    try:
        with open(path, 'r') as f:
            dict_from_yaml = yaml.safe_load(f)

    except yaml.parser.ParserError as e:
        raise SyntaxError(e)

    # 解析 -------------------------------------------
    dict_vaml = parse(dict_from_yaml)

    return dict_vaml



if __name__ == "__main__":

    p = "./example.vaml"
    d = load(p)

    print(d)