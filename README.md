# ariyantype
# sample pip package

# 実行方法（fish シェル用）

本プロジェクトは fish シェル 上でも問題なく実行できます。
ただし、fish は bash/zsh と文法が異なるため、以下の手順に従ってください。(bash等の場合お調べ下さい)

# 前提
- OS ： Linux / WSL（Ubuntu）
- シェル ： fish
- Python ： 3.8 以上

# セットアップ（fish）
``` bash
> git clone git@github.com:daddygongon/ariyantype.git
> cd ariyantype
> rm -rf .venv
> python3 -m venv .venv
> source .venv/bin/activate.fish
> python -m pip install -U pip setuptools wheel
> python -m pip install -e .
```
- データのダウンロード: 
src/ariyantype/srcディレクトリがない場合は，こちらの[URL](https://kwanseio365-my.sharepoint.com/:u:/g/personal/ifu81383_nuc_kwansei_ac_jp/IQBSS-jAWP16SJiUxjZMDCxhAYEuir8ryFpKOHtWwhpWoy0?e=MvIeWo)からdata.zipをダウンロードして，mvしてください．

# 実行方法（fish）
``` bash
> source .venv/bin/activate.fish
> ariyantype
> ariyantype -h
```
# 各機能の実行例
- STEP 練習（例：STEP-1）
    > ariyantype 1
- 練習履歴を表示
    > ariyantype -r
- STEP 練習履歴（一覧）
    > ariyantype -H
- グラフ生成（スピード）
    > ariyantype --plot-speed
- グラフ生成（トレーニングスコア）
    > ariyantype --plot-score
- データ展開（fish）
    > ariyantype -d path/to/data.zip
- グラフ表示
    > explorer.exe (wslpath -w ~/.local/share/ariyantype/plots)

直接ファイルを実行しない
- 必ず：
    > ariyantype
- または：
    > python -m ariyantype.typing_main

# 動作確認（fish）
> python -c 'import sys; print(sys.executable)'
> which ariyantype
