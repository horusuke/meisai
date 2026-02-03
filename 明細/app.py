import streamlit as st
import pandas as pd

# 伝票データ処理関数
def denpyou(df):
    df = df.drop(
        columns=[
            'バリエーション',
            '価格',
            '税率',
            '数量',
            '合計金額',
            '送料',
            '支払い方法',
            '代引き手数料',
            '発送状況',
            '商品ID',
            '種類ID',
            '購入元',
            '配送日',
            '配送時間帯',
            '注文メモ',
            '調整金額',
            '商品コード',
            '種類コード',
            'JAN / GTIN',
            '都道府県(請求先)',
            '住所(請求先)',
            '住所2(請求先)',
            '電話番号(請求先)',
            'メールアドレス(請求先)',
            '郵便番号(請求先)',
            '注文ID',
        ],
        errors='ignore'
    )

    df['氏名(配送先)'] = df['氏(配送先)'] + ' ' + df['名(配送先)']
    df = df.drop(columns=['氏(請求先)', '名(請求先)', '氏(配送先)', '名(配送先)'], errors='ignore')
    df['郵便番号(配送先)'] = (
        df['郵便番号(配送先)']
        .astype(str)
        .str.replace('.0', '', regex=False)
        .str.zfill(7))
    df['敬称'] = '様'
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('郵便番号(配送先)')))
    df = df[cols]
    ordered_cols = [
        '郵便番号(配送先)',
        '氏名(配送先)',
        '敬称',
        '都道府県(配送先)',
        '住所(配送先)',
        '住所2(配送先)',
        '住所3(配送先)',
        '商品名']

    df = df[[c for c in ordered_cols if c in df.columns]]
    df.insert(
        df.columns.get_loc('商品名'),
        '',
        '')

    return df

