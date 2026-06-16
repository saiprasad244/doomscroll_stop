import os
import json
import math

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'saved_models', 'best_model.json')
_model_bundle = None

def load_model():
    global _model_bundle
    if _model_bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model JSON file not found at {MODEL_PATH}. Run pipeline training first.")
        with open(MODEL_PATH, 'r') as f:
            _model_bundle = json.load(f)
    return _model_bundle

def evaluate_tree(node, sample):
    if node is None:
        return 0.0
    if node.get('is_leaf', False):
        if node.get('probas') is not None:
            return node['probas']
        return node.get('value', 0.0)
        
    feat_idx = node['feature_idx']
    threshold = node['threshold']
    
    if sample[feat_idx] <= threshold:
        return evaluate_tree(node['left'], sample)
    else:
        return evaluate_tree(node['right'], sample)

def predict_probabilities_json(model_name, params, sample):
    """
    Evaluates probabilities for the given sample based on model parameters from JSON.
    """
    if model_name == 'Logistic Regression':
        classifiers = params['classifiers']
        probs = []
        for clf in classifiers:
            linear = sum(sample[j] * clf['weights'][j] for j in range(len(sample))) + clf['bias']
            linear = max(-500.0, min(500.0, linear))
            probs.append(1.0 / (1.0 + math.exp(-linear)))
        sum_probs = sum(probs)
        if sum_probs > 0:
            return [p / sum_probs for p in probs]
        return [1.0 / 3] * 3
        
    elif model_name == 'Random Forest':
        trees = params['trees']
        avg_probs = [0.0, 0.0, 0.0]
        for tree_root in trees:
            tree_probs = evaluate_tree(tree_root, sample)
            for c in range(3):
                avg_probs[c] += tree_probs[c]
        return [p / len(trees) for p in avg_probs]
        
    elif model_name == 'XGBoost':
        trees = params['trees']
        lr = params['lr']
        n_classes = 3
        raw_scores = [0.0] * n_classes
        
        # Sequentially evaluate regression trees
        for round_trees in trees:
            for c in range(n_classes):
                val = evaluate_tree(round_trees[c], sample)
                # Ensure val is a single float value (regression leaf output)
                if isinstance(val, list):
                    # Fallback if a classification node was somehow serialized
                    val = sum(val) / len(val)
                raw_scores[c] += lr * val
                
        # Softmax
        max_score = max(raw_scores)
        exps = [math.exp(s - max_score) for s in raw_scores]
        sum_exps = sum(exps)
        return [e / sum_exps for e in exps]
        
    else:
        raise ValueError(f"Unknown model name: {model_name}")

def predict_doomscroll(session_duration, scroll_count, app_opens, night_usage, screen_time):
    bundle = load_model()
    model_name = bundle['model_name']
    params = bundle['model_params']
    scaler = bundle['scaler']
    encoder = bundle['encoder']
    
    # Preprocess feature vector
    raw_sample = [float(session_duration), float(scroll_count), float(app_opens), float(night_usage), float(screen_time)]
    
    # Scale sample features manually
    scaled_sample = []
    for j in range(len(raw_sample)):
        mean = scaler['means'][j]
        std = scaler['stds'][j]
        scaled_sample.append((raw_sample[j] - mean) / std)
        
    # Get probabilities
    probas = predict_probabilities_json(model_name, params, scaled_sample)
    
    prob_healthy = probas[0]
    prob_risky = probas[1]
    prob_severe = probas[2]
    
    # Predict category
    pred_idx = probas.index(max(probas))
    category = encoder['classes'][pred_idx]
    
    # Scaled visual Risk Score
    if pred_idx == 2: # Severe
        risk_score = round(70.0 + (prob_severe * 30.0))
    elif pred_idx == 1: # Risky
        risk_score = round(30.0 + (prob_risky * 39.0))
    else: # Healthy
        risk_score = round(prob_risky * 20.0 + prob_severe * 9.0)
        
    risk_score = max(0, min(100, risk_score))
    
    return {
        'category': category,
        'risk_score': risk_score,
        'probabilities': {
            'Healthy': round(prob_healthy, 4),
            'Risky': round(prob_risky, 4),
            'Severe': round(prob_severe, 4)
        },
        'model_used': model_name
    }
