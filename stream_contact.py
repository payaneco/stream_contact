import streamlit as st
from abc import ABC, abstractmethod
import pandas as pd

#現在のバージョン
CURRENT_VERSION = "0"

#最初にページコンフィグしないとエラーになるので注意
st.set_page_config(page_title="走行ポリシー趣意書", page_icon="🚲", layout="wide")

class Widget(ABC):
    @abstractmethod
    def view(self, r) -> str:
        pass
    
    @abstractmethod
    def edit(self):
        pass
    
class Radio(Widget):
    def __init__(self, label, l, help=None, horizontal=True):
        self.label = label
        dic = dict((i, v) for i, v in enumerate(l))
        dic[len(l)] = "非表示"
        self.options = dic
        self.help = help
        self.horizontal = horizontal

    def format_func(self, key):
        return self.options[key]
    
    def view(self, r) -> str:
        return self.options[int(r)]

    def edit(self):
        self.value = st.radio(self.label, self.options, index=len(self.options) - 1, help=self.help, format_func=self.format_func, horizontal=self.horizontal)

def getWidgets():
    questions = [
        #Radio("巡航速度目安(平坦無風時)", ("～18km/h", "～21km/h", "～25km/h", "～32km/h", "～40km/h", "40km/h～")),
        #Radio("ダウンヒル速度目安", ("～20km/h", "～30km/h", "～45km/h", "～60km/h", "60km/h～")),
        Radio("雨天走行", ("しない", "少雨可", "豪雨上等")),
        Radio("手信号(グループライド)", ("なし", "たまに", "わりと", "できるだけ")),
        Radio("手信号(ソロライド)", ("なし", "たまに", "わりと", "できるだけ")),
        Radio("走行注意の声掛け(グループライド)", ("なし", "たまに", "わりと", "できるだけ"), help="峠での「くるまー」「たいこー」などの声掛けです"),
        
        Radio("前照灯(昼間、平地)", ("点灯", "点滅", "つけない")),
        Radio("前照灯(昼間、ヒルクライム)", ("点灯", "点滅", "つけない")),        Radio("前照灯(雨天/夕方)", ("点灯", "点滅", "つけない")),
        Radio("尾灯(昼間、平地)", ("点灯", "点滅", "つけない")),
        Radio("尾灯(昼間、ヒルクライム)", ("点灯", "点滅", "つけない")),
        Radio("尾灯(雨天/夕方)", ("点灯", "点滅", "つけない")),
       
        Radio("赤信号待ち車両追い抜き", ("しない", "数台ならしない", "する", "歩道に上がる"), help="なお交番前ではなくパトカーはいない状況とします"),
        Radio("渋滞徐行時の車両追い抜き", ("しない", "する", "歩道に上がる"), help="車が渋滞で10km/h程度の速度で走行しているものとします"),
        Radio("自転車横断帯", ("横断帯の上を走る", "車道を真っすぐ走る")),
        Radio("一時停止線", ("止まって左右確認する", "足をつく", "徐行する", "普通に走る")),
        Radio("踏切停止線", ("止まって左右確認する", "足をつく", "徐行する", "普通に走る")),
        
        Radio("歩車分離式信号", ("車信号利用", "歩行者信号利用", "青い方を利用"), help="「歩行者自転車専用」の標識はないものとします"),
        Radio("赤信号(歩行者自転車専用)", ("自転車信号に従う", "自動車信号に従う"), help="自動車信号が青で歩行者自転車専用信号が赤の状態です。分離式ではありません"),
        Radio("赤信号(歩行者)", ("歩行者信号に従う", "自動車信号に従う"), help="自動車信号が青で歩行者信号が赤の状態です。分離式ではありません"),
        Radio("赤信号(左折時)", ("停止する", "歩道に上がって赤信号左折する", "車道のまま赤信号左折する"), horizontal=False),
        Radio("信号右折(右折車線有)", ("二段階右折遵守", "二段階(手前横断帯右折可)", "一段階右折"), help="「手前横断帯」とは赤信号侵入前の横断歩道を先に渡っておく時間短縮法です"),
        Radio("T字路右折(右折車線無)", ("二段階右折遵守", "二段階(手前横断帯右折可)", "一段階右折"), help="T字路の下方向(直進できない向き)から侵入した時の右折を想定しています"),
        Radio("信号直進(左折レーン＋境界ブロック有)", ("常に直進レーン走行", "ブロック前で直進レーンに車線変更", "左折レーンから横断歩道利用"), horizontal=False),
        Radio("車道逆走", ("しない", "数メートルなら", "気にしない")),
        Radio("並進走行", ("しない", "前後に車がいなければ", "気にしない")),
        Radio("橋(矢羽根マーク有)", ("車道走行優先", "歩道走行優先")),
        Radio("橋(矢羽根マーク無、道幅狭し)", ("車道走行優先", "歩道走行優先")),
        Radio("トンネル", ("車道走行優先", "歩道走行優先")),
        Radio("上り坂の蛇行/はみ出し運転", ("しない", "内側がエグいカーブですることもある", "激坂ですることもある"), horizontal=False),
        Radio("自転車専用道路", ("専用道を通行", "車道通行", "歩道通行"), help="歩道と車道の間に自転車専用の道路が縁石で独立している道です"),
        Radio("歩行者を抜けない時", ("何もせず減速する", "声掛けする", "ラチェット音とかで存在アピールする", "ベルを鳴らす"), horizontal=False),
        
        Radio("走行中片手スマホ撮影", ("しない", "たまにする", "よくする")),
        Radio("走行中固定スマホ操作", ("固定しない", "操作しない", "たまにする", "よくする"), help="スマホホルダーでハンドルに固定してあるものとします"),
        Radio("走行中サイコン操作", ("使用しない", "操作しない", "たまにする", "よくする")),
        Radio("走行中喫飲", ("しない", "停止時のみする", "する")),
        Radio("走行中喫食", ("しない", "停止時のみする", "する")),
        Radio("マスク着用", ("飲食時を除き常時する", "走行時は外す", "しない", "状況による")),
        Radio("スピーカー/ネックスピーカー利用", ("しない", "する時がある")),
        Radio("骨伝導イヤホン利用", ("しない", "する時がある")),
        Radio("片耳イヤホン利用", ("しない", "する時がある")),
        Radio("走行中の肉声会話", ("推奨", "可", "不可")),
        Radio("走行中のスピーカー/イヤホン会話", ("推奨", "可", "不可")),
        Radio("頭から液体ぶっかけ", ("しない", "水ならする", "お茶でもする", "スポドリでもする")),
    ]
    return questions

