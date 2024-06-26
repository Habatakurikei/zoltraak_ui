# 2024-06-17 DY revised to enable multiple LLM options
import os
import shutil
import subprocess
import sys

import zoltraak
from zoltraak.llms.common import call_llm
from zoltraak.utils.prompt_import import load_prompt


CODE_GEN_LLM = "anthropic/claude-3-5-sonnet-20240620"


class TargetCodeGenerator:

    def __init__(self,
                 source_file_path,
                 target_file_path,
                 past_source_file_path,
                 source_hash):
        self.source_file_path = source_file_path
        self.target_file_path = target_file_path
        self.past_source_file_path = past_source_file_path
        self.source_hash = source_hash

    def generate_target_code(self):
        """
        ソースファイルからターゲットファイルを生成するメソッド
        """
        # 1. 準備
        # print("1. コード生成の準備")
        create_domain_grimoire, target_dir = self.prepare_generation()

        # 2. ソースファイルの読み込みと変数の作成
        # print("2. ソースファイルの読み込みと変数の作成")
        source_content, source_file_name, variables = \
            self.load_source_and_create_variables()

        # 3. プロンプトの読み込みとコード生成
        # print("3. プロンプトの読み込みとコード生成")
        prompt, code = self.load_prompt_and_generate_code(
            create_domain_grimoire, variables)

        # 4. 生成されたコードの処理
        # print("4. 生成されたコードの処理")
        self.process_generated_code(code)

        # 5. 結果の出力
        # 2024-05-22 DY commented out
        # self.output_results()

    def prepare_generation(self, step_n=2):
        """
        ターゲットコード生成の準備を行うメソッド

        Args:
            step_n (int): ステップ番号。デフォルトは2。
        """
        create_domain_grimoire = os.path.join("grimoires",
                                              "architect",
                                              "architect_claude_3_5_sonnet.md")

        splitted = os.path.splitext(os.path.basename(self.target_file_path))
        target_dir = f"generated/{splitted[0]}"

        if step_n == 2:
            self.print_step2_info(create_domain_grimoire, target_dir)

        elif step_n == 3:
            self.print_step3_info(target_dir)

        if self.past_source_file_path is not None:
            # 過去のソースファイルパスが指定されている場合、現在のソースファイルを過去のソースファイルとして保存
            self.save_current_source_as_past()

        return create_domain_grimoire, target_dir

    def print_step2_info(self, create_domain_grimoire, target_dir):
        """
        ステップ2の情報を出力するメソッド
        """
        target_file_path_base = os.path.split(self.target_file_path)[1]

        print(
            f"""
==============================================================
ステップ2. **:green[魔法術式]** を用いて領域術式を実行する
**:violet[領域術式]** : {create_domain_grimoire}
**:violet[実行術式]** : {target_file_path_base}
**:violet[領域対象]** (ディレクトリパス) : {target_dir}
==============================================================
        """
        )

    def print_step3_info(self, target_dir):
        """
        ステップ3の情報を出力するメソッド
        """
        print(
            f"""
==============================================================
ステップ3. **:blue-background[展開術式]** を実行する
:blue-background[展開対象] (ディレクトリパス) : {target_dir}
==============================================================
        """
        )

    def load_source_and_create_variables(self):
        """
        ソースファイルの読み込みと変数の作成を行うメソッド
        """
        source_content = self.read_source_file()
        source_file_name = self.get_source_file_name()
        variables = self.create_variables_dict(source_content,
                                               source_file_name)

        return source_content, source_file_name, variables

    def load_prompt_and_generate_code(self, create_domain_grimoire, variables):
        """
        プロンプトの読み込みとコード生成を行うメソッド
        """
        prompt = self.load_prompt_with_variables(create_domain_grimoire,
                                                 variables)
        # print(prompt)

        code = self.generate_code(prompt)
        # print(code)

        return prompt, code

    def process_generated_code(self, code):
        """
        生成されたコードの処理を行うメソッド
        """
        self.write_code_to_target_file(code)

        if self.source_hash is not None:
            self.append_source_hash_to_target_file()

        if self.target_file_path.endswith(".py"):
            # ターゲットファイルがPythonファイルの場合
            self.try_execute_generated_code(code)
        else:
            # ターゲットファイルがマークダウンファイルの場合
            return code

    def output_results(self):
        """
        結果の出力を行うメソッド
        """
        self.print_target_file_path()
        self.open_target_file_in_vscode()

        # if self.target_file_path.endswith(".py"):
        #     self.run_python_file()

    def print_target_file_path(self):
        """
        ターゲットファイルのパスを出力するメソッド
        """
        print(f"ターゲットファイルのパス: {self.target_file_path}")

    def open_target_file_in_vscode(self):
        """
        ターゲットファイルをVS Codeで開くメソッド
        """
        subprocess.run(["code", self.target_file_path])

    def run_python_file(self):
        """
        Pythonファイルを実行するメソッド
        """
        print(f"Pythonファイルを実行します: {self.target_file_path}")
        subprocess.run([sys.executable, self.target_file_path])

    def save_current_source_as_past(self):
        """
        現在のソースファイルを過去のソースファイルとして保存するメソッド
        """
        shutil.copy(self.source_file_path, self.past_source_file_path)

    def read_source_file(self):
        """
        ソースファイルの内容を読み込むメソッド
        """
        with open(self.source_file_path, "r", encoding="utf-8") as source_file:
            source_content = source_file.read()
        return source_content

    def get_source_file_name(self):
        """
        ソースファイルのファイル名（拡張子なし）を取得するメソッド
        """
        splitted = os.path.splitext(os.path.basename(self.source_file_path))
        source_file_name = splitted[0]

        if source_file_name.startswith("def_"):
            source_file_name = source_file_name[4:]

        return source_file_name

    def create_variables_dict(self, source_content, source_file_name):
        """
        変数の辞書を作成するメソッド
        """
        variables = {
            "source_file_path": self.source_file_path,
            "source_file_name": source_file_name,
            "source_content": source_content,
        }
        return variables

    def load_prompt_with_variables(self, create_domain_grimoire, variables):
        """
        領域術式（要件定義書）からプロンプトを読み込み、変数を埋め込むメソッド
        """
        zoltraak_dir = os.path.dirname(zoltraak.__file__)

        prompt = load_prompt(f"{zoltraak_dir}/{create_domain_grimoire}",
                             variables)

        return prompt

    def generate_code(self, prompt):
        """
        AIを使用してコードを生成するメソッド
        """
        code = call_llm(model=CODE_GEN_LLM,
                        prompt=prompt,
                        temperature=0.0)
        code = code.replace("```python", "").replace("```", "")

        return code

    def write_code_to_target_file(self, code):
        """
        生成されたコードをターゲットファイルに書き込むメソッド
        """
        os.makedirs(os.path.dirname(self.target_file_path), exist_ok=True)
        with open(self.target_file_path, "w", encoding="utf-8") as target_file:
            target_file.write(code)

        print("実行術式のコードを生成しました。")

    def append_source_hash_to_target_file(self):
        """
        ソースファイルのハッシュ値をターゲットファイルに追記するメソッド
        """
        with open(self.target_file_path, "a", encoding="utf-8") as target_file:
            target_file.write(f"\n# HASH: {self.source_hash}\n")
        print(f"ターゲットファイルにハッシュ値を埋め込みました: {self.source_hash}")

    def try_execute_generated_code(self, code):
        """
        生成されたコードを実行するメソッド
        """
        print("領域展開を開始しました。すべてのコードが生成されるまで数分かかります。")

        while True:

            try:
                exec(code)
                break

            except Exception as e:
                print("Pythonファイルの実行中にエラーが発生しました。")
                print(f"**:red[エラーメッセージ]**: {str(e)}")

                msg = "エラーが発生したPythonファイルのパス: "
                msg += f"**:red[{self.target_file_path}]**"
                print(msg)

                while True:

                    prompt = f"""
                    以下のPythonコードにエラーがあります。修正してください。
                    コード: {code}
                    エラーメッセージ: {str(e)}
                    プログラムコードのみ記載してください。
                    """
                    code = call_llm(model=CODE_GEN_LLM,
                                    prompt=prompt,
                                    temperature=0.3)
                    code = code.replace("```python", "").replace("```", "")

                    print("修正したコードを再実行します。")

                    try:
                        exec(code)
                        print("コードの実行が成功しました。")
                        break

                    except Exception as e:
                        print("修正後のコードでもエラーが発生しました。再度修正を試みます。")
                        print(f"**:red[修正後のエラーメッセージ]**: {str(e)}")

                save_as = self.target_file_path
                with open(save_as, "w", encoding="utf-8") as target_file:
                    target_file.write(code)

        print("領域展開が終了しました。")
