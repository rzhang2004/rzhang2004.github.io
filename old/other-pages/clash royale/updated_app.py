from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import openai
import os
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

app = Flask(__name__)
CORS(app)

# LLM Setup - using environment variables
openai.api_key = os.environ.get("HF_TOKEN")
openai.api_base = "https://router.huggingface.co/v1"

# Clash Royale API key from environment variables
CLASH_ROYALE_API_KEY = os.environ.get("CLASH_ROYALE_API_KEY")

def send_prompt(prompt):
    """Returns only text response to given prompt."""
    try:
        response = openai.ChatCompletion.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B:novita",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating insights: {str(e)}"

def fetch_battle_data(player_tag):
    """Fetch battle data from Clash Royale API using server-side API key"""
    if not CLASH_ROYALE_API_KEY:
        raise Exception("Server configuration error: API key not found")
    
    url = f"https://api.clashroyale.com/v1/players/%23{player_tag}/battlelog"
    headers = {"Authorization": f"Bearer {CLASH_ROYALE_API_KEY}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        if response.status_code == 404:
            raise Exception("Player not found. Please check your player tag.")
        elif response.status_code == 403:
            raise Exception("API access denied. Player profile may be private.")
        else:
            raise Exception(f"API Error: {response.status_code} - Unable to fetch battle data")
    
    return response.json()

def process_battles(battles):
    """Process battle data into DataFrame (adapted from your notebook)"""
    rows = []
    
    # Collect all unique opponent card names for flags
    all_opp_cards = set()
    for battle in battles:
        opp_cards = [c["name"] for c in battle["opponent"][0]["cards"]]
        all_opp_cards.update(opp_cards)
    
    all_opp_cards = list(all_opp_cards)
    
    # Level adjustment per rarity
    level_adjust = {
        "common": 0,
        "rare": 0,
        "epic": 5,
        "legendary": 8,
        "champion": 10
    }
    
    for battle in battles:
        try:
            team = battle["team"][0]
            opp = battle["opponent"][0]
            
            # Extract card info
            my_cards = [{"name": c["name"], "level": c["level"], "rarity": c.get("rarity", "common")} for c in team["cards"]]
            opp_cards = [{"name": c["name"], "level": c.get("level", 1), "rarity": c.get("rarity", "common")} for c in opp["cards"]]
            
            # Pad to 8 cards
            while len(my_cards) < 8:
                my_cards.append({"name": None, "level": None, "rarity": None})
            while len(opp_cards) < 8:
                opp_cards.append({"name": None, "level": None, "rarity": None})
            
            # Count evolutions
            my_evos = sum(1 for c in team["cards"] if c.get("evolutionLevel", 0) > 0)
            opp_evos = sum(1 for c in opp["cards"] if c.get("evolutionLevel", 0) > 0)
            
            # Average elixir cost
            my_elixir_avg = sum(c.get("elixirCost", 4) for c in team["cards"]) / len(team["cards"])
            opp_elixir_avg = sum(c.get("elixirCost", 4) for c in opp["cards"]) / len(opp["cards"])
            
            row = {
                "result": 1 if team["crowns"] > opp["crowns"] else 0,
                "my_trophies": team.get("startingTrophies", 0),
                "my_evolutions": my_evos,
                "my_avg_elixir": my_elixir_avg,
                "opp_trophies": opp.get("startingTrophies", 0),
                "opp_evolutions": opp_evos,
                "opp_avg_elixir": opp_elixir_avg,
                "my_elixirLeaked": team.get("elixirLeaked", 0),
                "opp_elixirLeaked": opp.get("elixirLeaked", 0),
            }
            
            # Initialize rarity counts and adjusted level lists
            my_rarity_counts = {r: 0 for r in level_adjust}
            opp_rarity_counts = {r: 0 for r in level_adjust}
            my_adj_levels = []
            opp_adj_levels = []
            
            # Add card info and calculate adjusted levels
            for i in range(8):
                # My cards
                my_card = my_cards[i]
                row[f"my_card{i+1}_name"] = my_card["name"]
                row[f"my_card{i+1}_level"] = my_card["level"]
                row[f"my_card{i+1}_rarity"] = my_card["rarity"]
                if my_card["rarity"] and my_card["rarity"] in level_adjust:
                    my_rarity_counts[my_card["rarity"]] += 1
                    if my_card["level"]:
                        my_adj_levels.append(my_card["level"] + level_adjust[my_card["rarity"]])
                
                # Opponent cards
                opp_card = opp_cards[i]
                row[f"opp_card{i+1}_name"] = opp_card["name"]
                row[f"opp_card{i+1}_level"] = opp_card["level"]
                row[f"opp_card{i+1}_rarity"] = opp_card["rarity"]
                if opp_card["rarity"] and opp_card["rarity"] in level_adjust:
                    opp_rarity_counts[opp_card["rarity"]] += 1
                    if opp_card["level"]:
                        opp_adj_levels.append(opp_card["level"] + level_adjust[opp_card["rarity"]])
            
            # Add rarity counts
            for r in level_adjust:
                row[f"my_{r}_count"] = my_rarity_counts[r]
                row[f"opp_{r}_count"] = opp_rarity_counts[r]
            
            # Average adjusted levels
            row["my_avg_adj_level"] = sum(my_adj_levels) / len(my_adj_levels) if my_adj_levels else 0
            row["opp_avg_adj_level"] = sum(opp_adj_levels) / len(opp_adj_levels) if opp_adj_levels else 0
            
            # Add flags for all opponent cards
            opp_card_names = [c["name"] for c in opp_cards if c["name"]]
            for card_name in all_opp_cards:
                row[f"opp_has_{card_name.replace(' ', '_').replace('-', '_').replace('.', '_')}"] = int(card_name in opp_card_names)
            
            # Additional features
            row["trophy_gap"] = row["my_trophies"] - row["opp_trophies"]
            row["opp_evo_flag"] = row["opp_evolutions"] > 0
            row["avg_elixir_diff"] = row["my_avg_elixir"] - row["opp_avg_elixir"]
            row["avg_level_diff"] = row["my_avg_adj_level"] - row["opp_avg_adj_level"]
            row["avg_elixir_leak_diff"] = row["my_elixirLeaked"] - row["opp_elixirLeaked"]
            
            rows.append(row)
            
        except Exception as e:
            print(f"Error processing battle: {e}")
            continue
    
    return pd.DataFrame(rows)

def run_logistic_regression(df):
    """Run logistic regression analysis (from your notebook)"""
    if df.empty:
        return []
    
    # Select numeric columns and clean column names
    numeric_cols = df.select_dtypes(include='number').columns
    numeric_df = df[numeric_cols].copy()
    numeric_df.columns = numeric_df.columns.str.replace(r'[^0-9a-zA-Z_]', '_', regex=True)
    
    # Handle missing values
    numeric_df = numeric_df.fillna(0)
    
    target = 'result'
    if target not in numeric_df.columns:
        return []
    
    predictors = [col for col in numeric_df.columns if col != target]
    
    try:
        X = numeric_df[predictors]
        y = numeric_df[target]
        
        # Remove columns with zero variance
        X = X.loc[:, X.var() != 0]
        
        if X.empty or len(X.columns) == 0:
            return []
        
        model = LogisticRegression(penalty='l2', solver='liblinear', max_iter=1000)
        model.fit(X, y)
        
        coefs = np.hstack([model.intercept_, model.coef_.flatten()])
        variables = ['Intercept'] + list(X.columns)
        odds_ratios = np.exp(coefs)
        
        results = pd.DataFrame({
            'Variable': variables,
            'Coefficient': coefs,
            'Odds_Ratio': odds_ratios
        })
        
        # Sort by odds ratio and get strongest negative effects
        results_sorted = results.sort_values(by='Odds_Ratio', ascending=True).reset_index(drop=True)
        return results_sorted.head(10).to_dict(orient='records')
        
    except Exception as e:
        print(f"Error in logistic regression: {e}")
        return []

def generate_insights_with_llm(strong_features, battle_stats):
    """Generate insights using LLM (from your notebook)"""
    
    prompt = f"""
I have a list of Clash Royale predictors with their logistic regression coefficients and odds ratios that indicate the impact on winning a match. 
The target variable `result = 1` means that I win the match.

Battle Statistics:
- Total battles analyzed: {battle_stats['total_battles']}
- Win rate: {battle_stats['win_rate']:.1f}%
- Average trophy difference: {battle_stats['avg_trophy_diff']:.0f}

Instructions for the LLM (technical and specific):

- Only consider features that **negatively affect the probability of winning**.  
    - For opponent features ('opp_'): select features with **odds ratio (OR) < 1**, indicating that the presence or higher value of this feature decreases the probability that `result = 1`.  
    - For my features ('my_'): select features with **odds ratio (OR) < 1**, indicating that the presence or higher value of this feature decreases the probability that `result = 1`.  
- Use **logistic regression coefficients and OR values** to prioritize the magnitude of effect. Features with the largest absolute deviation of OR from 1 should be considered the most impactful.  
- The output must be actionable insights for gameplay and deck adjustments. **Do not include any statistical terms, formulas, or dataset variable names.** Use conventional card names instead.

Here is the data:

{strong_features}

Using the above, generate insights that include:

1. **Most threatening opponent cards or features** – suggest counters or strategies.  
2. **Strategic recommendations for deck adjustments, card play, and elixir management** to mitigate these threats.

Present the insights in **clear, concise bullet points**, prioritized by their negative impact on winning (largest effect first).
"""
    
    return send_prompt(prompt)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        player_tag = data.get('player_tag', '').strip()
        
        if not player_tag:
            return jsonify({'error': 'Player tag is required'}), 400
        
        # Remove # if user included it
        player_tag = player_tag.replace('#', '')
        
        # Fetch battle data using server-side API key
        battles = fetch_battle_data(player_tag)
        
        # Process battles into DataFrame
        df_battles = process_battles(battles)
        
        if df_battles.empty:
            return jsonify({'error': 'No battle data could be processed'}), 400
        
        # Calculate battle statistics
        total_battles = len(df_battles)
        wins = df_battles['result'].sum()
        win_rate = (wins / total_battles) * 100
        avg_trophy_diff = df_battles['trophy_gap'].mean() if 'trophy_gap' in df_battles.columns else 0
        
        battle_stats = {
            'total_battles': total_battles,
            'wins': wins,
            'losses': total_battles - wins,
            'win_rate': win_rate,
            'avg_trophy_diff': avg_trophy_diff
        }
        
        # Run logistic regression
        strong_features = run_logistic_regression(df_battles)
        
        # Generate insights with LLM
        insights = ""
        if strong_features:
            insights = generate_insights_with_llm(strong_features, battle_stats)
        else:
            insights = "Unable to generate detailed insights due to insufficient data variance. Try analyzing more battles."
        
        return jsonify({
            'success': True,
            'battle_stats': battle_stats,
            'insights': insights,
            'features_analyzed': len(strong_features)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint for deployment platforms"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)