def set_params():
    st.experimental_set_query_params(
        v = CURRENT_VERSION,
        r = "".join([str(w.value) for w in widgets])
    )

def go_top():
    st.experimental_set_query_params()

def show_views(widgets, res):
    st.markdown("""
このページは過度に細分化した自転車走行ポリシーに見せかけた**ダミー回答**を作成するページです。  
ダミー回答は実走行と関係ありません。  
法律を遵守し、安全第一で無理なく、気遣いのできる運転をしましょう。
""")
    #hc, vc = st.columns(2)
    l = []
    for i, r in enumerate(res):
        w = widgets[i]
        v = w.view(r)
        if v == "非表示":
            continue
        l.append({"質問": w.label, "ダミー回答": v})
        _ = """
        with hc:
            st.write(f"**{w.label}**")
        with vc:
            st.text(v)
        """
    df = pd.DataFrame(l, columns=["質問", "ダミー回答"])
    st.table(df)
    st.button("トップページに戻る", on_click=go_top)

def show_edits(widgets):
    st.markdown("""
このページは過度に細分化した自転車走行ポリシーに見せかけた**ダミー回答**を作成するページです。  
各項目を選択して『リスト表示』ボタンを押すと、『非表示』以外の項目を一覧表示するURLに移動します。  
ダミー回答とは関係なく法律を遵守しましょう。  
  
また、体調や道路状況に応じて最適な行動は変化します。  
もし本当にポリシーがあったとしても、安全第一で無理なく、気遣いのできる運転をしましょう。
""")
    st.subheader("質問とダミー回答")
    for w in widgets:
        w.edit()
    st.markdown("""
**免責および利用規約**

+ このページには道路交通法に即さない記述が含まれますが、法律違反や危険運転を助長する意図は一切ありません。それを理解した上でご利用の上、法律を守って安全運転してください
+ このページは断りなくバージョンアップや公開停止する場合があります。バージョンアップに伴い、過去の回答が無効になることを理解したうえでご利用ください
+ このページを誹謗中傷や悪意のある表現のために利用することを禁じます
+ このページを利用、転載することで直接・間接的に生じた被害、損失に関し、制作者は一切責任を負いません
""")
    agree = st.checkbox("上記内容に同意しました。")
    if agree:
        st.button("リスト表示", on_click=set_params)

def main(widgets):
    st.title("自転車走行ポリシー趣意書")
    # バージョン確認
    if ("v" in params.keys()):
        if params["v"][0] == CURRENT_VERSION: # パラメータ1個でも配列が帰ってくる[0]
            if "r" in params.keys():
                show_views(widgets, params["r"][0])
                return
        else:
            # 最新バージョンと異なる
            st.error("最新版と異なるバージョンが指定されました。<br/>リスト表示することができません。")

    show_edits(widgets)

params = st.experimental_get_query_params()
widgets = getWidgets()
main(widgets)
