import warnings
from typing import Tuple, List, Optional

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import diffprivlib
import diffprivlib.models as dp_models

from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


class DPKet:
    """
    Toolkit for Differential Privacy experiments.
    Unified interface for Statistical Analysis and Machine Learning.
    """

    def __init__(self, data_path: str):
        """
        Loads the dataset and performs initial cleaning.
        """
        self.raw_df = pd.read_csv(data_path)

        # Pre-clean data: Drop missing Age values (critical for both Stats and ML)
        self.clean_df = self.raw_df.dropna(subset=["Age"])

        # Suppress specific privacy budget warnings for cleaner output
        warnings.simplefilter("ignore")

    # =========================================================================
    #  SECTION 1: STATISTICAL ANALYSIS
    # =========================================================================

    def analyze_mean_stability(self, column: str, epsilons: List[float], bounds: Tuple[float, float]):
        """
        Calculates and plots the difference between Real Mean and DP Mean
        across varying privacy budgets (epsilon).
        """
        real_mean = self.clean_df[column].mean()

        # Calculate DP Mean for each epsilon
        dp_means = []
        for eps in epsilons:
            # diffprivlib requires bounds (min, max) to calibrate noise
            res = diffprivlib.tools.mean(self.clean_df[column], epsilon=eps, bounds=bounds)
            dp_means.append(res)

        self._plot_stability_curve(column, epsilons, real_mean, dp_means)

    def compare_histograms(self, column: str, epsilon: float, bins: List[int], bounds: Tuple[float, float]):
        """
        Visualizes the distortion added by Differential Privacy to a histogram.
        """
        # 1. Calculate Original Histogram
        clean_col = self.clean_df[column]
        hist_orig, bin_edges = np.histogram(clean_col, bins=bins)

        # 2. Calculate DP Histogram
        hist_dp, _ = diffprivlib.tools.histogram(
            clean_col, epsilon=epsilon, bins=bins, range=bounds
        )

        self._plot_histogram_comparison(hist_orig, hist_dp, bin_edges, epsilon)

    def calculate_private_sum(self, column: str, epsilon: float) -> float:
        """
        Calculates a differentially private sum using the Laplace Mechanism.
        Automatically detects bounds from the dataset (Note: In real scenarios, bounds should be known a priori).
        """
        # Bounds are required for sensitivity (Sensitivity = max_value - min_value)
        # We assume min is 0 for financial data like 'Fare'
        max_val = self.raw_df[column].max()

        dp_sum = diffprivlib.tools.sum(
            self.raw_df[column],
            epsilon=epsilon,
            bounds=(0, max_val)
        )
        return dp_sum

    # =========================================================================
    #  SECTION 2: MACHINE LEARNING (DP Random Forest)
    # =========================================================================

    def _prepare_ml_data(self, target_col: str) -> Tuple:
        """
        Internal helper to preprocess data: Select features, OneHotEncode, and Split.
        """
        # Define features as per original script
        features = ["Sex", "Age", "SibSp", "Parch", "Fare", "Embarked", "Deck"]

        X = self.clean_df[features].values
        y = self.clean_df[target_col].values

        # Apply Encoding: Columns 0 (Sex), 5 (Embarked), 6 (Deck)
        preprocessor = ColumnTransformer(
            [("OneHot", OneHotEncoder(handle_unknown='ignore'), [0, 5, 6])],
            remainder="passthrough"
        )

        X_encoded = preprocessor.fit_transform(X)
        return train_test_split(X_encoded, y, test_size=0.33, random_state=42)

    def evaluate_ml_tradeoff(self, target_col: str, epsilons: List[float]):
        """
        Trains DP Random Forests at different epsilon levels and compares
        Utility (F1-Score) against a non-private baseline.
        """
        X_train, X_test, y_train, y_test = self._prepare_ml_data(target_col)

        # 1. Baseline (Non-Private) Model
        baseline_rf = RandomForestClassifier(n_estimators=10, random_state=42)
        baseline_rf.fit(X_train, y_train)
        baseline_pred = baseline_rf.predict(X_test)

        # Extract macro avg F1 score
        baseline_f1 = classification_report(y_test, baseline_pred, output_dict=True)['macro avg']['f1-score']

        # 2. DP Models Loop
        dp_scores = []
        print(f"\n--- Training DP Models (Target: {target_col}) ---")

        for eps in epsilons:
            # DP Random Forest
            dp_clf = dp_models.RandomForestClassifier(n_estimators=10, epsilon=eps)
            dp_clf.fit(X_train, y_train)

            dp_pred = dp_clf.predict(X_test)
            score = classification_report(y_test, dp_pred, output_dict=True)['macro avg']['f1-score']
            dp_scores.append(score)
            print(f"  > Epsilon: {eps:<5} | F1-Score: {score:.4f}")

        self._plot_ml_tradeoff(epsilons, baseline_f1, dp_scores)

    # =========================================================================
    #  SECTION 3: VISUALIZATION HELPERS (Private Methods)
    # =========================================================================

    def _plot_stability_curve(self, col, epsilons, real_val, dp_vals):
        plt.figure(figsize=(7, 5))
        plt.plot(epsilons, [real_val] * len(epsilons), '--', color='grey', label='True Mean')
        plt.plot(epsilons, dp_vals, marker='o', color='tab:blue', label='DP Mean')
        plt.xscale('log')
        plt.xlabel('Privacy Budget (Epsilon)')
        plt.ylabel(f'Mean {col}')
        plt.title(f'Statistical Accuracy vs Privacy ({col})')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

    def _plot_histogram_comparison(self, h_orig, h_dp, bins, eps):
        labels = [f"{int(bins[i])}-{int(bins[i + 1])}" for i in range(len(bins) - 1)]
        x = np.arange(len(labels))
        width = 0.35

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(x - width / 2, h_orig, width, label='Original', color='skyblue')
        ax.bar(x + width / 2, h_dp, width, label=f'DP (ε={eps})', color='salmon')

        ax.set_ylabel('Frequency')
        ax.set_title(f'Histogram Distortion (Epsilon = {eps})')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=45)
        ax.legend()
        plt.tight_layout()
        plt.show()

    def _plot_ml_tradeoff(self, epsilons, baseline, scores):
        plt.figure(figsize=(7, 5))
        plt.plot(epsilons, [baseline] * len(epsilons), '--', color='black', label="Standard RF")
        plt.plot(epsilons, scores, marker='o', color='purple', label="Private RF")
        plt.xscale('log')
        plt.xlabel('Epsilon (log scale)')
        plt.ylabel('F1-Score')
        plt.title('Machine Learning Utility vs Privacy')
        plt.ylim(0, 1.0)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()


