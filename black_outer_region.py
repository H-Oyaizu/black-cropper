#!/usr/bin/env python3
"""指定フォルダ内の画像について、指定割合の外側領域を黒塗りして保存するスクリプト。"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from PIL import Image


対応拡張子 = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def 画像ファイル一覧(入力フォルダ: Path) -> Iterable[Path]:
    """入力フォルダ配下の対応画像ファイルを列挙する。"""
    for パス in sorted(入力フォルダ.rglob("*")):
        if パス.is_file() and パス.suffix.lower() in 対応拡張子:
            yield パス


def 外側領域を黒塗り(画像: Image.Image, 外側割合: float) -> Image.Image:
    """指定割合の外側領域を黒塗りし、処理後画像を返す。"""
    if not 0 <= 外側割合 < 50:
        raise ValueError("割合は0以上50未満で指定してください。")

    幅, 高さ = 画像.size
    左余白 = int(幅 * (外側割合 / 100))
    右余白 = 左余白
    上余白 = int(高さ * (外側割合 / 100))
    下余白 = 上余白

    出力画像 = 画像.copy()

    # 画像配列へ直接アクセスして高速に塗りつぶす
    ピクセル = 出力画像.load()

    for y in range(高さ):
        for x in range(幅):
            if x < 左余白 or x >= 幅 - 右余白 or y < 上余白 or y >= 高さ - 下余白:
                if 出力画像.mode in ("RGB", "RGBA"):
                    ピクセル[x, y] = (0, 0, 0, 255) if 出力画像.mode == "RGBA" else (0, 0, 0)
                elif 出力画像.mode in ("L", "P"):
                    ピクセル[x, y] = 0
                else:
                    # 未知のモードはRGBへ変換して再帰処理する
                    return 外側領域を黒塗り(出力画像.convert("RGB"), 外側割合)

    return 出力画像


def 画像群を処理(入力フォルダ: Path, 出力フォルダ: Path, 外側割合: float) -> None:
    """入力フォルダ内すべての画像を処理し、出力フォルダへ保存する。"""
    if not 入力フォルダ.exists() or not 入力フォルダ.is_dir():
        raise FileNotFoundError(f"入力フォルダが見つかりません: {入力フォルダ}")

    出力フォルダ.mkdir(parents=True, exist_ok=True)

    対象画像 = list(画像ファイル一覧(入力フォルダ))
    if not 対象画像:
        print("対象となる画像ファイルが見つかりませんでした。")
        return

    for 入力画像パス in 対象画像:
        相対パス = 入力画像パス.relative_to(入力フォルダ)
        出力画像パス = 出力フォルダ / 相対パス
        出力画像パス.parent.mkdir(parents=True, exist_ok=True)

        with Image.open(入力画像パス) as 画像:
            処理後 = 外側領域を黒塗り(画像, 外側割合)
            処理後.save(出力画像パス)

        print(f"処理完了: {入力画像パス} -> {出力画像パス}")

    print(f"全処理完了: {len(対象画像)} 枚")


def 引数解析() -> argparse.Namespace:
    """コマンドライン引数を解析する。"""
    parser = argparse.ArgumentParser(
        description="src内画像の外側領域を黒塗りしてtgtへ保存します。"
    )
    parser.add_argument("--src", type=Path, default=Path("src"), help="入力フォルダ (既定: src)")
    parser.add_argument("--tgt", type=Path, default=Path("tgt"), help="出力フォルダ (既定: tgt)")
    parser.add_argument(
        "--percent",
        type=float,
        required=True,
        help="外側から黒塗りする割合(%%)。例: 10 を指定すると各辺10%%を黒塗り",
    )
    return parser.parse_args()


def main() -> None:
    """エントリーポイント。"""
    args = 引数解析()
    画像群を処理(args.src, args.tgt, args.percent)


if __name__ == "__main__":
    main()
