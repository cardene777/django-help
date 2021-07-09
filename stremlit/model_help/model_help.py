import streamlit as st
import pykakasi
from googletrans import Translator
import re

translator = Translator()


def translate_en(text):
    """
    translate jp word to en
    :param text:
    :return: en word
    """
    en_text: str = translator.translate(text, src='ja', dest='en').text
    return en_text


def choice_selectbox():
    """
    choice field tuple
    :return: select field
    """
    selects: tuple = (
        "文字列（文字制限あり）",
        "文字列（文字制限なし）",
        "数字（整数）",
        "数字（浮動小数点数）",
        "画像",
        "論理値（True/False）",
        "日付",
        "日付＋時刻"
        "１対１",
        "１対多",
        "多対多"
    )
    return selects


def choice_model_field(str_model_field):
    """
    選択に応じたフィールドを選択
    :param str_model_field:
    :return: model field (str)
    """
    model_field: dict = {
        "文字列（文字制限あり）": "CharField",
        "文字列（文字制限なし）": "TextField",
        "数字（整数）": "IntegerField",
        "数字（浮動小数点数）": "FloatField",
        "画像": "ImageField",
        "論理値（True/False）": "BooleanField",
        "日付": "DateField",
        "日付＋時刻": "DateTimeField",
        "１対１": "OneToOneField",
        "１対多": "ForeignKey",
        "多対多": "ManyToManyField",
    }
    return model_field[str_model_field]


def select_argument(filed_name):
    base_field: list = [
        "フィールド簡潔に説明[verbose_name]（任意）",
        "入力しなくてもOKにする True/False[blank]（任意）",
        "空の値をOKにする True/False[null]（任意）",
        "選択できるようにする タプル形式[choices]（任意）",
        "デフォルトの値を設定[default]（任意）",
        "入力の際のヘルプテキスト[help_text]（任意）",
        "重複をしないようにする True/False[unique]（任意）"
    ]

    reference_field: list = [
        "関連先フィールド（必須）",
        "フィールド簡潔に説明[verbose_name]（任意）",
    ]

    argument_dict: dict = {
        "CharField": base_field + ["最大文字数[max_length]（必須）"],
        "TextField": base_field,
        "IntegerField": base_field,
        "FloatField": base_field,
        "ImageField": base_field + ["アップロード先指定[upload_to]（必須）"],
        "BooleanField": base_field,
        "DateField": base_field,
        "DateTimeField": base_field,
        "OneToOneField": reference_field,
        "ForeignKey": reference_field,
        "ManyToManyField": reference_field,
    }
    return argument_dict[filed_name]


def extraction_argument_name(text):
    pattern: str = '(?<=\[).*(?=\])'
    extraction_text: str = re.search(pattern, text).group()
    return extraction_text


def main():
    # 使い方
    st.title("使い方")
    st.subheader("①左のサイドバーにモデル名を入力してください。")
    st.subheader("②モデルに必要なフィールドをひらがなで入力していってください。（個数を増やしたい時は「＋」を押してください。")
    st.subheader("③右のページにある「フィールド選択」から、適切なフィールドを選択してください。")
    st.subheader("④必要なもののチェックボックスにチェックを入れて、値を入力してください。")
    st.subheader("⑤全てのフィールドの入力が終わったら一番下の完成形をコピーして、自分のアプリケーションに貼り付けてください。")

    # サイドバー
    st.sidebar.title('フィールド')

    model_name: str = st.sidebar.text_input("モデル名をひらがなで入力")

    field_number: int = st.sidebar.number_input("フィールドの数を調整してください。", 1, 50, 1)

    fields: list = []
    count = 1
    for index in range(field_number):
        field = st.sidebar.text_input("モデルのフィールド名を日本語で入力", key=f"field{int(index) + 1}")
        if field:
            fields.append(translate_en(field))

    model_name_capitaloze: str = ""

    if model_name:
        model_name_capitaloze: str = translate_en(model_name).capitalize()
        st.title(f"{model_name_capitaloze}Model")

    all_code: str = f"class {model_name_capitaloze}Model(models.Model): \n"
    for field_index in range(len(fields)):
        models_fields: dict = {}
        field: str = fields[field_index].lower()
        st.header(field)
        option = st.selectbox(
            "フィールド選択",
            choice_selectbox(),
            key=f"select{field_index+1}{field_index + 1}"
        )
        fields_name: str = choice_model_field(option)
        arguments: list = select_argument(fields_name)

        argument_list: dict = {}
        for argument_index, argument in enumerate(arguments):
            ag = st.checkbox(argument, key=f"checkbox{field_index+1}{argument_index + 1}{field_index + 1}")
            if ag:
                ag_text: str = st.text_input("入力してください。", key=f"ag{field_index+1}{argument_index + 1}{field_index + 1}")
                extraction_text: str = extraction_argument_name(argument)
                argument_list[extraction_text] = ag_text

        models_fields[field] = argument_list

        for model_name, model_dict in models_fields.items():
            arguments_names: list = model_dict.keys()
            arguments_values: list = model_dict.values()
            value_list: list = [f'{arguments_name} = {arguments_value}, ' for arguments_name, arguments_value in
                                zip(arguments_names, arguments_values)]
            valus: str = "\n".join([f"        {value}" for value in value_list])
            codes: str = f"    {model_name} = models.{fields_name} {'('} \n" \
                         f"{valus} \n    {')'} \n\n"

            all_code += codes
            st.code(codes, language='python')

    st.header("完成形")
    st.write("コピーして貼り付けてください！")
    st.code(all_code, language='python')


if __name__ == '__main__':
    main()