# ページ設定
st.set_page_config(
    page_title="CSV データ分析アプリ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# タイトル
st.title("📊 CSV 伝票変換")
st.markdown("---")

# ファイルアップロード
st.subheader("📁 CSVファイルをアップロード")
uploaded_file = st.file_uploader(
    "CSVファイルをドラッグ&ドロップするか、クリックして選択してください",
    type=['csv'],
    help="Shift_JISエンコーディングのCSVファイルに対応しています"
)

# ファイル名生成関数
def generate_processed_filename(original_filename):
    """元のファイル名に「加工済み」を追加したファイル名を生成"""
    import os
    if not original_filename:
        return "processed_data.csv"
    
    # 拡張子を分離
    name, ext = os.path.splitext(original_filename)
    # 「加工済み」を追加
    processed_name = name + "加工済み" + ext
    return processed_name

# データフレームをセッションステートに保存
if 'df' not in st.session_state:
    st.session_state.df = None
if 'df_original' not in st.session_state:
    st.session_state.df_original = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "処理後（伝票形式）"
if 'duplicate_info' not in st.session_state:
    st.session_state.duplicate_info = None
if 'original_filename' not in st.session_state:
    st.session_state.original_filename = None

# ファイルがアップロードされた場合
if uploaded_file is not None:
    try:
        # CSVファイルを読み込み（Shift_JISエンコーディング）
        df = pd.read_csv(uploaded_file, encoding='shift_jis')
        st.session_state.df_original = df.copy()
        # 元のファイル名を保存
        st.session_state.original_filename = uploaded_file.name
        
        # 注文番号の重複チェック
        order_id_columns = ['注文ID', '注文番号', '注文No', 'Order ID', 'order_id']
        order_id_col = None
        for col in order_id_columns:
            if col in df.columns:
                order_id_col = col
                break
        
        duplicate_warning = None
        if order_id_col:
            # 重複している注文IDを検出
            duplicates = df[df.duplicated(subset=[order_id_col], keep=False)]
            if len(duplicates) > 0:
                duplicate_order_ids = duplicates[order_id_col].value_counts()
                duplicate_count = len(duplicate_order_ids)
                total_duplicate_rows = len(duplicates)
                st.session_state.duplicate_info = {
                    'column': order_id_col,
                    'duplicate_order_ids': duplicate_order_ids,
                    'duplicate_count': duplicate_count,
                    'total_duplicate_rows': total_duplicate_rows
                }
            else:
                st.session_state.duplicate_info = None
        else:
            st.session_state.duplicate_info = None
        
        # デフォルトでdenpyou関数を適用
        df = denpyou(df)
        st.session_state.df = df
        
        st.success(f"✅ ファイル '{uploaded_file.name}' を正常に読み込み、伝票処理を適用しました！")
        
        # 注文番号の重複警告を表示
        if st.session_state.duplicate_info:
            dup_info = st.session_state.duplicate_info
            st.warning(
                f"⚠️ **重複する注文番号が検出されました！**\n\n"
                f"- 重複している注文番号の種類: {dup_info['duplicate_count']}件\n"
                f"- 重複を含む行数: {dup_info['total_duplicate_rows']}行\n"
                f"- 列名: {dup_info['column']}"
            )
            with st.expander("🔍 重複している注文番号の詳細", expanded=False):
                st.dataframe(
                    dup_info['duplicate_order_ids'].to_frame('出現回数'),
                    use_container_width=True
                )
                st.caption(f"※ 注文番号ごとの出現回数を表示しています（2回以上が重複）")
        
        # ファイル情報を表示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("行数", f"{len(df):,}")
        with col2:
            st.metric("列数", len(df.columns))
        with col3:
            st.metric("ファイル名", uploaded_file.name)
        
    except Exception as e:
        st.error(f"❌ エラーが発生しました: {str(e)}")
        st.info("💡 ヒント: ファイルがShift_JISエンコーディングであることを確認してください。")
        import traceback
        with st.expander("エラー詳細"):
            st.code(traceback.format_exc())

# サイドバーでの設定
with st.sidebar:
    st.header("⚙️ 設定")
    
    # データ表示モード選択（両方表示に変更したため、このセクションは削除または非表示に）
    # 両方表示するため、表示モード選択は不要
    
    # データ操作
    if st.session_state.df is not None:
        st.subheader("🔧 データ操作")
        if st.button("データをリセット"):
            st.session_state.df = None
            st.session_state.df_original = None
            st.session_state.view_mode = "処理後（伝票形式）"
            st.session_state.original_filename = None
            st.rerun()
    
    # エンコーディング選択（再読み込み用）
    st.subheader("📝 ファイル設定")
    encoding_option = st.selectbox(
        "エンコーディング",
        ["shift_jis", "utf-8", "cp932"],
        help="ファイルの読み込みに使用するエンコーディング"
    )

# データ表示
if st.session_state.df is not None:
    st.markdown("---")
    
    # 処理前と処理後のデータを両方表示
    if st.session_state.df_original is not None:
        # 2カラムレイアウトで表示
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 処理前データ（元のデータ）")
            st.dataframe(st.session_state.df_original, use_container_width=True)
            
            with st.expander("📊 処理前データの基本情報"):
                st.write("**データ型:**")
                st.dataframe(st.session_state.df_original.dtypes.to_frame('データ型'))
                
                st.write("**欠損値:**")
                missing_data_original = st.session_state.df_original.isnull().sum()
                if missing_data_original.sum() > 0:
                    st.dataframe(missing_data_original[missing_data_original > 0].to_frame('欠損数'))
                else:
                    st.info("欠損値はありません")
                
                st.write("**統計情報:**")
                st.dataframe(st.session_state.df_original.describe())
        
        with col2:
            st.subheader("📋 処理後データ（伝票形式）")
            st.caption("💡 データを直接編集できます。セルをクリックして編集してください。")
            
            # 編集可能なデータフレーム
            edited_df = st.data_editor(
                st.session_state.df,
                use_container_width=True,
                num_rows="dynamic",
                key="processed_data_editor"
            )
            
            # データが編集された場合、セッションステートを更新
            if not edited_df.equals(st.session_state.df):
                st.session_state.df = edited_df
                st.info("✅ データが更新されました")
            
            with st.expander("📊 処理後データの基本情報"):
                st.write("**データ型:**")
                st.dataframe(edited_df.dtypes.to_frame('データ型'))
                
                st.write("**欠損値:**")
                missing_data_processed = edited_df.isnull().sum()
                if missing_data_processed.sum() > 0:
                    st.dataframe(missing_data_processed[missing_data_processed > 0].to_frame('欠損数'))
                else:
                    st.info("欠損値はありません")
                
                st.write("**統計情報:**")
                st.dataframe(edited_df.describe())
    else:
        # 元のデータがない場合（通常は発生しないが、念のため）
        st.subheader("📋 処理後データプレビュー（伝票形式）")
        st.caption("💡 データを直接編集できます。セルをクリックして編集してください。")
        
        # 編集可能なデータフレーム
        edited_df = st.data_editor(
            st.session_state.df,
            use_container_width=True,
            num_rows="dynamic",
            key="processed_data_editor_single"
        )
        
        # データが編集された場合、セッションステートを更新
        if not edited_df.equals(st.session_state.df):
            st.session_state.df = edited_df
            st.info("✅ データが更新されました")
        
        with st.expander("📊 データの基本情報"):
            st.write("**データ型:**")
            st.dataframe(edited_df.dtypes.to_frame('データ型'))
            
            st.write("**欠損値:**")
            missing_data = edited_df.isnull().sum()
            if missing_data.sum() > 0:
                st.dataframe(missing_data[missing_data > 0].to_frame('欠損数'))
            else:
                st.info("欠損値はありません")
            
            st.write("**統計情報:**")
            st.dataframe(edited_df.describe())
    
    # CSVダウンロードボタン
    st.markdown("---")
    st.subheader("💾 データのエクスポート")
    
    st.write("ブラウザから直接ダウンロードします（保存先はブラウザの設定に従います）")
    
    # ファイル名のカスタマイズ（元のファイル名に「加工済み」を追加）
    if st.session_state.original_filename:
        default_filename = generate_processed_filename(st.session_state.original_filename)
    else:
        default_filename = "processed_data.csv"
    
    custom_filename = st.text_input(
        "ファイル名を指定",
        value=default_filename,
        help="ダウンロードするファイル名を指定してください（.csvを含めてください）"
    )
    
    # ファイル名の検証
    if custom_filename and not custom_filename.endswith('.csv'):
        st.warning("⚠️ ファイル名は .csv で終わる必要があります")
        custom_filename = default_filename
    
    csv = st.session_state.df.to_csv(index=False, encoding='shift_jis')
    st.download_button(
        label="📥 CSVファイルとしてダウンロード（処理後データ）",
        data=csv,
        file_name=custom_filename if custom_filename else default_filename,
        mime="text/csv",
        help="処理後のデータをCSVファイルとしてダウンロードします"
    )
