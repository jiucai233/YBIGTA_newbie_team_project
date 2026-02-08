# utils/embedding_eda.py
import matplotlib.pyplot as plt

for f in ["AppleGothic", "NanumGothic", "Malgun Gothic"]:
    try:
        plt.rcParams["font.family"] = f
        break
    except Exception:
        pass
plt.rcParams["axes.unicode_minus"] = False

import argparse
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity


def safe_name(path: str) -> str:
    base = Path(path).stem
    base = re.sub(r"[^A-Za-z0-9_\-]+", "_", base)
    return base


def ensure_dir(d: str) -> None:
    os.makedirs(d, exist_ok=True)


def load_tfidf(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # TF-IDF는 숫자여야 함 (혹시 모를 문자열 컬럼 방지)
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0.0)
    return df


def top_terms(df: pd.DataFrame, k: int = 20):
    # 평균 TF-IDF가 큰 단어(전체적으로 중요한 단어)
    mean_tfidf = df.mean(axis=0).sort_values(ascending=False)

    # 문서 등장 비율(0이 아닌 비율)이 큰 단어(자주 나오는 단어)
    doc_freq = (df.gt(0).sum(axis=0) / len(df)).sort_values(ascending=False)

    return mean_tfidf.head(k), doc_freq.head(k)


def plot_bar(series: pd.Series, title: str, out_path: str, xlabel: str):
    plt.figure(figsize=(10, 5))
    series.sort_values(ascending=True).plot(kind="barh")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def pca_scatter(df: pd.DataFrame, title: str, out_path: str, max_rows: int = 2000):
    X = df.to_numpy(dtype=np.float32)

    # 너무 크면 PCA 계산이 무거울 수 있어 샘플링 (지금은 462/633이라 샘플링 필요 없음)
    if X.shape[0] > max_rows:
        idx = np.random.choice(X.shape[0], max_rows, replace=False)
        X = X[idx]

    pca = PCA(n_components=2, random_state=42)
    Z = pca.fit_transform(X)

    plt.figure(figsize=(7, 6))
    plt.scatter(Z[:, 0], Z[:, 1], s=10)
    plt.title(f"{title}\nPCA 2D (explained var: {pca.explained_variance_ratio_.sum():.2f})")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def basic_stats(df: pd.DataFrame) -> dict:
    X = df.to_numpy(dtype=np.float32)
    zeros = (X == 0).sum()
    total = X.size
    sparsity = zeros / total

    row_nnz = (X != 0).sum(axis=1)  # 리뷰당 '의미있는 단어' 개수
    return {
        "n_docs": int(df.shape[0]),
        "n_terms": int(df.shape[1]),
        "sparsity(zeros_ratio)": float(sparsity),
        "avg_nonzero_terms_per_doc": float(row_nnz.mean()),
        "median_nonzero_terms_per_doc": float(np.median(row_nnz)),
    }


def compare_vocab(df_a: pd.DataFrame, df_b: pd.DataFrame) -> dict:
    vocab_a = set(df_a.columns)
    vocab_b = set(df_b.columns)
    inter = vocab_a & vocab_b
    union = vocab_a | vocab_b
    jaccard = len(inter) / len(union) if union else 0.0
    return {
        "vocab_a": len(vocab_a),
        "vocab_b": len(vocab_b),
        "intersection": len(inter),
        "union": len(union),
        "jaccard": float(jaccard),
    }


def compare_term_means(df_a: pd.DataFrame, df_b: pd.DataFrame, k: int = 25) -> pd.DataFrame:
    # 공통 단어에 대해 평균 TF-IDF 비교 (차이가 큰 단어 TOP)
    common = list(set(df_a.columns) & set(df_b.columns))
    if not common:
        return pd.DataFrame()

    a = df_a[common].mean(axis=0)
    b = df_b[common].mean(axis=0)
    out = pd.DataFrame({"mean_tfidf_A": a, "mean_tfidf_B": b})
    out["abs_diff"] = (out["mean_tfidf_A"] - out["mean_tfidf_B"]).abs()
    out = out.sort_values("abs_diff", ascending=False).head(k)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="+", help="TF-IDF embedding csv paths (1개 이상)")
    ap.add_argument("--out_dir", default="review_analysis/plot", help="output image/report directory")
    ap.add_argument("--topk", type=int, default=20, help="top-k terms for plots")
    args = ap.parse_args()

    ensure_dir(args.out_dir)

    # 개별 파일 분석
    summaries = {}
    dfs = {}

    for csv_path in args.csv:
        name = safe_name(csv_path)
        df = load_tfidf(csv_path)
        dfs[name] = df

        stats = basic_stats(df)
        summaries[name] = stats

        mean_top, df_top = top_terms(df, k=args.topk)

        plot_bar(
            mean_top,
            title=f"{name} - Top {args.topk} terms by MEAN TF-IDF",
            out_path=os.path.join(args.out_dir, f"{name}_top_mean_tfidf.png"),
            xlabel="mean tf-idf",
        )
        plot_bar(
            df_top,
            title=f"{name} - Top {args.topk} terms by DOC FREQUENCY",
            out_path=os.path.join(args.out_dir, f"{name}_top_doc_freq.png"),
            xlabel="doc frequency (ratio)",
        )
        pca_scatter(
            df,
            title=f"{name}",
            out_path=os.path.join(args.out_dir, f"{name}_pca_2d.png"),
        )

    # 요약 리포트 저장
    report_path = os.path.join(args.out_dir, "embedding_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=== TF-IDF Embedding EDA Report ===\n\n")
        for name, st in summaries.items():
            f.write(f"[{name}]\n")
            for k, v in st.items():
                f.write(f"  - {k}: {v}\n")
            f.write("\n")

        # 2개 이상이면 비교분석도 추가
        keys = list(dfs.keys())
        if len(keys) >= 2:
            f.write("=== Pairwise Vocabulary Comparison ===\n\n")
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    a, b = keys[i], keys[j]
                    comp = compare_vocab(dfs[a], dfs[b])
                    f.write(f"[{a}] vs [{b}]\n")
                    for k, v in comp.items():
                        f.write(f"  - {k}: {v}\n")

                    diff_df = compare_term_means(dfs[a], dfs[b], k=25)
                    if diff_df.empty:
                        f.write("  - common terms: 0 (no overlap)\n\n")
                    else:
                        f.write("  - top 25 common terms with largest mean tf-idf gap:\n")
                        f.write(diff_df.to_string())
                        f.write("\n\n")

    print(f"[OK] Saved plots + report to: {args.out_dir}")
    print(f"[OK] Report: {report_path}")


if __name__ == "__main__":
    main()
