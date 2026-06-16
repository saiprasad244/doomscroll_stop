import os
import sys
# Add project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import csv
import math
import random
import json

# ==========================================
# 1. DATA PREPROCESSING HELPERS
# ==========================================

def load_csv(filepath):
    features = []
    labels = []
    with open(filepath, mode='r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row:
                continue
            feat = [float(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4])]
            features.append(feat)
            labels.append(row[5])
    return features, labels, header[:-1]

def train_test_split(X, y, test_size=0.2, seed=42):
    random.seed(seed)
    combined = list(zip(X, y))
    random.shuffle(combined)
    
    split_idx = int(len(combined) * (1 - test_size))
    train_data = combined[:split_idx]
    test_data = combined[split_idx:]
    
    X_train, y_train = zip(*train_data)
    X_test, y_test = zip(*test_data)
    
    return list(X_train), list(X_test), list(y_train), list(y_test)

class StandardScaler:
    def __init__(self):
        self.means = []
        self.stds = []
        
    def fit(self, X):
        n_samples = len(X)
        n_features = len(X[0])
        self.means = [0.0] * n_features
        self.stds = [0.0] * n_features
        
        for sample in X:
            for j in range(n_features):
                self.means[j] += sample[j]
        self.means = [m / n_samples for m in self.means]
        
        for sample in X:
            for j in range(n_features):
                self.stds[j] += (sample[j] - self.means[j]) ** 2
        self.stds = [math.sqrt(s / n_samples) for s in self.stds]
        self.stds = [s if s > 0 else 1.0 for s in self.stds]
        return self
        
    def transform(self, X):
        X_trans = []
        for sample in X:
            scaled = []
            for j in range(len(sample)):
                scaled.append((sample[j] - self.means[j]) / self.stds[j])
            X_trans.append(scaled)
        return X_trans

class LabelEncoder:
    def __init__(self):
        self.classes_ = ["Healthy", "Risky", "Severe"]
        self.class_to_idx = {c: i for i, c in enumerate(self.classes_)}
        self.idx_to_class = {i: c for i, c in enumerate(self.classes_)}
        
    def transform(self, y):
        return [self.class_to_idx[val] for val in y]

# ==========================================
# 2. LOGISTIC REGRESSION (One-vs-Rest)
# ==========================================

class BinaryLogisticRegression:
    def __init__(self, lr=0.1, epochs=200):
        self.lr = lr
        self.epochs = epochs
        self.weights = None
        self.bias = 0.0
        
    def sigmoid(self, z):
        z = max(-500.0, min(500.0, z))
        return 1.0 / (1.0 + math.exp(-z))
        
    def fit(self, X, y):
        n_samples = len(X)
        n_features = len(X[0])
        self.weights = [0.0] * n_features
        self.bias = 0.0
        
        for _ in range(self.epochs):
            dw = [0.0] * n_features
            db = 0.0
            for i in range(n_samples):
                linear = sum(X[i][j] * self.weights[j] for j in range(n_features)) + self.bias
                y_pred = self.sigmoid(linear)
                error = y_pred - y[i]
                
                for j in range(n_features):
                    dw[j] += error * X[i][j]
                db += error
                
            for j in range(n_features):
                self.weights[j] -= (self.lr * dw[j]) / n_samples
            self.bias -= (self.lr * db) / n_samples

