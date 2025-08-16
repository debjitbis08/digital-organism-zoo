# 🤖 OpenAI Integration Setup

## 🚀 Quick Start with OpenAI

The Digital Organism Zoo now supports OpenAI API for intelligent parent teaching! This is perfect for your ThinkPad T480.

### **Step 1: Get OpenAI API Key**

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-...`)

### **Step 2: Set Environment Variable**

**Option A: Export (temporary)**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Option B: .env file (permanent)**
```bash
echo "OPENAI_API_KEY=sk-your-key-here" >> ~/.bashrc
source ~/.bashrc
```

### **Step 3: Run with OpenAI**

```bash
# With environment variable set
python run_indefinite_zoo.py

# Or pass key directly
python run_indefinite_zoo.py --openai-key="sk-your-key-here"

# Use different model
python run_indefinite_zoo.py --model="gpt-4o-mini"
```

## 🎛️ **Model Options**

### **Recommended for ThinkPad T480:**
- **`gpt-3.5-turbo`** (default) - Fast, cheap, good quality
- **`gpt-4o-mini`** - Better quality, still affordable

### **Cost Comparison (per 1M tokens):**
- **gpt-3.5-turbo**: $0.50 input / $1.50 output
- **gpt-4o-mini**: $0.15 input / $0.60 output  
- **gpt-4o**: $2.50 input / $10.00 output

## 💰 **Cost Estimation**

For typical Digital Organism Zoo usage:
- **Per hour**: ~$0.01-0.05 (very light usage)
- **Per day**: ~$0.25-1.00 
- **Per month**: ~$5-30 depending on activity

The system is designed to be cost-efficient with:
- Short prompts (organism context)
- Brief responses (under 100 chars)
- Smart fallback to cached responses
- Rate limiting and error handling

## 🧠 **What You Get with OpenAI**

### **Intelligent Teaching**
Instead of: "The wise seek patterns in chaos..."
You get: "Try searching data streams when energy drops below 30. Focus on XML feeds first."

### **Contextual Responses**
- **Young organism**: "You're learning so well! Keep trying different food sources."
- **Struggling organism**: "Your energy efficiency is low - maybe try smaller, more frequent meals?"
- **Advanced organism**: "You've mastered survival. Time to focus on helping others reproduce."

### **Dynamic Personalities**
Each parent gets a unique personality (Wise Mentor, Strict Professor, etc.) that influences all OpenAI responses.

## ⚡ **Usage Examples**

### **Start with OpenAI**
```bash
# Set your key
export OPENAI_API_KEY="sk-your-actual-key-here"

# Run the zoo
python run_indefinite_zoo.py
```

You'll see:
```
🌍 Digital Organism Zoo - Indefinite Evolution Mode
==================================================
🧠 LLM Model: gpt-3.5-turbo
🔑 API Key: Set
💾 State persistence: Continue from save
🛑 Press Ctrl+C to stop gracefully
==================================================
🧠 OpenAI LLM Teacher connected: gpt-3.5-turbo
```

### **Fallback Mode (no API key)**
```bash
python run_indefinite_zoo.py --no-llm
```

You'll see:
```
⚠️  OPENAI_API_KEY not set. Using fallback responses.
🧠 Teaching: Enhanced fallback responses active
```

## 🔧 **Troubleshooting**

### **API Key Issues**
```
⚠️  Invalid OpenAI API key. Using fallback responses.
```
- Check your API key is correct
- Ensure you have billing set up in OpenAI account
- Verify the key has sufficient credits

### **Rate Limiting**
```
⚠️  Rate limited, waiting before retry...
```
- Normal behavior - system will retry automatically
- Fallback responses used during rate limits

### **Network Issues**
```
⚠️  OpenAI API not available (Connection timeout). Using fallback responses.
```
- Check internet connection
- System continues with fallback responses

## 🎮 **Expected Behavior**

### **With OpenAI**
```
🧠 OpenAI-enhanced advice (socratic): "What happens when you focus on one food type?"
🔧 Parent modifies organism code: "Let me adjust your metabolism for better efficiency."
```

### **Without OpenAI (Fallback)**
```
🧠 Teaching: Enhanced fallback responses active
🔧 Parent modifies organism code: "Your body needs improvement, child..."
```

## 🏆 **Best Practices**

1. **Start with `gpt-3.5-turbo`** - good balance of cost/quality
2. **Monitor usage** at [OpenAI Usage](https://platform.openai.com/usage)
3. **Set billing limits** to avoid surprises
4. **Use `--no-llm`** for testing without API costs
5. **Let it run overnight** - the conversations get really interesting!

---

**Ready to give your digital organisms AI-powered parenting?**

```bash
export OPENAI_API_KEY="sk-your-key-here"
python run_indefinite_zoo.py
```