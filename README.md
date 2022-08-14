# Xterm tone map

[PCCS][pccs]と[Xterm 256色][xterm256]の対応表です。
ターミナル環境の設定でいい感じの色使いにしたくて作成しました。

[pccs]:https://www.dic-color.com/knowledge/pccs.html
[xterm256]:https://www.ditig.com/256-colors-cheat-sheet

`xterm-tone-map.py`を使って`pccs.csv`と`xterm256.csv`をもとにHSVに変換し、似た色を割り出しています。

```sh
python3 xterm-tone-map.py > out/xterm-tone-map.txt
```

出力した`xterm-tone-map.txt`をVSCodeの`Color Highlight`拡張機能を使ってみると近い色が確認できます。
一番近い色を抜き出したものがhtmlになってるので[xterm-tone-map.html](https://arkbig.github.io/color-coordinate/out/xterm-tone-map.html)ファイルとして保存するとブラウザで確認できます。

## 注意

色の知識はまだないので、似た色の検出アルゴリズムの精度は低いです。

また個人用なので0〜15はターミナルアプリ側で変更することを考えて除外しています。
実際私は黒背景だと青色が見えづらいので紫色に変更しています。

## License

This repository's license is [zlib](./LICENSE). Please feel free to use this, but no warranty.
(Except *.csv data)

*.csvデータは除いて、自由にご利用ください。（無保証です）