class MulticlassLogisticRegression:
    def __init__(self, lr=0.1, epochs=200):
        self.lr = lr
        self.epochs = epochs
        self.classifiers = []
        self.n_classes = 3
        
    def fit(self, X, y):
        self.classifiers = []
        for c in range(self.n_classes):
            y_bin = [1 if val == c else 0 for val in y]
            clf = BinaryLogisticRegression(lr=self.lr, epochs=self.epochs)
            clf.fit(X, y_bin)
            self.classifiers.append(clf)
            
    def predict_proba(self, X):
        probas = []
        for sample in X:
            probs = []
            for clf in self.classifiers:
                linear = sum(sample[j] * clf.weights[j] for j in range(len(sample))) + clf.bias
                linear = max(-500.0, min(500.0, linear))
                probs.append(1.0 / (1.0 + math.exp(-linear)))
            sum_probs = sum(probs)
            if sum_probs > 0:
                probs = [p / sum_probs for p in probs]
            else:
                probs = [1.0 / self.n_classes] * self.n_classes
            probas.append(probs)
        return probas
        
    def predict(self, X):
        probas = self.predict_proba(X)
        return [p.index(max(p)) for p in probas]

# ==========================================
# 3. DECISION TREE & RANDOM FOREST
# ==========================================

class Node:
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, value=None, probas=None):
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value
        self.probas = probas

    def is_leaf(self):
        return self.value is not None

class RegressionTree:
    def __init__(self, max_depth=3, min_samples_split=5):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None
        
    def fit(self, X, y):
        self.root = self._build_tree(X, y, depth=0)
        return self
        
    def _variance(self, y_values):
        if not y_values:
            return 0.0
        mean = sum(y_values) / len(y_values)
        return sum((val - mean) ** 2 for val in y_values) / len(y_values)
        
    def _split_data(self, X, y, idx, threshold):
        left_X, left_y, right_X, right_y = [], [], [], []
        for sample, val in zip(X, y):
            if sample[idx] <= threshold:
                left_X.append(sample)
                left_y.append(val)
            else:
                right_X.append(sample)
                right_y.append(val)
        return left_X, left_y, right_X, right_y

    def _build_tree(self, X, y, depth):
        n_samples = len(X)
        if n_samples == 0:
            return Node(value=0.0)
            
        mean_val = sum(y) / n_samples
        if depth >= self.max_depth or n_samples < self.min_samples_split or self._variance(y) < 1e-7:
            return Node(value=mean_val)
            
        n_features = len(X[0])
        best_var_reduction = -1.0
        best_split = None
        current_variance = self._variance(y)
        
        for idx in range(n_features):
            vals = [sample[idx] for sample in X]
            if not vals:
                continue
            min_val, max_val = min(vals), max(vals)
            if min_val == max_val:
                continue
            step = (max_val - min_val) / 11
            thresholds = [min_val + step * k for k in range(1, 11)]
            
            for threshold in thresholds:
                left_X, left_y, right_X, right_y = self._split_data(X, y, idx, threshold)
                if len(left_y) == 0 or len(right_y) == 0:
                    continue
                w_left = len(left_y) / n_samples
                w_right = len(right_y) / n_samples
                var_reduction = current_variance - (w_left * self._variance(left_y) + w_right * self._variance(right_y))
                
                if var_reduction > best_var_reduction:
                    best_var_reduction = var_reduction
                    best_split = (idx, threshold, left_X, left_y, right_X, right_y)
                    
        if best_split is None or best_var_reduction <= 0:
            return Node(value=mean_val)
            
        idx, threshold, left_X, left_y, right_X, right_y = best_split
        left_child = self._build_tree(left_X, left_y, depth + 1)
        right_child = self._build_tree(right_X, right_y, depth + 1)
        return Node(feature_idx=idx, threshold=threshold, left=left_child, right=right_child)
        
    def _predict_sample(self, node, x):
        if node.is_leaf():
            return node.value
        if x[node.feature_idx] <= node.threshold:
            return self._predict_sample(node.left, x)
        return self._predict_sample(node.right, x)
        
    def predict(self, X):
        return [self._predict_sample(self.root, x) for x in X]

