import re
import pyparsing
from omegaconf import DictConfig, OmegaConf

from pyparsing import Word, Keyword, Suppress, Group, ZeroOrMore, Regex
from pyparsing import alphanums, infix_notation, oneOf, opAssoc

#パース可能な辞書型
DICT_TYPES = [dict, DictConfig]

# 計算可能な演算子
OPERATORS = ["+", "-", "*", "/", "//", "**"]

# 単項演算，二項演算
UNARY, BINARY = 1, 2

# 構文規則 --------------------------------------------------------------------
# Reference : https://qiita.com/knoguchi/items/6f9b7383b7252a9ebdad

VAR = Keyword("$")
POINT = Suppress(".")
LBRACE = Suppress("{")
RBRACE = Suppress("}")

ident = Word(alphanums + "-" + "_")
number = Regex(r"\d+(\.\d*)?([eE][+-]?\d+)?")

variable = Group(VAR + LBRACE + ident + ZeroOrMore(POINT + ident) + RBRACE)
factor = variable | number

expression = infix_notation(
    factor,
    [
        (oneOf("+ -"), UNARY, opAssoc.RIGHT),  # 符号は最優先。
        (oneOf("* / // **"), BINARY, opAssoc.LEFT),  # 掛け算割り算は足し算引き算より優先
        (oneOf("+ -"), BINARY, opAssoc.LEFT),
    ],
)
# -----------------------------------------------------------------------------


def parse(input_dict):
    """
    yamlとしてデシリアライズした辞書型データを解析
    ${...}で指定されている変数部と計算式部を変換していく

    input  > input_data(dict)  : dict data that loaded from yamlx file as yaml file
    output > parsed_data(dict) : parsed dict data
    """

    # internal func -----------------------------------------------------
    # ネストしているvalueを再帰的に解析
    def parse_dict_recursive(original_dict: dict, target_value: dict):
        new_dict = {}

        for k, v in target_value.items():
            # ネストしているとき-------------------------
            if type(v) in DICT_TYPES:
                new_dict[k] = parse_dict_recursive(original_dict, v)
                continue
            # 式や変数が含まれているとき------------------
            if has_expression(v):
                new_dict[k] = parse_expression(original_dict, v)
                continue
            # ---------------------------------------
            new_dict[k] = v

        return new_dict
    # -----------------------------------------------------------------------
    parsed_data = parse_dict_recursive(input_dict, input_dict)

    return parsed_data


def has_expression(value: any):
    """
    受け取ったvalueに変数や式が含まれているか判定
    valueがstr以外 -> False
    valueがstr     -> $か演算子が含まれていたら True /はパスの可能性もあるので演算子の場合だけTrue
    """
    ops = ["+", "-", "*", "//", "**", "$"]

    if type(value) != str:
        return False
    if any(op in value for op in ops):
        return True
    if '/' in value:
        slash_sep_list = value.split('/')
        return all([s.isdecimal() for s in slash_sep_list])
    else:
        return False


def parse_expression(original_dict: dict, expr: str):
    """
    式を解析して計算
    """

    try:
        # 構文解析：解析された構文木をリストとして獲得
        parse_result = expression.parse_string(expr)[0].asList()
    except pyparsing.exceptions.ParseException as e:
        raise SyntaxError(e)

    # 構文木から式を計算
    expr_result = calc_expression(original_dict, parse_result)

    return expr_result


def calc_expression(original_dict: dict, expr: list):
    # 構文木から式を再帰的に計算

    # 項が変数のみのとき (構文木のリストの先頭が'$'のとき)------------------------
    if expr[0] == "$":
        try:
            new_value = get_value_from_key_list(original_dict, expr[1:])
        except KeyError as e:
            # 存在しないキーの場合はKeyError
            raise KeyError("Invalid key : {}".format(".".join(expr[1:])))

        return new_value

    # 構文木の中に式があるとき-----------------------------------------------
    terms = []  # 項を格納するリスト
    operator = None  # 演算子
    for term in expr:
        # -----------------------------------
        if term in OPERATORS:
            operator = term
            continue

        # 項が式であるとき -> 再帰で計算----------
        if type(term) == list:
            term = calc_expression(original_dict, term)

        # ------------------------------------
        terms.append(term)

    operation_result = calc_operation(terms, operator)

    return operation_result


def get_value_from_key_list(data: dict, k_list: list):
    # キーのリストを受け取り，辞書型データから該当するキーの値を返す

    for k in k_list:
        data = data[k]
    return data


def calc_operation(terms: list, operator: str):
    terms = [float(t) for t in terms]  # 各項をfloatに変換
    op_type = len(terms)  # 演算の種類 (項が一つ->単項演算, 項が二つ->二項演算)

    # 単項演算-----------------------------------------
    if op_type == UNARY:
        term = terms[0]
        match operator:
            case "+":
                return term
            case "-":
                return -term
            case _:
                raise SyntaxError("Invalid operator : {}".format(operator))

    # 二項演算-------------------------------------------
    elif op_type == BINARY:
        match operator:
            case "+":
                return terms[0] + terms[1]
            case "-":
                return terms[0] - terms[1]
            case "*":
                return terms[0] * terms[1]
            case "/":
                return terms[0] / terms[1]
            case "%":
                return terms[0] % terms[1]
            case "//":
                return terms[0] // terms[1]
            case "**":
                return terms[0] ** terms[1]
            case _:
                raise SyntaxError("Invalid operator : {}".format(operator))
    # ---------------------------------------------------------------
    else:
        raise SyntaxError


if __name__ == '__main__':

    print("load ymx file by OmegaConf and parse")
    p = "./example.ymx"
    d = OmegaConf.load(p)
    d = parse(d)
    print(d)