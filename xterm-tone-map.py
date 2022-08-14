import colorsys
import csv
import sys


def main():
    pccs_dict = load_pccs()

    xterm256_dict = load_xterm256()

    pair_pccs_xterm256_dict = pair_pccs_xterm256(pccs_dict, xterm256_dict)

    print_sorted_xterm256(xterm256_dict)
    print_pair_pccs_xterm256(pccs_dict, xterm256_dict, pair_pccs_xterm256_dict)
    print_tone_map_html(pccs_dict, xterm256_dict, pair_pccs_xterm256_dict)

def load_pccs():
    '''
    PCCSデータ読み込み
    # トーン名 => RGB (と変換したHSV)のペアを作る
    '''
    pccs_dict = {}
    file = "data/pccs.csv"
    with open(file) as f:
        # Drop header
        f.readline()
        header_no = 0
        header_name = 1
        header_rgb = 2
        # Read csv
        reader = csv.reader(f)
        for row in reader:
            name = row[header_name]
            rgb = row[header_rgb]
            if len(rgb) != 7:
                raise ValueError(f"Not RGB code [{rgb}]")
            r = int(rgb[1:3], 16) / 255
            g = int(rgb[3:5], 16) / 255
            b = int(rgb[5:7], 16) / 255 
            (h, s, v) = colorsys.rgb_to_hsv(r, g, b)
            # Construct
            pccs_dict[name] = { "rgb": rgb, "h": h, "s": s, "v": v }
    return pccs_dict


def load_xterm256():
    '''
    XTERM-256データを読み込み
    # 番号と名前 => RGB (と変換したHSV)のペアを作る
    '''
    xterm256_dict = {}
    file = "data/xterm256.csv"
    with open(file) as f:
        # Drop header
        f.readline()
        header_no = 0
        header_name = 1
        header_rgb = 2
        # Read csv
        reader = csv.reader(f)
        for row in reader:
            no = row[header_no]
            if int(no) < 16:
                continue
            name = row[header_name]
            rgb = row[header_rgb]
            if len(rgb) != 7:
                raise ValueError(f"Not RGB code [{rgb}] in {file}")
            r = int(rgb[1:3], 16) / 255
            g = int(rgb[3:5], 16) / 255
            b = int(rgb[5:7], 16) / 255
            (h, s, v) = colorsys.rgb_to_hsv(r, g, b)
            # Construct
            xterm256_dict[no] = { "name": name, "rgb": rgb, "h": h, "s": s, "v": v }
    return xterm256_dict


def pair_pccs_xterm256(pccs_dict, xterm256_dict):
    '''
    PCCSとXTERM-256のHSV近似ペアを作る
    # PCCS => XTERM-256
    '''
    pair_pccs_xterm256_dict = { k: [] for k in pccs_dict.keys() }
    # Choose the closest one out of almost the same hue
    for xterm256_no, xterm256 in xterm256_dict.items():
        for pccs_name, pccs in pccs_dict.items():
            diff_h = (xterm256["h"] - pccs["h"])
            # hue is circle
            if diff_h < -300:
                diff_h += 360
            elif 300 < diff_h:
                diff_h -= 360
            diff_h *= 360 / 100
            diff_s = xterm256["s"] - pccs["s"]
            diff_v = xterm256["v"] - pccs["v"]
            # Negative numbers are preferred
            positive_rate = 1.4
            if 0 < diff_h:
                diff_h *= positive_rate
            if 0 < diff_s:
                diff_s *= positive_rate
            if 0 < diff_v:
                diff_v *= positive_rate
            diff_sq = diff_h * diff_h + diff_s * diff_s + diff_v * diff_v
            if diff_sq < 0.7:
                insert_index = bisect_left_with_key(pair_pccs_xterm256_dict[pccs_name], diff_sq, key=lambda v: v[1], offset=0, length=len(pair_pccs_xterm256_dict[pccs_name]))
                pair_pccs_xterm256_dict[pccs_name].insert(insert_index, (xterm256_no, diff_sq))
                if 8 <= len(pair_pccs_xterm256_dict[pccs_name]):
                    del pair_pccs_xterm256_dict[pccs_name][7]
    return pair_pccs_xterm256_dict