class DecisionTree:
    def __init__(self, max_depth=5, min_samples_split=5):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root = None
        
    def _gini(self, groups, classes):
        n_instances = float(sum([len(group) for group in groups]))
        gini = 0.0
        for group in groups:
            size = float(len(group))
            if size == 0:
                continue
            score = 0.0
            counts = {c: 0 for c in classes}
            for sample in group:
                label = sample[-1]
                counts[label] = counts.get(label, 0) + 1
            for c in classes:
                p = counts[c] / size
                score += p * p
            gini += (1.0 - score) * (size / n_instances)
        return gini

    def _split_data(self, X, y, idx, threshold):
        left_X, left_y, right_X, right_y = [], [], [], []
        for sample, val in zip(X, y):
            if sample[idx] <= threshold:
                left_X.append(sample)
                left_y.append(val)
            else:
                right_X.append(sample)
                right_y.append(val)
        return left_X, left_y, right_X, right_y

    def _build_tree(self, X, y, depth=0):
        n_samples = len(X)
        if n_samples == 0:
            return Node(value=0, probas=[1.0, 0.0, 0.0])
            
        classes = list(set(y))
        counts = {0: 0, 1: 0, 2: 0}
        for val in y:
            counts[val] = counts.get(val, 0) + 1
        majority_class = max(counts, key=counts.get)
        probas = [counts.get(i, 0) / n_samples for i in range(3)]
        
        if depth >= self.max_depth or n_samples < self.min_samples_split or len(classes) == 1:
            return Node(value=majority_class, probas=probas)
            
        n_features = len(X[0])
        best_gini = 999.0
        best_split = None
        
        for idx in range(n_features):
            vals = [sample[idx] for sample in X]
            if not vals:
                continue
            min_val, max_val = min(vals), max(vals)
            if min_val == max_val:
                continue
            step = (max_val - min_val) / 11
            thresholds = [min_val + step * k for k in range(1, 11)]
            
            for threshold in thresholds:
                left_X, left_y, right_X, right_y = self._split_data(X, y, idx, threshold)
                if not left_y or not right_y:
                    continue
                left_group = [x + [val] for x, val in zip(left_X, left_y)]
                right_group = [x + [val] for x, val in zip(right_X, right_y)]
                gini_val = self._gini([left_group, right_group], [0, 1, 2])
                
                if gini_val < best_gini:
                    best_gini = gini_val
                    best_split = (idx, threshold, left_X, left_y, right_X, right_y)
                    
        if best_split is None:
            return Node(value=majority_class, probas=probas)
            
        idx, threshold, left_X, left_y, right_X, right_y = best_split
        left_child = self._build_tree(left_X, left_y, depth + 1)
        right_child = self._build_tree(right_X, right_y, depth + 1)
        return Node(feature_idx=idx, threshold=threshold, left=left_child, right=right_child, probas=probas)

    def fit(self, X, y):
        self.root = self._build_tree(X, y)
        return self

    def _predict_sample_probas(self, node, x):
        if node.is_leaf():
            return node.probas
        if x[node.feature_idx] <= node.threshold:
            return self._predict_sample_probas(node.left, x)
        return self._predict_sample_probas(node.right, x)

    def predict_proba(self, X):
        return [self._predict_sample_probas(self.root, x) for x in X]

    def predict(self, X):
        probas = self.predict_proba(X)
        return [p.index(max(p)) for p in probas]