# =========================================================================
#  SECTION 4: EXECUTION
# =========================================================================

if __name__ == "__main__":
    # Initialize Toolkit
    toolkit = DPKet("data/titanic.csv")

    print("1. Running Statistical Stability Check...")
    # Analyze how the mean of 'Age' changes with epsilon
    toolkit.analyze_mean_stability(
        column="Age",
        epsilons=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
        bounds=(0, 80)
    )

    print("\n2. Comparing Histograms...")
    # Visualize histogram noise
    toolkit.compare_histograms(
        column="Age",
        epsilon=0.1,
        bins=[0, 10, 20, 30, 40, 50, 60, 70, 80],
        bounds=(0, 80)
    )

    print("\n3. Evaluating ML Privacy Trade-off...")
    # Compare Random Forest performance
    toolkit.evaluate_ml_tradeoff(
        target_col="Survived",
        epsilons=[0.01, 0.1, 0.5, 1.0, 5.0, 10.0]
    )

    print("\n4. Calculating Private Sum...")
    real_fare = toolkit.raw_df['Fare'].sum()
    dp_fare = toolkit.calculate_private_sum("Fare", epsilon=1.0)
    print(f"Real Fare Sum: {real_fare:,.2f}")
    print(f"DP Fare Sum:   {dp_fare:,.2f}")