def print_sorted_xterm256(xterm256_dict):
    xterm256_sorted = sorted(sorted(sorted(xterm256_dict.items(), key=lambda kvp: kvp[1]["v"]), key=lambda kvp: kvp[1]["h"]), key=lambda kvp: kvp[1]["s"])
    print("\n# XTERM 256 colors\n")
    for kvp in xterm256_sorted:
        xterm256_no = kvp[0]
        xterm256_name = kvp[1]["name"]
        xterm256_rgb = kvp[1]["rgb"]
        xterm256_h = round(kvp[1]["h"] * 360)
        xterm256_s = round(kvp[1]["s"] * 100)
        xterm256_v = round(kvp[1]["v"] * 100)
        print(f"{xterm256_rgb}, H={xterm256_h:3}, S={xterm256_s:3}, V={xterm256_v:3} : No={xterm256_no:3}, Name={xterm256_name}")


def print_pair_pccs_xterm256(pccs_dict, xterm256_dict, pair_pccs_xterm256_dict):
    print("\n# PCCS pair")
    # python 3.7以降でdictの挿入順が保証されている想定
    for pccs_name in pccs_dict.keys():
        pccs : dict = pccs_dict[pccs_name]
        pccs_rgb = pccs["rgb"]
        pccs_h = round(pccs["h"] * 360)
        pccs_s = round(pccs["s"] * 100)
        pccs_v = round(pccs["v"] * 100)
        print(f"{pccs_name:6}: {pccs_rgb}, H={pccs_h:3}, S={pccs_s:3}, V={pccs_v:3}")
        # lower_diff = None
        for t in pair_pccs_xterm256_dict[pccs_name]:
            xterm256_pccs_diff = t[1]
            # if lower_diff:
            #     if lower_diff * 2 < xterm256_pccs_diff:
            #         break
            # else:
            #     lower_diff = xterm256_pccs_diff
            xterm256_no = t[0]
            xterm256 = xterm256_dict[xterm256_no]
            xterm256_name = xterm256["name"]
            xterm256_rgb = xterm256["rgb"]
            xterm256_h = round(xterm256["h"] * 360)
            xterm256_s = round(xterm256["s"] * 100)
            xterm256_v = round(xterm256["v"] * 100)
            print(f"          {xterm256_rgb}, H={xterm256_h:3}, S={xterm256_s:3}, V={xterm256_v:3} : No={xterm256_no:3}, Name={xterm256_name} : Diff={xterm256_pccs_diff:.3}")