class RandomForest:
    def __init__(self, n_estimators=10, max_depth=5, min_samples_split=5):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.trees = []
        
    def fit(self, X, y):
        self.trees = []
        n_samples = len(X)
        for _ in range(self.n_estimators):
            boot_indices = [random.randint(0, n_samples - 1) for _ in range(n_samples)]
            boot_X = [X[i] for i in boot_indices]
            boot_y = [y[i] for i in boot_indices]
            
            tree = DecisionTree(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
            tree.fit(boot_X, boot_y)
            self.trees.append(tree)
        return self
        
    def predict_proba(self, X):
        forest_probas = []
        for x in X:
            probs = [0.0, 0.0, 0.0]
            for tree in self.trees:
                tree_prob = tree._predict_sample_probas(tree.root, x)
                for c in range(3):
                    probs[c] += tree_prob[c]
            probs = [p / self.n_estimators for p in probs]
            forest_probas.append(probs)
        return forest_probas
        
    def predict(self, X):
        probas = self.predict_proba(X)
        return [p.index(max(p)) for p in probas]

# ==========================================
# 4. MULTICLASS GRADIENT BOOSTING (XGBoost Analogue)
# ==========================================

class XGBoostAnalogue:
    def __init__(self, n_estimators=10, lr=0.1, max_depth=3, min_samples_split=5):
        self.n_estimators = n_estimators
        self.lr = lr
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.n_classes = 3
        self.trees = []
        
    def fit(self, X, y):
        n_samples = len(X)
        raw_predictions = [[0.0] * self.n_classes for _ in range(n_samples)]
        self.trees = []
        
        for t in range(self.n_estimators):
            round_trees = []
            
            probs = []
            for i in range(n_samples):
                scores = raw_predictions[i]
                max_score = max(scores)
                exps = [math.exp(s - max_score) for s in scores]
                sum_exps = sum(exps)
                probs.append([e / sum_exps for e in exps])
                
            for c in range(self.n_classes):
                residuals = []
                for i in range(n_samples):
                    y_true = 1.0 if y[i] == c else 0.0
                    residuals.append(y_true - probs[i][c])
                    
                tree = RegressionTree(max_depth=self.max_depth, min_samples_split=self.min_samples_split)
                tree.fit(X, residuals)
                round_trees.append(tree)
                
                predictions = tree.predict(X)
                for i in range(n_samples):
                    raw_predictions[i][c] += self.lr * predictions[i]
                    
            self.trees.append(round_trees)
        return self
        
    def predict_raw(self, X):
        n_samples = len(X)
        raw_predictions = [[0.0] * self.n_classes for _ in range(n_samples)]
        for round_trees in self.trees:
            for c in range(self.n_classes):
                tree = round_trees[c]
                predictions = tree.predict(X)
                for i in range(n_samples):
                    raw_predictions[i][c] += self.lr * predictions[i]
        return raw_predictions
        
    def predict_proba(self, X):
        raw_preds = self.predict_raw(X)
        probas = []
        for i in range(len(X)):
            scores = raw_preds[i]
            max_score = max(scores)
            exps = [math.exp(s - max_score) for s in scores]
            sum_exps = sum(exps)
            probas.append([e / sum_exps for e in exps])
        return probas
        
    def predict(self, X):
        probas = self.predict_proba(X)
        return [p.index(max(p)) for p in probas]

# ==========================================
# 5. METRICS EVALUATION
# ==========================================

def calculate_metrics(y_true, y_pred):
    n_classes = 3
    cm = [[0] * n_classes for _ in range(n_classes)]
    for t, p in zip(y_true, y_pred):
        cm[t][p] += 1
        
    correct = sum(cm[i][i] for i in range(n_classes))
    accuracy = correct / len(y_true) if len(y_true) > 0 else 0
    
    precision_list = []
    recall_list = []
    f1_list = []
    
    for c in range(n_classes):
        tp = cm[c][c]
        fp = sum(cm[i][c] for i in range(n_classes)) - tp
        fn = sum(cm[c][j] for j in range(n_classes)) - tp
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        precision_list.append(precision)
        recall_list.append(recall)
        f1_list.append(f1)
        
    macro_precision = sum(precision_list) / n_classes
    macro_recall = sum(recall_list) / n_classes
    macro_f1 = sum(f1_list) / n_classes
    
    return {
        'accuracy': round(accuracy, 4),
        'precision': round(macro_precision, 4),
        'recall': round(macro_recall, 4),
        'f1': round(macro_f1, 4),
        'confusion_matrix': cm
    }

# ==========================================
# 6. SERIALIZATION DIRECTIVES (PORTABLE JSON)
# ==========================================

def serialize_node(node):
    if node is None:
        return None
    if node.is_leaf():
        return {
            'is_leaf': True,
            'value': node.value,
            'probas': node.probas
        }
    return {
        'is_leaf': False,
        'feature_idx': node.feature_idx,
        'threshold': node.threshold,
        'left': serialize_node(node.left),
        'right': serialize_node(node.right)
    }

def serialize_lr(model):
    return {
        'classifiers': [{
            'weights': clf.weights,
            'bias': clf.bias
        } for clf in model.classifiers]
    }

def serialize_rf(model):
    return {
        'trees': [serialize_node(tree.root) for tree in model.trees]
    }

def serialize_xgb(model):
    return {
        'lr': model.lr,
        'trees': [[serialize_node(tree.root) for tree in round_trees] for round_trees in model.trees]
    }

# ==========================================
# 7. PIPELINE RUNNER
# ==========================================

def run_ml_pipeline():
    dataset_path = 'dataset/doomscroll_dataset.csv'
    if not os.path.exists(dataset_path):
        print("Dataset not found. Generating...")
        from dataset.generate_data import generate_synthetic_dataset
        generate_synthetic_dataset(dataset_path)
        
    X, y, feature_names = load_csv(dataset_path)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, seed=42)
    
    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    encoder = LabelEncoder()
    y_train_encoded = encoder.transform(y_train)
    y_test_encoded = encoder.transform(y_test)
    
    print("Training Logistic Regression...")
    lr_model = MulticlassLogisticRegression(lr=0.5, epochs=300)
    lr_model.fit(X_train_scaled, y_train_encoded)
    lr_preds = lr_model.predict(X_test_scaled)
    lr_metrics = calculate_metrics(y_test_encoded, lr_preds)
    print("Logistic Regression Metrics:", lr_metrics)
    
    print("\nTraining Random Forest...")
    rf_model = RandomForest(n_estimators=15, max_depth=6)
    rf_model.fit(X_train_scaled, y_train_encoded)
    rf_preds = rf_model.predict(X_test_scaled)
    rf_metrics = calculate_metrics(y_test_encoded, rf_preds)
    print("Random Forest Metrics:", rf_metrics)
    
    print("\nTraining XGBoost Analogue...")
    xgb_model = XGBoostAnalogue(n_estimators=15, lr=0.2, max_depth=4)
    xgb_model.fit(X_train_scaled, y_train_encoded)
    xgb_preds = xgb_model.predict(X_test_scaled)
    xgb_metrics = calculate_metrics(y_test_encoded, xgb_preds)
    print("XGBoost Analogue Metrics:", xgb_metrics)
    
    comparison = {
        'Logistic Regression': lr_metrics,
        'Random Forest': rf_metrics,
        'XGBoost': xgb_metrics
    }
    
    os.makedirs('saved_models', exist_ok=True)
    with open('saved_models/model_comparison.json', 'w') as f:
        json.dump(comparison, f, indent=4)
        
    models_eval = {
        'Logistic Regression': (lr_model, serialize_lr, lr_metrics['f1']),
        'Random Forest': (rf_model, serialize_rf, rf_metrics['f1']),
        'XGBoost': (xgb_model, serialize_xgb, xgb_metrics['f1'])
    }
    
    best_model_name = max(models_eval, key=lambda k: models_eval[k][2])
    best_model, serializer_func, best_f1 = models_eval[best_model_name]
    
    print(f"\nBest Model: {best_model_name} with F1-Score {best_f1}")
    
    model_data = {
        'model_name': best_model_name,
        'model_params': serializer_func(best_model),
        'scaler': {
            'means': scaler.means,
            'stds': scaler.stds
        },
        'encoder': {
            'classes': encoder.classes_
        },
        'feature_names': feature_names
    }
    
    with open('saved_models/best_model.json', 'w') as f:
        json.dump(model_data, f, indent=4)
        
    print(f"Saved best model bundle to saved_models/best_model.json")

if __name__ == '__main__':
    run_ml_pipeline()