def print_tone_map_html(pccs_dict, xterm256_dict, pair_pccs_xterm256_dict):
    # Keys are names without numbers and minus
    tone_image = {
        "v": "Vivid [ さえた, 鮮やかな, 派手な, 目だつ ]",
        "b": "Bright [ 明るい, 健康的な, 陽気な ]",
        "s": "Strong [ 強い, くどい, 動的な ]",
        "dp": "Deep [ 濃い, 深い, 充実した, 伝統的な, 和風の ]",
        "lt+": "Light (high saturation) [ 浅い, 澄んだ, 子供っぽい, さわやかな ]",
        "lt": "Light [ 浅い, 澄んだ, 子供っぽい, さわやかな ]",
        "sf": "Soft [ 柔らかな, おだやかな, ぼんやりした ]",
        "d": "Dull [ にぶい, くすんだ, 中間色的 ]",
        "dk": "Dark [ 暗い, 大人っぽい, 丈夫な, 円熟した ]",
        "p+": "Pale (high saturation)  [ 薄い, 軽い, あっさりした, 弱い, 女性的, 若々しい, やさしい, 淡い, かわいい ]",
        "p": "Pale [ 薄い, 軽い, あっさりした, 弱い, 女性的, 若々しい, やさしい, 淡い, かわいい ]",
        "ltg": "Light Grayish [ 明るい灰みの, 落ち着いた, 渋い, おとなしい ]",
        "g": "Grayish [ 灰みの, 濁った, 地味な ]",
        "dkg": "Dark Grayish [ 暗い灰みの, 陰気な, 重い, 固い, 男性的 ]",
        "W": "White [ 清潔な, 冷たい, 新鮮な ]",
        "Gy": "Gray [ スモーキーな, しゃれた, 寂しい ]",
        "Bk": "Black [ 高級な, フォーマルな, シックな, おしゃれな, 締まった ]"
    }

    print('\n<html lang="ja"><head><meta charset="utf-8"></head><body><h1>Tone table</h1>')
    print("<table style='color:#ffffff;background-color:#000000'>")
    # python 3.7以降でdictの挿入順が保証されている想定
    current_pccs = ""
    current_xterm256 =  ""
    current_group = ""
    for pccs_name in pccs_dict.keys():
        # print group tone image
        group = pccs_name.translate(str.maketrans("","","-.0123456789"))
        if group != current_group:
            if current_pccs:
                print(f"<tr>{current_pccs}</tr>")
            if current_xterm256:
                print(f"<tr>{current_xterm256}</tr>")
            current_pccs = ""
            current_xterm256 = ""
            current_group = group
            if not group in tone_image:
                raise IndexError(f"{pccs_name} does not exists in tone image")
            print(f"<tr><td colspan=24>{tone_image[group]}</td></tr>")
        pccs : dict = pccs_dict[pccs_name]
        pccs_rgb = pccs["rgb"]
        pccs_h = round(pccs["h"] * 360)
        pccs_s = round(pccs["s"] * 100)
        pccs_v = round(pccs["v"] * 100)
        pccs_fg = "#000000" if pccs_s - pccs_v < 0 else "#ffffff"
        current_pccs = f"{current_pccs}<td style='color:{pccs_fg};background-color:{pccs_rgb}'>{pccs_name}</td>"
        for t in pair_pccs_xterm256_dict[pccs_name]:
            xterm256_pccs_diff = t[1]
            xterm256_no = t[0]
            xterm256 = xterm256_dict[xterm256_no]
            xterm256_name = xterm256["name"]
            xterm256_rgb = xterm256["rgb"]
            xterm256_h = round(xterm256["h"] * 360)
            xterm256_s = round(xterm256["s"] * 100)
            xterm256_v = round(xterm256["v"] * 100)
            xterm256_fg = "#000000" if xterm256_s - xterm256_v < 0 else "#ffffff"
            current_xterm256 = f"{current_xterm256}<td style='color:{xterm256_fg};background-color:{xterm256_rgb}'>{xterm256_no}</td>"
            break
    if current_pccs:
        print(f"<tr>{current_pccs}</tr>")
    if current_xterm256:
        print(f"<tr>{current_xterm256}</tr>")
    print("</table>")
    print("</body></html>")


def bisect_left_with_key(sorted_list, value, key, offset, length):
    '''
    pythonが古くて"key is an invalid keyword argument for bisect_left()"エラーが出るので自作
    '''
    if length <= 8:
        for i,v in enumerate(sorted_list[offset:]):
            if value <= key(v):
                return offset+i
        return offset + length

    center = offset + int(length / 2)
    if key(sorted_list[center]) < value:
        if center < offset + length:
            return bisect_left_with_key(sorted_list, value, key, center, length - center - offset)
        else:
            return offset
    else:
        if offset < center:
            return bisect_left_with_key(sorted_list, value, key, offset, length - center)
        else:
            return offset


if __name__ == "__main__":
    main()
